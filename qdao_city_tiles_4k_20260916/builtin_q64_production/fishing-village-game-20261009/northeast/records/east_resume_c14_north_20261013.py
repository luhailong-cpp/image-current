import importlib.util,json,uuid,argparse,re
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('eastold',Z/'records/r04_c14-current-helper-20261012.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def selection(t):
 f=Z/'records'/f'{t}.working-selection.json'
 return json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {}
def coords(p):
 m=re.fullmatch(r'(r0[123]_c14)_p([1-4])([1-4])',p);assert m,p
 t,r,c=m.group(1),int(m.group(2)),int(m.group(3));tr=int(t[1:3]);x=53248+(c-1)*1024;y=(tr-1)*4096+(r-1)*1024;box=[x-115,y-115,x+1139,y+1139]
 return t,r,c,{'id':p,'coreGlobalBox':[x,y,x+1024,y+1024],'nativeGlobalBox':box,'overviewBox':[v*1254/57344 for v in box],'expectedSize':[1254,1254],'nativeCoreBox':[115,115,1139,1139]}
def prepare(p):
 t,r,c,co=coords(p);cur=selection(t);assert p not in cur
 below=f'r{int(t[1:3])+1:02d}_c14'
 sn=selection(below).get(f'{below}_p1{c}') if r==4 else cur.get(f'{t}_p{r+1}{c}')
 rn=cur.get(f'{t}_p{r}{c+1}') if c<4 else None
 assert sn or rn,'No stable neighbor'
 layout=Image.open(b.C['layoutReference']).convert('RGB');w,h=layout.size
 pad=Image.new('RGB',(w+16,h+16));pad.paste(layout,(8,8))
 pad.paste(layout.crop((0,0,1,h)).resize((8,h)),(0,8));pad.paste(layout.crop((w-1,0,w,h)).resize((8,h)),(w+8,8))
 pad.paste(pad.crop((0,8,w+16,9)).resize((w+16,8)),(0,0));pad.paste(pad.crop((0,h+7,w+16,h+8)).resize((w+16,8)),(0,h+8))
 a=pad.transform((1254,1254),Image.Transform.EXTENT,[v+8 for v in co['overviewBox']],Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.layout-only.png';assert not pure.exists();a.save(pure)
 edges=[]
 for name,side in [(rn,'right'),(sn,'bottom')]:
  if not name:continue
  path=Z/'native'/name;n=Image.open(path).convert('RGB');assert n.size==(1254,1254)
  box=[0,0,230,1254] if side=='right' else [0,0,1254,230];at=[1024,0] if side=='right' else [0,1024]
  e=b.ref(path,'exact_native_'+side+'_230px');e.update(cropBox=box,pasteAt=at);edges.append(e);a.paste(n.crop(box),tuple(at))
 gp=Z/'guides'/f'{p}.native-edge-layout.png';assert not gp.exists();a.save(gp)
 refs=[b.ref(b.C['layoutReference'],'full-map layout only'),b.ref(b.C['detailStyleReference'],'independent materials only'),b.ref(b.C['primaryStyleReference'],'primary style only'),b.ref(gp,'exact target layout with native edge anchors')]
 plan={'patchId':p,'createdAtUtc':b.now(),'coordinates':co,'references':refs,'nativeEdgeSources':edges,'pendingExternalBoundary':'north and west pending; east world edge where applicable','expectedNativeSize':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'formalAccepted':False,'preGenerationRootInstructionsSha256':b.sha(Path('D:/work/image/AGENTS.md')),'coordinateSplitSha256':b.sha(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json'))}
 write(Z/'records'/f'{p}.plan.json',plan);write(Path(str(gp)+'.derived.json'),{'purpose':'guidance only, never final pixels','operation':'layout crop/enlargement plus native1:1 edge strips','coordinates':co,'nativeEdgeSources':edges})
 print(json.dumps({'patchId':p,'nativeGlobalBox':co['nativeGlobalBox'],'anchors':[q['path'] for q in edges],'guide':str(gp)}))
def select(p,v,note):
 t,r,c,co=coords(p);dst=Z/'native'/f'{p}-{v}.png';assert dst.exists()
 write(Z/'qa'/f'{p}-{v}.east-resume-review.json',{'patchId':p,'source':b.ref(dst,'native candidate'),'reviewer':'/root/east_resume','reviewedAtUtc':b.now(),'quickLayoutAndNeighborReview':'pass','note':note,'tileInternalReview':'pending until all16','formalAccepted':False})
 path=Z/'records'/f'{t}.working-selection.json';d=selection(t);d[p]=dst.name;tmp=path.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(path);print(p+' selected')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('op');a.add_argument('patch');a.add_argument('--source');a.add_argument('--version',default='v1');a.add_argument('--note');q=a.parse_args()
 if q.op=='prepare':prepare(q.patch)
 elif q.op=='ingest':b.ingest(q.patch,q.source,q.version)
 elif q.op=='select':select(q.patch,q.version,q.note)

