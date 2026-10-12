"""Read-only geometry diagnostics for the three authorized material repairs."""
import json, hashlib, sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SPECS={
"s03_01":[("y",201,0,1254),("y",595,0,1254),("y",957,0,1254),
           ("x",1034,0,201),("x",901,201,595),("x",359,595,957)],
"s03_02":[("y",42,438,1254),("y",202,0,761),("y",594,0,1254),("y",957,0,1254),
           ("x",10,0,202),("x",438,0,202),("x",1120,0,42),("x",761,42,594),("x",351,594,957),("x",710,957,1254)],
"s03_03":[("y",41,0,1254),("y",592,0,1254),("y",957,0,1254),
           ("x",95,0,41),("x",626,0,41),("x",959,41,592)]
}
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mask_components(mask):
    remaining=set(map(tuple,np.argwhere(mask)))
    components=[]
    while remaining:
        stack=[remaining.pop()]; points=[]
        while stack:
            y,x=stack.pop();points.append((y,x))
            for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                n=(y+dy,x+dx)
                if n in remaining: remaining.remove(n);stack.append(n)
        if len(points)>=5:
            p=np.array(points)
            components.append({"pixels":len(points),"boxLTRB":[int(p[:,1].min()),int(p[:,0].min()),int(p[:,1].max()+1),int(p[:,0].max()+1)]})
    return sorted(components,key=lambda c:(c["boxLTRB"][1],c["boxLTRB"][0]))
def run(pid):
    original=ROOT/"native"/(pid+".png")
    edited=ROOT/"native"/(pid+"_material01.png")
    a=np.array(Image.open(original).convert("RGB")).astype(float)
    b=np.array(Image.open(edited).convert("RGB")).astype(float)
    if a.shape!=b.shape or a.shape!=(1254,1254,3): raise ValueError("wrong native geometry")
    gray_a=a.mean(axis=2);gray_b=b.mean(axis=2)
    lines=[]
    for axis,pos,start,end in SPECS[pid]:
        lo=max(0,pos-14);hi=min(1254,pos+15)
        start+=12;end-=12
        if end<=start: continue
        first=gray_a[lo:hi,start:end] if axis=="y" else gray_a[start:end,lo:hi].T
        second=gray_b[lo:hi,start:end] if axis=="y" else gray_b[start:end,lo:hi].T
        path_a=first.argmin(axis=0)+lo;path_b=second.argmin(axis=0)+lo
        shifts=np.abs(path_a-path_b)
        ma=first<180;mb=second<180
        union=np.count_nonzero(ma|mb)
        lines.append({"axis":axis,"approximateOriginalPosition":pos,"sampleRange":[start,end],
                      "originalMedianDarkCenter":float(np.median(path_a)),"editedMedianDarkCenter":float(np.median(path_b)),
                      "medianAbsoluteCenterShift":float(np.median(shifts)),"p95AbsoluteCenterShift":float(np.percentile(shifts,95)),
                      "maxAbsoluteCenterShift":int(shifts.max()),
                      "darkJointMaskIoU":float(np.count_nonzero(ma&mb)/union) if union else None,
                      "originalMedianDarkWidth":float(np.median(ma.sum(axis=0))),
                      "editedMedianDarkWidth":float(np.median(mb.sum(axis=0)))})
    def red(array): return (array[:,:,0]>170)&(array[:,:,0]>array[:,:,1]*1.5)&(array[:,:,0]>array[:,:,2]*1.5)&(array[:,:,1]<160)
    red_a,red_b=red(a),red(b);union=np.count_nonzero(red_a|red_b)
    return {"logicalPatch":pid,"original":{"file":str(original),"sha256":digest(original)},
            "edited":{"file":str(edited),"sha256":digest(edited)},"nativePixels":[1254,1254],
            "joints":lines,"redPaper":{"originalComponents":mask_components(red_a),"editedComponents":mask_components(red_b),
            "redMaskIoU":float(np.count_nonzero(red_a&red_b)/union) if union else None},
            "diagnosticOnly":True,"imagesModifiedByDiagnostic":False,
            "note":"Dark-center profiles and threshold masks are diagnostics, not a promise of pixel-identical generative editing; visual review is recorded separately."}
if __name__=="__main__": print(json.dumps(run(sys.argv[1]),ensure_ascii=False,indent=2))

