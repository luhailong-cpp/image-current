"""Private deterministic delivery export. No pose synthesis or per-frame alignment."""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageFilter
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(source,dest):
    source=Path(source).resolve(); dest=Path(dest).resolve()
    if ROOT not in dest.parents: raise ValueError('Destination outside character directory')
    im=Image.open(source).convert('RGBA'); native=im.size
    if min(native)<1024: raise ValueError('Native frame below 1024')
    if native[0]!=native[1]: raise ValueError('Expected square frame; no automatic crop')
    a=np.asarray(im).copy(); alpha=a[:,:,3].copy()
    # Only very saturated chroma-matte colours within four native pixels of alpha edge.
    rgb=a[:,:,:3].astype(int); r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    opaque=(alpha>8).astype(np.uint8)*255
    inside=np.asarray(Image.fromarray(opaque).filter(ImageFilter.MinFilter(9)))>0
    neon=(((b>180)&(r<100)&(g<100))|((r>180)&(b>180)&(g<70)))&(alpha>0)&~inside
    valid=(alpha>180)&~neon
    replaced=0
    for y,x in zip(*np.nonzero(neon)):
        y0,y1=max(0,y-8),min(a.shape[0],y+9); x0,x1=max(0,x-8),min(a.shape[1],x+9)
        yy,xx=np.nonzero(valid[y0:y1,x0:x1]);
        if len(xx):
            distances=(yy+y0-y)**2+(xx+x0-x)**2; k=int(distances.argmin())
            a[y,x,:3]=a[yy[k]+y0,xx[k]+x0,:3]; replaced+=1
    assert np.array_equal(alpha,a[:,:,3])
    cleaned=Image.fromarray(a)
    out=cleaned.resize((1024,1024),Image.Resampling.LANCZOS) if native!=(1024,1024) else cleaned
    dest.parent.mkdir(parents=True,exist_ok=True); out.save(dest)
    rec={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'recordedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'mode':'RGBA','format':'PNG','derivedFrom':{'file':source.relative_to(ROOT).as_posix() if ROOT in source.parents else str(source),'sha256':sha(source),'nativeSize':native,'generationRecord':str(source)+'.generation.json'},'operation':{'type':'whole_canvas_downsample','scale':1024/native[0],'translation':[0,0],'noPoseSynthesis':True,'noMirroring':True,'noPerFrameBBoxFitting':True,'noSoleRealignment':True,'edgeColorCleanup':{'method':'neon-only-nearest-clean-colour within alpha boundary band','candidatePixels':int(neon.sum()),'changedPixels':replaced,'alphaUnchangedBeforeResize':True}},'review':{'status':'pending_sequence_review'},'clientStatus':'not_integrated'}
    Path(str(dest)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(dest),'sha256':rec['sha256'],'cleanup':rec['operation']['edgeColorCleanup']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('destination');a=p.parse_args();run(a.source,a.destination)
