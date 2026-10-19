#!/usr/bin/env python3
"""Owned-window X11 input check. Synthetic OS keys, not physical-device evidence."""
import argparse
import ctypes
import json
import os
import re
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def request_close(window):
    # The same WM_DELETE_WINDOW protocol used by a window-manager close button.
    # This is a graceful request to the verified owned window, not process killing.
    x = ctypes.CDLL('libX11.so.6')
    x.XOpenDisplay.restype = ctypes.c_void_p
    display = x.XOpenDisplay(None)
    if not display:
        raise RuntimeError('X11 display unavailable.')
    x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    x.XInternAtom.restype = ctypes.c_ulong
    class Data(ctypes.Union):
        _fields_ = [('l', ctypes.c_long * 5)]
    class Client(ctypes.Structure):
        _fields_ = [('type', ctypes.c_int), ('serial', ctypes.c_ulong),
                    ('send_event', ctypes.c_int), ('display', ctypes.c_void_p),
                    ('window', ctypes.c_ulong), ('message_type', ctypes.c_ulong),
                    ('format', ctypes.c_int), ('data', Data)]
    class Event(ctypes.Union):
        _fields_ = [('client', Client), ('padding', ctypes.c_long * 24)]
    event = Event()
    event.client.type = 33
    event.client.send_event = 1
    event.client.display = display
    event.client.window = window
    event.client.message_type = x.XInternAtom(display, b'WM_PROTOCOLS', 0)
    event.client.format = 32
    event.client.data.l[0] = x.XInternAtom(display, b'WM_DELETE_WINDOW', 0)
    x.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_long, ctypes.POINTER(Event)]
    x.XSendEvent(display, window, 0, 0, ctypes.byref(event))
    x.XFlush.argtypes = [ctypes.c_void_p]
    x.XFlush(display)
    x.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x.XCloseDisplay(display)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--executable', type=Path, required=True)
    p.add_argument('--editor', action='store_true')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out = a.out.resolve()
    a.out.mkdir(parents=True, exist_ok=False)
    slot = 'AnanseMenu_' + time.strftime('%Y%m%dT%H%M%S')
    command = [str(a.executable.resolve())]
    if a.editor:
        command += [str(ROOT / 'Unreal/Ananse.uproject'), '-game']
    command += ['-AnanseEpisode', '-AnanseCheckpointSlot=' + slot, '-ansimalloc',
                '-windowed', '-ResX=1280', '-ResY=720', '-abslog=' + str(a.out / 'session.log')]
    env = dict(os.environ)
    for key in ('PYTHONPATH', 'LD_LIBRARY_PATH'):
        env.pop(key, None)
    report = {'command': command, 'slot': slot, 'input': 'synthetic X11 keys to verified owned window',
              'forced_termination': False, 'checks': [], 'status': 'running'}
    def xd(*args):
        return subprocess.check_output(['xdotool', *map(str, args)], text=True).strip()
    with (a.out / 'process.log').open('x') as log:
        proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        report['pid'] = proc.pid
        (a.out / 'launch.json').write_text(json.dumps(report, indent=2) + '\n')
        window = None
        try:
            for _ in range(120):
                if proc.poll() is not None:
                    raise RuntimeError('Game exited before its window appeared.')
                try:
                    ids = xd('search', '--onlyvisible', '--pid', proc.pid).splitlines()
                    for candidate in ids:
                        if xd('getwindowpid', candidate) == str(proc.pid) and 'ANANSE' in xd('getwindowname', candidate).upper():
                            window = int(candidate)
                            break
                except subprocess.CalledProcessError:
                    pass
                if window:
                    break
                time.sleep(.5)
            if not window:
                raise RuntimeError('No uniquely owned ANANSE window found.')
            report['window'] = window
            def key(name):
                if xd('getwindowpid', window) != str(proc.pid):
                    raise RuntimeError('Window ownership changed.')
                xd('key', '--window', window, '--clearmodifiers', name)
                time.sleep(.5)
            def capture(name):
                raw = a.out / (name + '.xwd')
                subprocess.run(['xwd', '-silent', '-id', str(window), '-out', str(raw)], check=True)
                subprocess.run(['convert', str(raw), str(a.out / (name + '.png'))], check=True)
            time.sleep(8)
            capture('initial-menu')
            key('n')
            time.sleep(9)
            key('p')
            capture('paused-opening')
            key('equal');key('equal')
            capture('subtitle-settings')
            key('minus');key('minus')
            key('Escape')
            time.sleep(2)
            key('Escape')
            time.sleep(2)
            key('F5')
            key('p')
            capture('paused-play')
            key('c')
            time.sleep(8)
            capture('continued-game')
            text = (a.out / 'session.log').read_text(errors='replace')
            expected = ['ANANSE episode menu=1 paused=1', 'ANANSE episode menu=0 paused=0',
                        'ANANSE subtitle scale=', 'AnanseContinueSlot=' + slot]
            for item in expected:
                if item not in text:
                    raise RuntimeError('Missing native UI evidence: ' + item)
                report['checks'].append(item)
            times = [float(value) for value in re.findall(r'ANANSE paused presentation time=([0-9.]+)', text)]
            if len(times) < 2 or abs(times[0] - times[1]) > .01:
                raise RuntimeError('Opening playback did not remain frozen through pause/settings/resume.')
            report['paused_sequence_seconds'] = times[:2]
            request_close(window)
            rc = proc.wait(timeout=40)
            report['exit_status'] = rc
            if rc != 0:
                raise RuntimeError('Owned game did not exit normally.')
            report['status'] = 'passed'
        except Exception as exc:
            report['status'] = 'failed'
            report['error'] = str(exc)
            if proc.poll() is None and window:
                request_close(window)
                try:
                    report['exit_status'] = proc.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    report['owned_process_still_running'] = True
            raise
        finally:
            (a.out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
