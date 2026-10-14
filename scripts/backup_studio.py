#!/usr/bin/env python3
"""Consistent SQLite backup, including WAL transactions. Never copies a live DB naively."""
import argparse,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'.local/studio.sqlite3');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if not a.source.is_file():p.error('Source database does not exist.')
if a.out.exists():p.error('Refusing to overwrite an existing backup.')
a.out.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(a.source) as source,sqlite3.connect(a.out) as target:source.backup(target)
with sqlite3.connect(a.out) as check:
    result=check.execute('PRAGMA integrity_check').fetchone()[0]
    if result!='ok':raise SystemExit('Backup integrity check failed: '+result)
print('Consistent backup created:',a.out)
