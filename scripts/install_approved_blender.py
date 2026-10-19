"""Verify and extract only the specifically approved portable archive, offline."""
import hashlib,json,os,tarfile,posixpath
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'.local/acquisition/blender-4.5.14-approved'
NAME='blender-4.5.14-linux-x64'
ARCHIVE=SOURCE/(NAME+'.tar.xz.part')
DEST=Path('/home/favl/.local/opt')/NAME
REPORT=ROOT/'.local/verification/osebo-family-20261015/blender-acquisition/install.json'
if DEST.exists() or REPORT.exists():raise RuntimeError('Existing install/evidence must be preserved')
lines=(SOURCE/'blender-4.5.14.sha256').read_text().splitlines()
expected=[line.split()[0] for line in lines if line.split()[-1]==NAME+'.tar.xz']
if len(expected)!=1:raise RuntimeError('Official checksum entry missing/ambiguous')
with ARCHIVE.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
if actual!=expected[0]:raise RuntimeError('Archive checksum mismatch; do not extract')
with tarfile.open(ARCHIVE,'r:xz') as tar:
    members=tar.getmembers();total=0
    for m in members:
        p=PurePosixPath(m.name)
        if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0]!=NAME:
            raise RuntimeError('Unsafe archive entry')
        if not (m.isfile() or m.isdir() or m.issym() or m.islnk()):raise RuntimeError('Unsupported archive entry')
        if m.issym() or m.islnk():
            target=posixpath.normpath(posixpath.join(posixpath.dirname(m.name),m.linkname) if m.issym() else m.linkname)
            if PurePosixPath(m.linkname).is_absolute() or not target.startswith(NAME+'/'):
                raise RuntimeError('Archive link escapes destination')
        total+=m.size
    DEST.parent.mkdir(parents=True,exist_ok=True)
    if total>4*1024**3:raise RuntimeError('Archive exceeds approved working allowance')
    tar.extractall(DEST.parent,filter='data')
if not (DEST/'blender').is_file() or not os.access(DEST/'blender',os.X_OK):raise RuntimeError('Portable executable missing')
REPORT.write_text(json.dumps(dict(status='verified_extracted',archive_sha256=actual,
    archive_bytes=ARCHIVE.stat().st_size,expanded_file_bytes=total,entries=len(members),
    destination=str(DEST),approval='User approved portable Blender 4.5.14 acquisition',
    source_url='https://download.blender.org/release/Blender4.5/'+NAME+'.tar.xz',
    system_environment_modified=False),indent=2)+'\n')
print(json.dumps(dict(status='verified_extracted',entries=len(members),expanded_file_bytes=total,destination=str(DEST))))
