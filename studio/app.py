"""Loopback-only local studio. The shipping game never receives editor credentials."""
from __future__ import annotations
import hashlib, json, secrets, uuid
from pathlib import Path
from fastapi import FastAPI, Depends, Header, Query, Response, Request
from fastapi.responses import JSONResponse, FileResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError
from .models import Kind, CreateRecord, UpdateRecord, Review, Publish, Revert, LabAction, SCHEMAS
from .store import Store, DomainError, canonical
from . import lab

STATIC=Path(__file__).parent/"static"

def create_app(db_path, tokens: dict[str,str], seed_path: Path | None = None):
    if set(tokens)!={"editor","reviewer","publisher"} or any(len(v)<32 for v in tokens.values()) or len(set(tokens.values()))!=3:
        raise ValueError("Three distinct editor, reviewer and publisher secrets of at least 32 characters are required.")
    store=Store(db_path)
    if seed_path:
        seed=json.loads(Path(seed_path).read_text())
        for kind in ("factions","assets","characters","missions"):
            for r in seed[kind]:
                try: store.get(kind,r["id"],True)
                except DomainError: store.create(kind,r["id"],r["data"],"seed-import")
    app=FastAPI(title="ANANSE local Content Studio",version="0.1.0",docs_url=None,redoc_url=None,openapi_url=None)
    app.state.store=store
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=["127.0.0.1","localhost","[::1]","testserver"])
    @app.middleware("http")
    async def guard(request:Request,call_next):
        origin=request.headers.get("origin")
        if origin and origin!=str(request.base_url).rstrip("/"):
            return JSONResponse({"detail":"Cross-origin access is not allowed."},403)
        # Enforce an actual byte limit, including chunked requests; metadata only.
        total=0;parts=[]
        async for part in request.stream():
            total+=len(part)
            if total>262144: return JSONResponse({"detail":"Metadata body exceeds 256 KiB."},413)
            parts.append(part)
        request._body=b"".join(parts)
        response=await call_next(request)
        response.headers["Content-Security-Policy"]="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["Cache-Control"]="no-store"
        return response
    @app.exception_handler(DomainError)
    async def domain_error(request,exc): return JSONResponse({"detail":exc.message},exc.status)
    @app.exception_handler(ValidationError)
    async def validation_error(request,exc):
        return JSONResponse({"detail":json.loads(exc.json(include_url=False))},422)
    def principal(authorization: str | None = Header(default=None)):
        supplied=authorization.removeprefix("Bearer ") if authorization and authorization.startswith("Bearer ") else ""
        for role,token in tokens.items():
            if secrets.compare_digest(supplied,token): return {"role":role,"actor":hashlib.sha256(token.encode()).hexdigest()[:20]}
        raise DomainError(401,"Supply a valid local role token as Bearer authorization.")
    def permission(p,role):
        if p["role"]!=role: raise DomainError(403,f"This operation requires the {role} role.")
    def expected(if_match):
        if if_match is None: raise DomainError(428,"If-Match is required for writes to existing records.")
        text=if_match.strip('"')
        if not text.isdecimal() or int(text)<1: raise DomainError(400,"If-Match must contain a positive revision number.")
        return int(text)
    def tagged(r,response):response.headers["ETag"]=f'"{r["version"]}"';return r
    @app.get("/")
    def index(): return FileResponse(STATIC/"index.html")
    @app.get("/static/{name}")
    def static(name:str):
        if name not in {"app.js","style.css"}:raise DomainError(404,"Not found.")
        return FileResponse(STATIC/name)
    @app.get("/health")
    def health(): return {"status":"ok","mode":"local-authoring-prototype","unreal_verified":False}
    @app.get("/api/whoami")
    def whoami(p=Depends(principal)):return p
    @app.get("/api/openapi")
    def openapi(p=Depends(principal)):return app.openapi()
    @app.get("/api/schemas")
    def schemas(p=Depends(principal)):return {k:v.model_json_schema() for k,v in SCHEMAS.items()}
    @app.get("/api/validation")
    def validation(p=Depends(principal)):return store.validation()
    @app.get("/api/audit")
    def audit(p=Depends(principal),limit:int=Query(default=100,ge=1,le=1000)):return {"items":store.audit(limit),"integrity":store.verify_audit()}
    @app.post("/api/publish",status_code=201)
    def publish(body:Publish,p=Depends(principal)):
        permission(p,"publisher");return store.publish(body.channel,p["actor"])
    @app.get("/api/publications/{id}")
    def publication(id:str,p=Depends(principal)):return store.publication(id)
    @app.get("/api/lab/actions")
    def actions(p=Depends(principal)):return lab.ACTIONS
    @app.post("/api/lab/sessions",status_code=201)
    def new_session(p=Depends(principal)):
        permission(p,"editor");id=uuid.uuid4().hex;s=lab.initial()
        with store.connect(True) as c: c.execute("INSERT INTO lab_sessions VALUES(?,?,?)",(id,1,canonical(s)))
        return {"id":id,"version":1,"state":s}
    @app.get("/api/lab/sessions/{id}")
    def get_session(id:str,p=Depends(principal)):
        with store.connect() as c:
            r=c.execute("SELECT * FROM lab_sessions WHERE id=?",(id,)).fetchone()
            if not r:raise DomainError(404,"Session not found.")
            return {"id":id,"version":r["version"],"state":json.loads(r["state"])}
    @app.post("/api/lab/sessions/{id}/actions")
    def act(id:str,body:LabAction,p=Depends(principal)):
        permission(p,"editor")
        with store.connect(True) as c:
            r=c.execute("SELECT * FROM lab_sessions WHERE id=?",(id,)).fetchone()
            if not r:raise DomainError(404,"Session not found.")
            if r["version"]!=body.expected_version:raise DomainError(412,"Stale lab session; reload before acting.")
            if r["version"]>300:raise DomainError(409,"Local lab run limit reached; begin a new run.")
            s=lab.step(json.loads(r["state"]),body.action);v=r["version"]+1
            c.execute("UPDATE lab_sessions SET version=?,state=? WHERE id=?",(v,canonical(s),id))
        return {"id":id,"version":v,"state":s}
    @app.get("/api/{kind}")
    def listing(kind:Kind,p=Depends(principal),include_deleted:bool=False,limit:int=Query(default=100,ge=1,le=100),offset:int=Query(default=0,ge=0)):
        return store.list(kind,include_deleted,limit,offset)
    @app.post("/api/{kind}",status_code=201)
    def create(kind:Kind,body:CreateRecord,response:Response,p=Depends(principal)):
        permission(p,"editor");return tagged(store.create(kind,body.id,body.data,p["actor"]),response)
    @app.get("/api/{kind}/{id}")
    def get(kind:Kind,id:str,response:Response,p=Depends(principal),include_deleted:bool=False):return tagged(store.get(kind,id,include_deleted),response)
    @app.patch("/api/{kind}/{id}")
    def update(kind:Kind,id:str,body:UpdateRecord,response:Response,p=Depends(principal),if_match:str|None=Header(default=None)):
        permission(p,"editor");return tagged(store.update(kind,id,body.data,expected(if_match),p["actor"]),response)
    @app.delete("/api/{kind}/{id}")
    def archive(kind:Kind,id:str,response:Response,p=Depends(principal),if_match:str|None=Header(default=None)):
        permission(p,"editor");return tagged(store.archive(kind,id,expected(if_match),p["actor"]),response)
    @app.post("/api/{kind}/{id}/restore")
    def restore(kind:Kind,id:str,response:Response,p=Depends(principal),if_match:str|None=Header(default=None)):
        permission(p,"editor");return tagged(store.archive(kind,id,expected(if_match),p["actor"],True),response)
    @app.get("/api/{kind}/{id}/history")
    def history(kind:Kind,id:str,p=Depends(principal)):return {"items":store.history(kind,id)}
    @app.post("/api/{kind}/{id}/revert")
    def revert(kind:Kind,id:str,body:Revert,response:Response,p=Depends(principal),if_match:str|None=Header(default=None)):
        permission(p,"editor");return tagged(store.revert(kind,id,body.revision,expected(if_match),p["actor"]),response)
    @app.post("/api/{kind}/{id}/review")
    def review(kind:Kind,id:str,body:Review,p=Depends(principal)):
        permission(p,"reviewer");return store.review(kind,id,body.version,p["actor"],body.decision,body.note)
    return app
