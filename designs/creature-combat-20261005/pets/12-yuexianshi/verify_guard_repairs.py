"""Reproducible shoe-support measurements and edge checks; no image changes."""
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
def read(path):return json.loads(path.read_text(encoding="utf-8-sig"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def components(mask):
    pending=set(zip(*np.nonzero(mask)));out=[]
    while pending:
        first=pending.pop();q=deque([first]);pixels=[first]
        while q:
            y,x=q.popleft()
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    at=(y+dy,x+dx)
                    if at in pending:pending.remove(at);q.append(at);pixels.append(at)
        if len(pixels)>=500:
            a=np.array(pixels);out.append({"pixels":len(pixels),"centroid":[round(float(a[:,1].mean()),4),round(float(a[:,0].mean()),4)],"bbox":[int(a[:,1].min()),int(a[:,0].min()),int(a[:,1].max())+1,int(a[:,0].max())+1]})
    return sorted(out,key=lambda x:x["centroid"][0])
def w_measure(path):
    with Image.open(path) as im:a=np.asarray(im.convert("RGBA"))
    y,x=np.indices(a.shape[:2])
    mask=(x>=280)&(x<605)&(y>=850)&(y<970)&(a[:,:,3]>150)&(a[:,:,:3].max(2)<185)
    cs=components(mask)
    return cs[0] if cs else None
def e_measure(path):
    with Image.open(path) as im:a=np.asarray(im.convert("RGBA"))
    y,x=np.indices(a.shape[:2]);out=[]
    for lo,hi in [(450,610),(610,850)]:
        yy,xx=np.nonzero((y>=890)&(x>=lo)&(x<hi)&(a[:,:,3]>150)&(a[:,:,:3].max(2)<185))
        out.append({"pixels":len(xx),"centroid":[round(float(xx.mean()),4),round(float(yy.mean()),4)]})
    return out
def main():
    prior_path=ROOT/"records/guardfix-20261008-measurements.json"
    prior=read(prior_path) if prior_path.exists() else {}
    prior_edges={entry["file"]:entry for entry in prior.get("nativeEdges",[])}
    baseline=w_measure(ROOT/"runtime/cast/W/16.png")
    w=[];native=[]
    for action,count in [("hit",6),("attack",12)]:
        for index in range(1,count+1):
            file=f"runtime/{action}/W/{index:02}.png";path=ROOT/file
            measured=w_measure(path);r=read(ROOT/f"records/{action}-W/{index:02}.generation.json")
            w.append({"file":file,"sha256":sha(path),"measuredScreenLeftShoe":measured,"horizontalDeltaToCast16":round(measured["centroid"][0]-baseline["centroid"][0],4) if measured else None,"guardfixRecorded":"guardfix-20261008" in r.get("prompt","")})
    e=[]
    for index in [1,2,12]:
        path=ROOT/f"runtime/attack/E/{index:02}.png"
        e.append({"file":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"shoeMeasurements":e_measure(path)})
    for item in [*w,e[0]]:
        parts=Path(item["file"]).parts;action,direction=parts[1:3];num=Path(parts[-1]).stem
        record=read(ROOT/f"records/{action}-{direction}/{num}.generation.json")
        source=Path(record["derivedFrom"]["path"])
        if source.exists():
            with Image.open(source) as im:a=np.asarray(im.convert("RGBA"))[:,:,3]
            edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
            native.append({"file":item["file"],"source":str(source),"sha256":sha(source),"nativeSize":[a.shape[1],a.shape[0]],"edgeMaxAlpha":int(edge.max()),"edgePixelsAlphaAbove64":int((edge>64).sum())})
        elif item["file"] in prior_edges and prior_edges[item["file"]]["sha256"]==record["native"]["sha256"]:
            retained=dict(prior_edges[item["file"]]);retained["verificationTiming"]="Historical native-edge evidence retained after policy cleanup; not rechecked from deleted pixels."
            native.append(retained)
    result={"checkedAt":datetime.now(timezone.utc).isoformat(),"method":"Unchanged 1024 exports. W: ROI x[280,605),y[850,970),alpha>150,maxRGB<185; smallest-x 8-connected component >=500px. E: y>=890,alpha>150,maxRGB<185; x[450,610) and[610,850), unweighted mean.","limits":"Dark-shoe components are not joints; natural pose and perspective affect measurements. Metrics require visual review and do not establish actual playback.","baselineWCast16":baseline,"w":w,"e":e,"nativeEdges":native,"playbackStatus":"not-verified-browser-policy-blocked"}
    (ROOT/"records/guardfix-20261008-measurements.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"repairedW":sum(x["guardfixRecorded"] for x in w),"w": [{"file":x["file"],"dx":x["horizontalDeltaToCast16"]} for x in w],"e":e,"nativeSolidEdgeAttention":[x for x in native if x["edgePixelsAlphaAbove64"]]},ensure_ascii=False))
if __name__=="__main__":main()
