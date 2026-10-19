"use strict";
const $=id=>document.getElementById(id);
let token="",kind="characters",selected=null,records=[],session=null,actionLabels={};
let designPreview=null,designPreviewGeneration=0;
function clearDesignPreview(){designPreviewGeneration++;if(designPreview){designPreview.dispose();designPreview=null;}$("design-tools").hidden=true;}
function notice(message,error=false){$("notice").textContent=message;$("notice").classList.toggle("error",error);}
async function api(path,method="GET",body=undefined,version=undefined){
 const headers={Authorization:`Bearer ${token}`};if(body!==undefined)headers["Content-Type"]="application/json";if(version!==undefined)headers["If-Match"]=`"${version}"`;
 const response=await fetch(path,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
 const value=await response.json();if(!response.ok)throw new Error(typeof value.detail==="string"?value.detail:JSON.stringify(value.detail));return value;
}
function run(fn){return async()=>{try{await fn();}catch(e){notice(e.message,true);}};}
function report(title,data){$("dialog-title").textContent=title;$("dialog-body").textContent=JSON.stringify(data,null,2);$("dialog-actions").replaceChildren();$("dialog").showModal();}
function editorData(){return JSON.parse($("json").value);}
function requireRecord(){if(!selected)throw new Error("Select a record first.");}
async function load(){
 records=[];let page;do{page=await api(`/api/${kind}?include_deleted=${$("archived").checked}&limit=100&offset=${records.length}`);records.push(...page.items);}while(records.length<page.total);
 $("count").textContent=String(records.length);renderList();
 if(selected){const fresh=records.find(r=>r.id===selected.id);if(fresh)select(fresh);else{clearDesignPreview();selected=null;$("json").value="";$("character-tools").hidden=true;}}
}
function renderList(){
 $("records").replaceChildren();const term=$("search").value.toLowerCase();
 for(const r of records){if(!`${r.id} ${r.data.name}`.toLowerCase().includes(term))continue;
  const b=document.createElement("button");b.classList.toggle("selected",selected?.id===r.id);b.textContent=r.data.name;
  const sub=document.createElement("span");sub.className="subtitle";sub.textContent=`${r.id} · revision ${r.version}${r.deleted?" · archived":""}`;b.append(sub);b.addEventListener("click",()=>select(r));$("records").append(b);
 }
}
function select(r){selected=r;$("record-id").textContent=`${kind.toUpperCase()} / ${r.id}`;$("record-name").textContent=r.data.name;$("revision").textContent=`REVISION ${r.version}${r.deleted?" · ARCHIVED":""}`;$("json").value=JSON.stringify(r.data,null,2);$("character-tools").hidden=kind!=="characters";if(kind==="characters")variants();
 designPreviewGeneration++;if(designPreview){designPreview.dispose();designPreview=null;}$("design-tools").hidden=kind!=="assets"||!r.data.visual_design;$("design-status").textContent="Source not loaded; no native/art acceptance implied.";
 if(r.data.visual_design){const cosmetics=r.data.visual_design.design_id==="osebo-leopard-v1";$("design-cape").disabled=!cosmetics;$("design-accent").disabled=!cosmetics;if(cosmetics){$("design-cape").value=r.data.visual_design.cape_colour;$("design-accent").value=r.data.visual_design.accent_colour;}}renderList();}
$("design-preview").onclick=run(async()=>{requireRecord();const generation=++designPreviewGeneration;$("design-status").textContent="Validating local source bytes…";const response=await fetch(`/api/assets/${encodeURIComponent(selected.id)}/preview.glb`,{headers:{Authorization:`Bearer ${token}`}});if(!response.ok)throw Error((await response.json()).detail);const bytes=await response.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');if(hash!==selected.data.visual_design.source_glb_sha256||hash!==response.headers.get('X-Source-SHA256'))throw Error('Preview bytes failed exact revision integrity.');const module=await import('/static/leopard-preview.js');if(generation!==designPreviewGeneration)return;if(designPreview)designPreview.dispose();const candidate=await module.preview($('design-canvas'),bytes,{clips:$('design-clip'),turn:$('design-turn'),wire:$('design-wire'),blink:$('design-blink'),cape:$('design-cape'),accent:$('design-accent')});if(generation!==designPreviewGeneration){candidate.dispose();return;}designPreview=candidate;$('design-status').textContent=`Actual saved model: ${candidate.boneCount} joints, ${candidate.clipCount} clips, ${candidate.morphCount} eyelid targets. SHA-256 ${hash}. Final art/contact approval remains separate.`;});
for(const id of ['design-cape','design-accent'])$(id).oninput=run(async()=>{const d=editorData();if(!d.visual_design)throw Error('No selected visual design');d.visual_design[id==='design-cape'?'cape_colour':'accent_colour']=$(id).value;$("json").value=JSON.stringify(d,null,2);});
function variants(){
 const d=editorData();$("variant").replaceChildren();for(const v of d.variants){const o=document.createElement("option");o.value=v.id;o.textContent=v.label;$("variant").append(o);}variantFields();
}
function variantFields(){const d=editorData(),v=d.variants.find(v=>v.id===$("variant").value);if(!v)return;$("cloth").value=v.cloth_colour;$("accent").value=v.accent_colour;$("scale").value=v.body_scale??1;$("scale-value").value=v.body_scale??1;draw(d,v);}
function editVariant(){const d=editorData(),v=d.variants.find(v=>v.id===$("variant").value);v.cloth_colour=$("cloth").value;v.accent_colour=$("accent").value;v.body_scale=Number($("scale").value);$("scale-value").value=v.body_scale;$("json").value=JSON.stringify(d,null,2);draw(d,v);}
function draw(d,v){
 const c=$("preview"),ctx=c.getContext("2d"),w=c.width,h=c.height;ctx.clearRect(0,0,w,h);ctx.fillStyle="#121c17";ctx.fillRect(0,0,w,h);ctx.strokeStyle="#2c3c2d";for(let i=20;i<w;i+=30){ctx.beginPath();ctx.moveTo(i,245);ctx.lineTo(w/2+(i-w/2)*2,290);ctx.stroke();}
 ctx.save();ctx.translate(w/2,245);ctx.scale(v.body_scale??1,v.body_scale??1);ctx.fillStyle="#090e0b";ctx.beginPath();ctx.ellipse(0,5,70,13,0,0,7);ctx.fill();
 ctx.fillStyle=v.cloth_colour;
 if(d.silhouette==="serpent"){ctx.lineWidth=27;ctx.strokeStyle=v.cloth_colour;ctx.beginPath();ctx.moveTo(-55,-12);ctx.bezierCurveTo(80,-25,-90,-110,32,-150);ctx.stroke();ctx.fillStyle=v.accent_colour;ctx.fillRect(20,-163,35,24);}
 else if(d.silhouette==="swarm"){for(let i=0;i<30;i++){ctx.beginPath();ctx.arc(Math.sin(i*2.7)*65,-85+Math.cos(i*1.7)*65,5,0,7);ctx.fill();}}
 else{ctx.fillRect(-32,-141,64,78);ctx.fillRect(-30,-62,23,58);ctx.fillRect(7,-62,23,58);ctx.fillRect(-52,-135,15,75);ctx.fillRect(37,-135,15,75);ctx.fillStyle=v.accent_colour;ctx.beginPath();ctx.arc(0,-169,24,0,7);ctx.fill();ctx.fillRect(-33,-77,66,8);if(d.silhouette==="scholar"||d.silhouette==="court"){ctx.beginPath();ctx.moveTo(-32,-116);ctx.lineTo(-53,-12);ctx.lineTo(53,-12);ctx.lineTo(32,-116);ctx.closePath();ctx.fill();}if(d.silhouette==="guard"){ctx.fillRect(52,-158,6,147);}}
 ctx.restore();ctx.textAlign="center";ctx.font="10px system-ui";ctx.fillStyle="#b3c0b0";ctx.fillText("PROCEDURAL STAND-IN · NOT CHARACTER ART",w/2,21);ctx.fillText(`${d.representation.toUpperCase()} / ${d.silhouette.toUpperCase()}`,w/2,301);
}
$("connect").onclick=run(async()=>{token=$("token").value.trim();const me=await api("/api/whoami");$("token").value="";$("identity").textContent=`Connected as ${me.role}`;notice("Connected. Changes are local and versioned; production publishing remains blocked.");await load();});
for(const b of document.querySelectorAll("[data-kind]"))b.onclick=run(async()=>{clearDesignPreview();kind=b.dataset.kind;selected=null;document.querySelectorAll("[data-kind]").forEach(x=>x.classList.toggle("active",x===b));$("list-heading").textContent=b.textContent;$("record-name").textContent="Select a record";$("json").value="";$("character-tools").hidden=true;await load();});
$("search").oninput=renderList;$("archived").onchange=run(load);$("variant").onchange=variantFields;
for(const id of ["cloth","accent","scale"])$(id).oninput=editVariant;
$("json").addEventListener("change",run(async()=>{if(kind==="characters")variants();}));
$("save").onclick=run(async()=>{requireRecord();const r=await api(`/api/${kind}/${selected.id}`,"PATCH",{data:editorData()},selected.version);select(r);notice(`Saved revision ${r.version}. Any prior review applies only to its original revision.`);await load();});
const defaults={characters:{name:"New Story Road character",role:"Original role",source_note:"Original draft; cultural review pending.",variants:[{id:"base",label:"Base concept"}]},factions:{name:"New faction",description:"Draft"},missions:{name:"New mission",supported_routes:["social"],endings:["truth-exposed","witnesses-protected"]},assets:{name:"New asset",category:"skeletal-mesh"}};
async function create(duplicate){if(duplicate)requireRecord();const id=prompt("New stable ID: lowercase letters, numbers and hyphens");if(!id)return;const data=duplicate?editorData():structuredClone(defaults[kind]);if(duplicate)data.name+=" — variant character";const r=await api(`/api/${kind}`,"POST",{id,data});selected=r;await load();notice(`Created ${id}; no existing record was changed.`);}
$("create").onclick=run(()=>create(false));$("duplicate").onclick=run(()=>create(true));
$("add-variant").onclick=run(async()=>{requireRecord();const id=prompt("New appearance variant ID");if(!id)return;const d=editorData();d.variants.push({...structuredClone(d.variants[0]),id,label:id});$("json").value=JSON.stringify(d,null,2);variants();notice("Variant added to the draft. Save a new revision to persist it.");});
$("delete").onclick=run(async()=>{requireRecord();if(!confirm(`Archive ${selected.id}? Dependencies may block this.`))return;await api(`/api/${kind}/${selected.id}`,"DELETE",undefined,selected.version);selected=null;await load();notice("Archived; ID, revision history and prior publications remain preserved.");});
$("restore").onclick=run(async()=>{requireRecord();selected=await api(`/api/${kind}/${selected.id}/restore`,"POST",undefined,selected.version);await load();notice("Record restored as a new revision.");});
$("history").onclick=run(async()=>{requireRecord();const h=await api(`/api/${kind}/${selected.id}/history`);report("Revision history",h);for(const r of h.items){const b=document.createElement("button");b.textContent=`Revert to r${r.version}`;b.onclick=run(async()=>{selected=await api(`/api/${kind}/${selected.id}/revert`,"POST",{revision:r.version},selected.version);$("dialog").close();await load();notice("History restored into a NEW revision, not overwritten.");});$("dialog-actions").append(b);}});
$("review").onclick=run(async()=>{requireRecord();const note=prompt("Review note (reviewer token required). Do not certify work you have not inspected.");if(!note)return;const r=await api(`/api/${kind}/${selected.id}/review`,"POST",{version:selected.version,decision:"approved",note});report("Revision review recorded",r);});
$("validate").onclick=run(async()=>report("Production release blockers",await api("/api/validation")));
$("audit").onclick=run(async()=>report("Local audit trail (not tamper-proof storage)",await api("/api/audit")));
$("publish").onclick=run(async()=>{const r=await api("/api/publish","POST",{channel:"prototype"});report("Immutable prototype publication",{publication_id:r.id,sha256:r.manifest.sha256,next_command:`python scripts/export_content.py --publication ${r.id}`,warning_count:r.manifest.payload.warnings.length});const b=document.createElement("button");b.textContent="Save manifest JSON";b.onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(r.manifest,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="catalogue.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};$("dialog-actions").append(b);});
$("close-dialog").onclick=()=>$("dialog").close();
function renderLab(){if(!session)return;const s=session.state;$("lab-metrics").textContent=`BEAT ${s.turn} · ${s.location.toUpperCase()} · THREAD ${s.thread}/3 · SUSPICION ${s.suspicion}/100${s.outcome?` · ${s.outcome}`:""}`;$("lab-state").textContent=JSON.stringify(s,null,2);$("lab-events").replaceChildren();for(const e of s.events){const li=document.createElement("li");li.textContent=e.why;$("lab-events").append(li);}for(const b of $("lab-actions").querySelectorAll("button"))b.disabled=!!s.outcome;}
$("open-lab").onclick=run(async()=>{$("lab").hidden=false;actionLabels=await api("/api/lab/actions");$("lab-actions").replaceChildren();for(const [action,label] of Object.entries(actionLabels)){const b=document.createElement("button");b.textContent=label;b.onclick=run(async()=>{if(!session)throw new Error("Start a new run first.");session=await api(`/api/lab/sessions/${session.id}/actions`,"POST",{action,expected_version:session.version});renderLab();notice("Narrative action applied. This tests rules, not animation or mobile performance.");});$("lab-actions").append(b);}$("lab").scrollIntoView({behavior:"smooth"});});
$("new-run").onclick=run(async()=>{session=await api("/api/lab/sessions","POST");renderLab();notice("Fresh deterministic run. Try evidence → negotiation → archive → ledger → protect.");});
