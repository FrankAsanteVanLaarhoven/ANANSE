"""Deterministic story-rule laboratory. Not the Unreal game or a network game server."""
from copy import deepcopy
from .store import DomainError
ACTIONS={
    "inspect-evidence":"Inspect the altered royal edict",
    "listen-captain":"Listen to the captain's authorised call",
    "borrowed-voice":"Use Borrowed Voice at the gate",
    "negotiate":"Promise to protect the market witnesses",
    "web-step":"Take the rooftop route with Web Step",
    "trick-mirror":"Distract the archive guard",
    "enter-archive":"Enter the guarded archive",
    "take-ledger":"Recover the ledger of stolen names",
    "challenge-identity":"Test a guard's challenge to your disguise",
    "expose":"Expose the forged edict publicly",
    "protect":"Protect the witnesses; withhold the ledger",
    "wait":"Wait one narrative beat",
}
def initial():
    return {"turn":0,"thread":3,"suspicion":0,"inventory":[],"location":"market","route":None,"outcome":None,
            "guard_beliefs":{},"kojo_beliefs":{},"voice_until":-1,"distraction_until":-1,"promise":False,
            "reputation":{"market":0,"court":0},"cooldowns":{},"events":[]}
def step(state,action):
    if action not in ACTIONS: raise DomainError(422,"Unknown lab action.")
    if state["outcome"]: raise DomainError(409,"This run has ended. Start a new session.")
    s=deepcopy(state);s["turn"]+=1;t=s["turn"];why=""
    if t>s["voice_until"]: s["guard_beliefs"].pop("royal-courier",None)
    def has(item): return item in s["inventory"]
    def power(name):
        if s["thread"]<1: raise DomainError(409,"No story-thread remains in this run.")
        if t<s["cooldowns"].get(name,0): raise DomainError(409,"Power is on cooldown.")
        s["thread"]-=1;s["cooldowns"][name]=t+2
    if action=="inspect-evidence":
        if has("forgery-evidence"): raise DomainError(409,"Evidence already collected; it cannot be farmed.")
        s["inventory"].append("forgery-evidence");s["kojo_beliefs"]["edict-forged"]=1.0
        why="You found the overwritten seal. Kojo knows this; the gate guard does not."
    elif action=="listen-captain":
        if has("captains-call"): raise DomainError(409,"The call is already learned.")
        s["inventory"].append("captains-call");why="You learned one authorised phrase, not a universal identity."
    elif action=="borrowed-voice":
        if not has("captains-call"): raise DomainError(409,"First listen to the captain's authorised call.")
        power(action);s["guard_beliefs"]["royal-courier"]=0.75;s["voice_until"]=t+2
        s["suspicion"]+=8;why="Only this guard tentatively accepts the voice; evidence can still contradict it."
    elif action=="negotiate":
        if not has("forgery-evidence"): raise DomainError(409,"Negotiation needs evidence, not an arbitrary dialogue roll.")
        if has("market-permit"): raise DomainError(409,"The promise was already made.")
        s["promise"]=True;s["inventory"].append("market-permit");s["reputation"]["market"]+=1
        why="A market elder grants access in exchange for protecting the witnesses."
    elif action=="web-step":
        if s["location"]!="market": raise DomainError(409,"This anchor is only reachable from the market.")
        power(action);s["location"]="rooftop";s["suspicion"]+=10;why="The rooftop bypasses the checkpoint, not the archive watcher."
    elif action=="trick-mirror":
        power(action);s["distraction_until"]=t+2;why="The archive watcher follows a decoy for two narrative beats."
    elif action=="enter-archive":
        if s["location"]=="archive": raise DomainError(409,"Already inside the archive.")
        if has("market-permit"): s["route"]="negotiation"
        elif s["guard_beliefs"].get("royal-courier",0)>=0.7: s["route"]="social"
        elif s["location"]=="rooftop" and t<=s["distraction_until"]: s["route"]="rooftop"
        else:
            s["suspicion"]+=25;why="Access denied: no accepted identity, permit, or distracted rooftop opening."
        if not why: s["location"]="archive";why=f'Archive reached through the {s["route"]} route.'
    elif action=="take-ledger":
        if s["location"]!="archive": raise DomainError(409,"The ledger is inside the archive.")
        if has("stolen-ledger"): raise DomainError(409,"The ledger was already collected.")
        s["inventory"].append("stolen-ledger");why="You possess the evidence and the witnesses' vulnerable identities."
    elif action=="challenge-identity":
        s["guard_beliefs"].pop("royal-courier",None);s["voice_until"]=-1;s["suspicion"]+=30
        why="The guard challenges a contradiction. Borrowed Voice does not make every witness believe you."
    elif action in ("expose","protect"):
        if not has("stolen-ledger"): raise DomainError(409,"Recover the ledger before choosing its fate.")
        if action=="expose":
            if not has("forgery-evidence"): raise DomainError(409,"Public exposure requires corroborating evidence.")
            s["outcome"]="truth-exposed";s["reputation"]["court"]-=2
            s["reputation"]["market"]+= -2 if s["promise"] else 1
            why="The forgery is exposed, but the named witnesses face retaliation."
            if s["promise"]: why+=" You also broke your protection promise."
        else:
            s["outcome"]="witnesses-protected";s["reputation"]["market"]+=2
            why="Witness identities remain hidden; the court's public history is still uncorrected."
    elif action=="wait": why="Time passes; an accepted disguise and a decoy are temporary."
    s["suspicion"]=min(100,max(0,s["suspicion"]))
    if s["suspicion"]>=100 and not s["outcome"]: s["outcome"]="detained";why+=" Suspicion reaches the detention threshold."
    s["events"].append({"turn":t,"action":action,"why":why})
    return s

def replay(actions):
    s=initial()
    for action in actions:s=step(s,action)
    return s
