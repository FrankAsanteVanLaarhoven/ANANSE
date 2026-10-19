"""Transactional, single-host authoring store, NOT a production player backend."""
from __future__ import annotations
import hashlib, json, sqlite3, uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .models import references, validate

class DomainError(Exception):
    def __init__(self, status: int, message: str):
        self.status,self.message=status,message
        super().__init__(message)

def now(): return datetime.now(timezone.utc).isoformat()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def digest(obj): return hashlib.sha256(canonical(obj).encode()).hexdigest()

def row_to_record(row):
    return {"kind":row["kind"],"id":row["id"],"version":row["version"],"deleted":bool(row["deleted"]),"updated_at":row["updated_at"],"data":json.loads(row["document"])}

class Store:
    def __init__(self,path: str | Path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.executescript("""
            CREATE TABLE IF NOT EXISTS records(kind TEXT,id TEXT,version INTEGER NOT NULL,document TEXT NOT NULL,deleted INTEGER NOT NULL DEFAULT 0,updated_at TEXT NOT NULL,PRIMARY KEY(kind,id));
            CREATE TABLE IF NOT EXISTS revisions(kind TEXT,id TEXT,version INTEGER,document TEXT NOT NULL,deleted INTEGER NOT NULL,updated_at TEXT NOT NULL,actor TEXT NOT NULL,PRIMARY KEY(kind,id,version));
            CREATE TABLE IF NOT EXISTS reviews(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,id TEXT,version INTEGER,reviewer TEXT,decision TEXT,note TEXT,created_at TEXT);
            CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,target TEXT NOT NULL,payload TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS publications(id TEXT PRIMARY KEY,channel TEXT NOT NULL,created_at TEXT NOT NULL,content_hash TEXT NOT NULL,manifest TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS lab_sessions(id TEXT PRIMARY KEY,version INTEGER NOT NULL,state TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS revisions_no_update BEFORE UPDATE ON revisions BEGIN SELECT RAISE(ABORT,'revisions are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS revisions_no_delete BEFORE DELETE ON revisions BEGIN SELECT RAISE(ABORT,'revisions are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS publications_no_update BEFORE UPDATE ON publications BEGIN SELECT RAISE(ABORT,'publications are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS publications_no_delete BEFORE DELETE ON publications BEGIN SELECT RAISE(ABORT,'publications are immutable'); END;
            """)
    @contextmanager
    def connect(self,write=False):
        c=sqlite3.connect(self.path,timeout=15,isolation_level=None)
        c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON")
        try:
            if write: c.execute("BEGIN IMMEDIATE")
            yield c
            if write: c.commit()
        except BaseException:
            if write: c.rollback()
            raise
        finally: c.close()
    def _get(self,c,kind,id,include_deleted=False):
        row=c.execute("SELECT * FROM records WHERE kind=? AND id=?",(kind,id)).fetchone()
        if not row or (row["deleted"] and not include_deleted): raise DomainError(404,"Record not found.")
        return row_to_record(row)
    def get(self,kind,id,include_deleted=False):
        with self.connect() as c: return self._get(c,kind,id,include_deleted)
    def list(self,kind,include_deleted=False,limit=100,offset=0):
        with self.connect() as c:
            rows=c.execute("SELECT * FROM records WHERE kind=? AND (? OR deleted=0) ORDER BY id LIMIT ? OFFSET ?",(kind,int(include_deleted),limit,offset)).fetchall()
            total=c.execute("SELECT COUNT(*) FROM records WHERE kind=? AND (? OR deleted=0)",(kind,int(include_deleted))).fetchone()[0]
            return {"items":[row_to_record(r) for r in rows],"total":total,"limit":limit,"offset":offset}
    def _refs(self,c,kind,data):
        for rk,rid in references(kind,data):
            try: self._get(c,rk,rid)
            except DomainError: raise DomainError(409,f"Missing or archived dependency: {rk}/{rid}")
        if kind == "characters":
            for v in data["variants"]:
                for field,category in [("body_asset_id","skeletal-mesh"),("animation_asset_id","animation")]:
                    if v.get(field) and self._get(c,"assets",v[field])["data"]["category"] != category:
                        raise DomainError(409,f"{field} must reference an asset of category {category}.")
    def _audit(self,c,actor,action,target,payload):
        last=c.execute("SELECT event_hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        previous=last[0] if last else "0"*64
        stamp=now();body={"at":stamp,"actor":actor,"action":action,"target":target,"payload":payload,"previous_hash":previous}
        c.execute("INSERT INTO audit(created_at,actor,action,target,payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?)",(stamp,actor,action,target,canonical(payload),previous,digest(body)))
    def _revision(self,c,record,actor,action):
        c.execute("INSERT INTO revisions VALUES(?,?,?,?,?,?,?)",(record["kind"],record["id"],record["version"],canonical(record["data"]),int(record["deleted"]),record["updated_at"],actor))
        self._audit(c,actor,action,f'{record["kind"]}/{record["id"]}',{"version":record["version"],"record_hash":digest(record)})
    def create(self,kind,id,data,actor):
        data=validate(kind,data)
        with self.connect(True) as c:
            if c.execute("SELECT 1 FROM records WHERE kind=? AND id=?",(kind,id)).fetchone(): raise DomainError(409,"ID exists, including archived IDs. Restore or choose a new ID.")
            self._refs(c,kind,data)
            r={"kind":kind,"id":id,"version":1,"data":data,"deleted":False,"updated_at":now()}
            c.execute("INSERT INTO records VALUES(?,?,?,?,?,?)",(kind,id,1,canonical(data),0,r["updated_at"]))
            self._revision(c,r,actor,"create");return r
    def update(self,kind,id,data,expected,actor):
        data=validate(kind,data)
        with self.connect(True) as c:
            r=self._get(c,kind,id)
            if r["version"] != expected: raise DomainError(412,"Stale revision; reload and reconcile before saving.")
            self._refs(c,kind,data)
            # A referenced asset cannot silently change type.
            if kind == "assets" and data["category"] != r["data"]["category"]:
                for row in c.execute("SELECT * FROM records WHERE kind='characters' AND deleted=0"):
                    if (kind,id) in references("characters",json.loads(row["document"])): raise DomainError(409,"Referenced asset category cannot change.")
            r.update(data=data,version=r["version"]+1,updated_at=now())
            c.execute("UPDATE records SET document=?,version=?,updated_at=? WHERE kind=? AND id=?",(canonical(data),r["version"],r["updated_at"],kind,id))
            self._revision(c,r,actor,"update");return r
    def archive(self,kind,id,expected,actor,restore=False):
        with self.connect(True) as c:
            r=self._get(c,kind,id,True)
            if r["version"] != expected: raise DomainError(412,"Stale revision.")
            if r["deleted"] != restore: raise DomainError(409,"Record is already in the requested state.")
            if restore: self._refs(c,kind,r["data"])
            else:
                for row in c.execute("SELECT * FROM records WHERE deleted=0"):
                    if (kind,id) in references(row["kind"],json.loads(row["document"])):
                        raise DomainError(409,f'Dependency is used by {row["kind"]}/{row["id"]}; remove that reference first.')
            r.update(deleted=not restore,version=r["version"]+1,updated_at=now())
            c.execute("UPDATE records SET deleted=?,version=?,updated_at=? WHERE kind=? AND id=?",(int(r["deleted"]),r["version"],r["updated_at"],kind,id))
            self._revision(c,r,actor,"restore" if restore else "archive");return r
    def history(self,kind,id):
        with self.connect() as c:
            self._get(c,kind,id,True)
            return [dict(r)|{"data":json.loads(r["document"])} for r in c.execute("SELECT * FROM revisions WHERE kind=? AND id=? ORDER BY version DESC",(kind,id))]
    def revert(self,kind,id,revision,expected,actor):
        with self.connect(True) as c:
            current=self._get(c,kind,id)
            if current["version"] != expected: raise DomainError(412,"Stale revision.")
            old=c.execute("SELECT * FROM revisions WHERE kind=? AND id=? AND version=?",(kind,id,revision)).fetchone()
            if not old: raise DomainError(404,"Revision not found.")
            data=validate(kind,json.loads(old["document"]));self._refs(c,kind,data)
            if kind == "assets" and data["category"] != current["data"]["category"]:
                for row in c.execute("SELECT * FROM records WHERE kind='characters' AND deleted=0"):
                    if (kind,id) in references("characters",json.loads(row["document"])): raise DomainError(409,"Referenced asset category cannot change.")
            current.update(data=data,version=current["version"]+1,updated_at=now())
            c.execute("UPDATE records SET document=?,version=?,updated_at=? WHERE kind=? AND id=?",(canonical(data),current["version"],current["updated_at"],kind,id))
            self._revision(c,current,actor,"revert");return current
    def review(self,kind,id,version,reviewer,decision,note):
        with self.connect(True) as c:
            r=self._get(c,kind,id)
            if r["version"] != version: raise DomainError(412,"Only the current revision can be reviewed.")
            latest=c.execute("SELECT actor FROM revisions WHERE kind=? AND id=? AND version=?",(kind,id,version)).fetchone()[0]
            if latest == reviewer: raise DomainError(403,"An author cannot approve their own revision.")
            c.execute("INSERT INTO reviews(kind,id,version,reviewer,decision,note,created_at) VALUES(?,?,?,?,?,?,?)",(kind,id,version,reviewer,decision,note,now()))
            self._audit(c,reviewer,"review",f"{kind}/{id}",{"version":version,"decision":decision,"note":note})
            return {"kind":kind,"id":id,"version":version,"decision":decision}
    def validation(self):
        with self.connect() as c: return self._validation(c)
    def _validation(self,c):
        issues=[];records=[row_to_record(r) for r in c.execute("SELECT * FROM records WHERE deleted=0 ORDER BY kind,id")]
        for r in records:
            key=f'{r["kind"]}/{r["id"]}'
            validate(r["kind"],r["data"])
            self._refs(c,r["kind"],r["data"])
            review=c.execute("SELECT decision FROM reviews WHERE kind=? AND id=? AND version=? ORDER BY seq DESC LIMIT 1",(r["kind"],r["id"],r["version"])).fetchone()
            if not review or review[0] != "approved": issues.append({"record":key,"code":"REVIEW_REQUIRED","detail":"Current revision needs independent review."})
            if r["kind"] == "characters":
                if r["data"]["stage"] != "runtime-ready": issues.append({"record":key,"code":"CHARACTER_NOT_RUNTIME_READY","detail":"Concept/greybox data is not final character art."})
                for v in r["data"]["variants"]:
                    if not v["body_asset_id"]: issues.append({"record":key,"code":"MISSING_MESH","detail":f'Variant {v["id"]} has no approved skeletal mesh.'})
            if r["kind"] == "assets":
                d=r["data"]
                if d["status"] != "approved" or not d["unreal_path"] or not d["sha256"] or d["licence"] == "UNVERIFIED" or not d["mobile_review_passed"]:
                    issues.append({"record":key,"code":"ASSET_NOT_APPROVED","detail":"Asset needs provenance, cooked-file verification, mobile review and approval."})
        # No runtime inspection, signing service, or two-person OIDC release authority is bundled.
        issues.append({"record":"release","code":"PRODUCTION_VALIDATOR_NOT_CONNECTED","detail":"Production cook evidence, asset-byte verification, signing and OIDC release approvals are not implemented in this local starter."})
        return {"record_count":len(records),"prototype_export_allowed":True,"production_export_allowed":False,"issues":issues}
    def publish(self,channel,actor):
        with self.connect(True) as c:
            report=self._validation(c)
            designs=set()
            for row in c.execute("SELECT * FROM records WHERE kind='assets' AND deleted=0"):
                record=row_to_record(row);design=record['data'].get('visual_design')
                if not design: continue
                if design['design_id'] in designs: raise DomainError(409,"Duplicate visual design bindings must be reconciled before publication.")
                designs.add(design['design_id'])
                review=c.execute("SELECT decision FROM reviews WHERE kind='assets' AND id=? AND version=? ORDER BY seq DESC LIMIT 1",(record['id'],record['version'])).fetchone()
                if not review or review['decision']!='approved': raise DomainError(409,"Visual design publication requires approval of its exact current asset revision.")
            if channel != "prototype": raise DomainError(409,"Production publish is blocked. Inspect /api/validation; this starter has no verified production release adapter.")
            entities={k:[] for k in ("characters","factions","missions","assets")}
            for row in c.execute("SELECT * FROM records WHERE deleted=0 ORDER BY kind,id"):
                r=row_to_record(row);entities[r["kind"]].append(r)
            payload={"schema_version":1,"channel":channel,"created_at":now(),"entities":entities,"warnings":report["issues"]}
            manifest={"payload":payload,"sha256":digest(payload)}
            id=uuid.uuid4().hex
            c.execute("INSERT INTO publications VALUES(?,?,?,?,?)",(id,channel,payload["created_at"],manifest["sha256"],canonical(manifest)))
            self._audit(c,actor,"publish",id,{"channel":channel,"sha256":manifest["sha256"]})
            return {"id":id,"manifest":manifest}
    def publication(self,id):
        with self.connect() as c:
            r=c.execute("SELECT manifest FROM publications WHERE id=?",(id,)).fetchone()
            if not r: raise DomainError(404,"Publication not found.")
            return json.loads(r[0])
    def audit(self,limit=200):
        with self.connect() as c: return [dict(r) for r in c.execute("SELECT * FROM audit ORDER BY seq DESC LIMIT ?",(limit,))]
    def verify_audit(self):
        prev="0"*64;count=0
        with self.connect() as c:
            for r in c.execute("SELECT * FROM audit ORDER BY seq"):
                body={"at":r["created_at"],"actor":r["actor"],"action":r["action"],"target":r["target"],"payload":json.loads(r["payload"]),"previous_hash":prev}
                if r["previous_hash"] != prev or r["event_hash"] != digest(body): return {"valid":False,"events":count}
                prev=r["event_hash"];count+=1
        return {"valid":True,"events":count,"head":prev,"note":"Local integrity check, not tamper-proof storage."}
