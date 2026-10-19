"""Validate actual cooked shader values against a preserved visual publication."""
import argparse,json,math,re
from pathlib import Path
from scripts.run_leopard_check import verify
def check(report,process,manifest):
 try:
  if process['accepted'] is not True or not verify(report,process['exit_code']):return False
  asset=next(x for x in manifest['payload']['entities']['assets'] if x['id']=='osebo-leopard-design')
  if report['published_visual_revision']!=asset['version']:return False
  for field,key in [('actual_cape_linear','cape_colour'),('actual_accent_linear','accent_colour')]:
   values={k:float(v) for k,v in re.findall(r'([RGBA])=([-+0-9.eE]+)',report[field])}
   if set(values)!={'R','G','B','A'} or abs(values['A']-1)>1e-4:return False
   colour=asset['data']['visual_design'][key]
   for channel,i in [('R',1),('G',3),('B',5)]:
    srgb=int(colour[i:i+2],16)/255
    expected=srgb/12.92 if srgb<=.04045 else ((srgb+.055)/1.055)**2.4
    if not math.isfinite(values[channel]) or abs(values[channel]-expected)>1e-4:return False
  return True
 except (KeyError,ValueError,TypeError,StopIteration):return False
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--publication',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise RuntimeError('Preserve prior cosmetic evidence')
 r=json.loads((a.run/'result.json').read_text(encoding='utf-8-sig'));process=json.loads((a.run/'process.json').read_text());manifest=json.loads(a.publication.read_text())
 accepted=check(r,process,manifest);a.out.write_text(json.dumps(dict(accepted=accepted,actual_cape_linear=r.get('actual_cape_linear'),actual_accent_linear=r.get('actual_accent_linear'),visual_revision=r.get('published_visual_revision'),publication_hash=manifest.get('sha256'),scope='Actual material instance parameters in rendered native package, not creative approval'),indent=2)+'\n');print('Actual cooked cosmetic parameters:',accepted);return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())
