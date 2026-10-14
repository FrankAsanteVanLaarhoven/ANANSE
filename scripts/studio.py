#!/usr/bin/env python3
"""Start a local authoring server. No installation, cloud deployment, or engine download."""
import argparse,json,os,secrets,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--db',type=Path,default=ROOT/'.local/studio.sqlite3');args=p.parse_args()
    if not 1024<=args.port<=65535:p.error('Use a non-privileged port from 1024 to 65535.')
    local=ROOT/'.local';local.mkdir(exist_ok=True)
    creds=local/'credentials.json'
    if not creds.exists():
        values={role:secrets.token_urlsafe(32) for role in ('editor','reviewer','publisher')}
        fd=os.open(creds,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as f:json.dump(values,f,indent=2)
    tokens=json.loads(creds.read_text())
    if os.name=='posix':creds.chmod(0o600)
    from studio.app import create_app
    import uvicorn
    print(f'ANANSE local studio: http://127.0.0.1:{args.port}')
    print(f'Role tokens are in {creds}. Paste the editor token into the studio. Never share or commit this file.')
    print('This is a loopback-only prototype, not a production deployment.')
    uvicorn.run(create_app(args.db,tokens,ROOT/'content/seed.json'),host='127.0.0.1',port=args.port,access_log=False)
if __name__=='__main__':main()
