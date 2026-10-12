import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
from verify_guard_repairs import w_measure
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=w_measure(ROOT/"runtime/cast/W/16.png")
items=[];errors=[]
for n in range(1,7):
    path=ROOT/f"runtime/hit/W/{n:02}.png"
    record=ROOT/f"records/hit-W/{n:02}.generation.json"
    d=json.loads(record.read_text(encoding="utf-8"));actual=sha(path)
    with Image.open(path) as im:
        size=im.size;mode=im.mode;alpha=im.getchannel("A").getextrema()
    if actual!=d["sha256"]:errors.append(f"{n}: record SHA mismatch")
    if size!=(1024,1024) or mode!="RGBA" or alpha!=(0,255):errors.append(f"{n}: image format")
    native=Path(d["derivedFrom"]["path"])
    with Image.open(native) as im:a=np.asarray(im.convert("RGBA"))[:,:,3]
    edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    measured=w_measure(path)
    items.append({"file":path.relative_to(ROOT).as_posix(),"sha256":actual,"record":record.relative_to(ROOT).as_posix(),"prompt":d["prompt"],"native":str(native),"nativeSha256":sha(native),"nativeSize":[a.shape[1],a.shape[0]],"nativeEdgeMaxAlpha":int(edge.max()),"nativeEdgePixelsAlphaAbove64":int((edge>64).sum()),"shoeMeasurement":measured,"shoeHorizontalDeltaToCast16":round(measured["centroid"][0]-baseline["centroid"][0],4) if measured else None,"staticViewed":True})
if len({x["sha256"] for x in items})!=6:errors.append("duplicated whole-file bytes")
result={"reviewedAt":datetime.now(timezone.utc).isoformat(),"group":"hit-W","status":"repaired-static-reviewed","inspected":"All six exported final frames were actually displayed via view_image; native outputs also visually inspected. Neighbour 01 and02 viewed sequentially; no actual timed playback was seen.","anatomy":"All selected six are genuine rear three-quarter facing upper-left. Exactly two shoes and coherent pair of legs in compact fore/aft stance. Left hand supports crescent harp, right hand stays near strings; two arms/hands; no wings/tail.","action":"01 onset recoil with wide hair sweep;02 protects harp and absorbs;03 peak/rebound with hair/cloth response;04 rises with right hand returning;05 and06 settle near guard. Initial 01/02/04 candidates lost hit-stage upper body and were rejected; root independently repaired02.","support":"Original wide horizontal shoe separation was removed. 01 r4 reduces oversize from r3; small independent pose/foot differences remain and require timed playback assessment. Numeric dark-pixel components are auxiliary, not joints or proof of motion quality.","finalRecovery":"06 returns to narrow fore/aft guard with same two-sole identity as castW16, no wide split stance.","playbackStatus":"not-verified-browser-policy-blocked","baselineWCast16":baseline,"technicalErrors":errors,"frames":items,"imageGenerationRoute":"builtin","actualModel":None,"actualQuality":None,"unknownReason":"Host-managed builtin tool exposes no model/quality selector or returned value.","cleanupList":"records/hit-W/guardfix-20261008-native-cleanup-list.json"}
(ROOT/"records/hit-W/guardfix-20261008-review.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"errors":errors,"shoeDx":[x["shoeHorizontalDeltaToCast16"] for x in items],"solidEdges":[x["file"] for x in items if x["nativeEdgePixelsAlphaAbove64"]]},ensure_ascii=False))

