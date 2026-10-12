import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib,datetime
import numpy as np
z=Path(__file__).resolve().parents[1];q=z/'qa';ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
old=q/'block2x2-r09r10c05c06-v1-r09_c06-context-native.png';new=q/'block2x2-r09r10c06c07-v2-r09_c06-context-native.png';ours=q/'pair-r08c06-r09c06-v5-r09_c06-context-native.png'
assert ref(old)['sha256']=='7cda883269fefa3b54c32a6c6720b97fe3c04710ba94a98b632aef9253839e55'
assert ref(new)['sha256']=='cb6a2b2af0f72f45e45e87a2dff36cb21251f66300cea074e118690f1ac74903'
a,b,c=[np.array(Image.open(p).convert('RGB')) for p in (old,new,ours)];mask=np.any(c!=a,axis=2)
assert np.array_equal(b[mask],a[mask]),'Our north edits conflict with new joint'
out=b.copy();out[mask]=c[mask];assert np.array_equal(out[~mask],b[~mask]);assert np.array_equal(out[mask],c[mask])
p=q/'r08c06-south-v5-rebased-r09_c06-context-native.png';assert not p.exists();Image.fromarray(out).save(p)
mp=q/'r08c06-south-v5-rebased-r09_c06-change-mask.npy';assert not mp.exists();np.save(mp,mask.astype(np.uint8),allow_pickle=False)
ys,xs=np.where(mask);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
t={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oldBase':ref(old),'latestBase':ref(new),'northEditedContext':ref(ours),'context':ref(p),'selectionMask':ref(mp),'maskLegend':{'0':'latest base','1':'north edited context'},'changedPixels':int(mask.sum()),'changedContextBox':box,'allLatestBasePixelsWithinSelectionEqualOldBase':True,'allFinalPixelsMatchRecordedSource':True,'noResample':True,'preservedLatestSouthernChanges':True,'provenance':[ref(q/'pair-r08c06-r09c06-v5-trace.json'),ref(q/'block2x2-r09r10c06c07-v2-trace.json')]}
tp=q/'r08c06-south-v5-rebased-r09_c06-trace.json';assert not tp.exists();tp.write_text(json.dumps(t,indent=2),encoding='utf-8')
east=q/'block2x2-r09r10c06c07-v2-r09_c07-context-native.png';assert ref(east)['sha256']=='0e89b7285595d5f1de2c7c5b000dc6f88ab895cbdb15e8e2c4c7bba4d01ed537'
m={'outputPrefix':'pair-r09c06-c07-northupdate-v1','inputs':[{'tile':'r09_c06','context':ref(p)},{'tile':'r09_c07','context':ref(east)}],'provenance':[ref(tp),ref(q/'block2x2-r09r10c06c07-v2-trace.json')]}
mfile=q/(m['outputPrefix']+'.manifest.json');assert not mfile.exists();mfile.write_text(json.dumps(m,indent=2),encoding='utf-8');print(json.dumps(t))

