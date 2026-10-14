#!/usr/bin/env python3
"""Export a previously published immutable prototype snapshot, not an editable DB view."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from studio.store import Store,digest
from studio.models import validate,references

def verify_manifest(manifest):
    payload=manifest['payload']
    if manifest['sha256']!=digest(payload):raise ValueError('Content digest mismatch.')
    if payload['schema_version']!=1 or payload['channel']!='prototype':raise ValueError('Unsupported manifest version or channel.')
    entities=payload['entities'];keys=set()
    if set(entities)!={'characters','factions','missions','assets'}:raise ValueError('Manifest entity collections are incomplete or unknown.')
    for kind,records in entities.items():
        for record in records:
            if record['deleted'] or record['kind']!=kind:raise ValueError('Archived or incorrectly typed entity in manifest.')
            key=(kind,record['id'])
            if key in keys:raise ValueError('Duplicate identity.')
            keys.add(key);validate(kind,record['data'])
    for kind,records in entities.items():
        for record in records:
            if any(ref not in keys for ref in references(kind,record['data'])):raise ValueError('Broken manifest dependency.')
    return payload

def main():
    p=argparse.ArgumentParser();p.add_argument('--publication',required=True);p.add_argument('--db',type=Path,default=ROOT/'.local/studio.sqlite3');p.add_argument('--out',type=Path,default=ROOT/'Unreal/Content/Data/catalogue.json');a=p.parse_args()
    if not a.db.is_file():p.error('No studio database exists. Run the studio and publish a prototype first.')
    manifest=Store(a.db).publication(a.publication);verify_manifest(manifest)
    a.out.parent.mkdir(parents=True,exist_ok=True);temp=a.out.with_suffix(a.out.suffix+'.tmp')
    temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');temp.replace(a.out)
    print(f'Exported {manifest["sha256"]} to {a.out}; rebuild/cook Unreal to consume this revision.')
if __name__=='__main__':main()
