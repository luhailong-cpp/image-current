import importlib.util,json,uuid,argparse
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('eastold',Z/'records/r04_c14-current-helper-20261012.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(p):
 co=b.coords(p);r,c=int(p[-2]),int(p[-1]);assert p.startswith('r04_c14_')
 current=json.loads((Z/'records/r04_c14.working-selection.json').read_text(encoding='utf-8-sig'))
 south_name=b.SOUTH[c-1] if r==4 else current.get(f'r04_c14_p{r+1}{c}')
 right_name=current.get(f'r04_c14_p{r}{c+1}') if c<4 else None
 south=Z/'native'/south_name if south_name else None
 right=Z/'native'/right_name if right_name else None
 assert south or right,'At least one selected stable edge is required'
 layout=Image.open(b.C['layoutReference']).convert('RGB');pad=Image.new('RGB',(layout.width+8,layout.height));pad.paste(layout,(0,0));pad.paste(layout.crop((layout.width-1,0,layout.width,layout.height)).resize((8,layout.height)),(layout.width,0))
 a=pad.transform((1254,1254),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.layout-only.png';assert not pure.exists();a.save(pure)
 sources=[]
 for path,side in [(right,'right'),(south,'bottom')]:
  if not path:continue
  n=Image.open(path).convert('RGB');assert n.size==(1254,1254)
  box=[0,0,230,1254] if side=='right' else [0,0,1254,230];at=[1024,0] if side=='right' else [0,1024]
  e=b.ref(path,'exact_native_'+side+'_230px');e.update({'cropBox':box,'pasteAt':at.copy()});sources.append(e);a.paste(n.crop(box),tuple(at))
 gp=Z/'guides'/f'{p}.native-edge-layout.png';assert not gp.exists();a.save(gp)
 refs=[b.ref(b.C['layoutReference'],'full-map layout only'),b.ref(b.C['detailStyleReference'],'independent materials only'),b.ref(b.C['primaryStyleReference'],'primary style only'),b.ref(gp,'exact layout with native bottom/right constraints')]
 plan={'patchId':p,'createdAtUtc':b.now(),'coordinates':co,'references':refs,'nativeEdgeSources':sources,'pendingExternalBoundary':'west not generated, p41 failure not propagated','expectedNativeSize':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'formalAccepted':False,'preGenerationRootInstructionsSha256':b.sha(Path('D:/work/image/AGENTS.md')),'coordinateSplitSha256':b.sha(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json'))}
 write(Z/'records'/f'{p}.plan.json',plan);write(Path(str(gp)+'.derived.json'),{'purpose':'guidance only, never final pixels','operation':'layout enlargement plus integer native strips','nativeEdgeSources':sources,'coordinates':co});print(json.dumps(plan))
def select(p,v,note):
 dst=Z/'native'/f'{p}-{v}.png';assert dst.exists();qp=Z/'qa'/f'{p}-{v}.east-resume-review.json'
 write(qp,{'patchId':p,'source':b.ref(dst,'native candidate'),'reviewer':'/root/east_resume','reviewedAtUtc':b.now(),'quickLayoutAndNeighborReview':'pass','note':note,'tileInternalReview':'pending until all16','formalAccepted':False})
 target=Z/'records/r04_c14.working-selection.json';d=json.loads(target.read_text(encoding='utf-8-sig'));d[p]=dst.name;temp=target.with_suffix('.'+uuid.uuid4().hex+'.tmp');temp.write_text(json.dumps(d,indent=2)+'\n');temp.replace(target);print(p+' selected')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('op');a.add_argument('patch');a.add_argument('--source');a.add_argument('--version',default='v1');a.add_argument('--note');q=a.parse_args()
 if q.op=='prepare':prepare(q.patch)
 elif q.op=='ingest':b.ingest(q.patch,q.source,q.version)
 elif q.op=='select':select(q.patch,q.version,q.note)
