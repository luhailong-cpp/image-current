"""Independent north-side missing cores. Guides only; no final resampling."""
import json,argparse
from pathlib import Path
from PIL import Image
import root_north_20261012 as n
b=n.b;Z=n.Z
def prep(p,version="v1"):
 tile=p[:7];n.configure(tile);co=b.coords(p);r,c=int(p[-2]),int(p[-1]);d=json.loads((Z/'records'/f'{tile}.working-selection.json').read_text(encoding='utf-8-sig'))
 a=Image.open(b.C['layoutReference']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.north-independent-layout-only.png'
 if pure.exists():assert Image.open(pure).convert("RGB").tobytes()==a.tobytes()
 else:a.save(pure)
 edges=[]
 keys=[(f'{tile}_p{r}{c-1}','left')] if c>1 else []
 if r>1:keys.append((f'{tile}_p{r-1}{c}','top'))
 for k,side in keys:
  if k not in d:
   assert p=="r04_c12_p44" and side=="left","Missing stable anchor "+k
   continue
  f=Z/'native'/d[k];im=Image.open(f).convert('RGB');assert im.size==(1254,1254)
  box=[1024,0,1254,1254] if side=='left' else [0,1024,1254,1254]
  xy=[0,0];a.paste(im.crop(box),xy)
  rr=b.ref(f,'exact_native_'+side+'_230px');rr.update(cropBox=box,pasteAt=xy[:2]);edges.append(rr)
 if p=="r04_c12_p44":
  sf=Z/'records/r05_c12.selection-root-v2.json';f=n.selected(sf,"r05_c12_p14");im=Image.open(f).convert("RGB");a.paste(im.crop((0,0,1254,230)),(0,1024));rr=b.ref(f,"exact_native_bottom_230px");rr.update(cropBox=[0,0,1254,230],pasteAt=[0,1024]);edges.append(rr)
 gp=Z/'guides'/f'{p}.native-independent-edges-{version}.png';assert not gp.exists();a.save(gp)
 n.atomic(str(gp)+'.derived.json',{'purpose':'generation guide only','sources':[b.ref(b.C['layoutReference'],'layout only')]+edges,'operation':'overview bicubic guide plus exact native opaque crop paste, top owns corner','finalArt':False,'coordinates':co})
 refs=[b.ref(b.C['layoutReference'],'full-map layout only'),b.ref(b.C['detailStyleReference'],'material style only'),b.ref(b.C['primaryStyleReference'],'primary style only'),b.ref(gp,'local independent native geometry guide')]
 plan={'patchId':p,'coordinates':co,'createdAtUtc':b.now(),'references':refs,'nativeEdgeSources':edges,'expectedNativeSize':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'deferredNeighbor':'r04_c12_p43 is unpassed; no pixels from it used','status':'new independent coordinate, full tile pending'}
 plan.update(b.config_evidence());pp=Z/'records'/(f'{p}.plan.json' if version=="v1" else f'{p}-{version}.plan.json');assert not pp.exists();n.atomic(pp,plan);print(json.dumps({'guide':str(gp),'coords':co,'edges':edges}))
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('patch');q.add_argument("--version",default="v1");x=q.parse_args();prep(x.patch,x.version)

