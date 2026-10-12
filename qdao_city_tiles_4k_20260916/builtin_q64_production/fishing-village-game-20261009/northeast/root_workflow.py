import argparse,json,uuid
from pathlib import Path
from PIL import Image
import north_extension as north
import r06_c14_extension as base
Z=Path(__file__).resolve().parent
def atomic(p,d):
 p=Path(p); t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
def select(p,v,note):
 f=Z/'native'/f'{p}-{v}.png';a=Image.open(f);assert a.size==(1254,1254)
 planp=Z/'records'/f'{p}-{v}.plan.json'
 if not planp.exists():planp=Z/'records'/f'{p}.plan.json'
 plan=json.loads(planp.read_text()); sides=[e['role'].replace('exact_native_','').replace('_230px','') for e in plan['nativeEdgeSources']]
 review={'reviewedAtUtc':base.now(),'fullOutputViewed':True,'nativeSeamsViewed':sides,'nativeSize':list(a.size),'sha256':base.sha(f),'provisionallySelected':True,'observations':note,'formalAccepted':False}
 atomic(Z/'qa'/f'{p}-{v}.root-review.json',review)
 q=Z/'records'/f'{p[:7]}.working-selection.json';d=json.loads(q.read_text(encoding='utf-8-sig'));d[p]=f.name;atomic(q,d)
def rightprep(p):
 north.prep(p)
 planp=Z/'records'/f'{p}.plan.json';d=json.loads(planp.read_text());r=int(p[-2]);versions={1:'v2',2:'v3',3:'v4',4:'v3'}
 f=Z/'native'/f'r05_c13_p{r}1-{versions[r]}.png'
 pins={1:'a9cb502262869fd20a8050de8f0b26abf5a4cb25a909dcb0fb1a914bfdc4441b',2:'e1c1249087771f495501324c33352d3d399a8386fc26bc4e56ea5599b826d574',3:'15a2382c95faa9279fc5a4625e79eb4d7376e1f90968e883b686ec0f3c509976',4:'2b4b0ff800a83dc633ab17ed8c3213565dbfdddd542c64f5d9515de52c4b63f7'}
 assert base.sha(f)==pins[r];im=Image.open(d['references'][3]['path']).convert('RGB');a=Image.open(f).convert('RGB');assert a.size==(1254,1254)
 im.paste(a.crop((0,0,230,1254)),(1024,0))
 bottom=next(e for e in d['nativeEdgeSources'] if 'bottom' in e['role']);b=Image.open(bottom['path']).convert('RGB');im.paste(b.crop((0,0,1254,230)),(0,1024))
 gp=Z/'guides'/f'{p}.three-edge-layout-v1.png';assert not gp.exists();im.save(gp)
 rr=base.ref(f,'exact_native_right_230px');rr.update({'cropBox':[0,0,230,1254],'pasteAt':[1024,0]});d['nativeEdgeSources'].append(rr)
 d['references'][3]=base.ref(gp,'exact local guide with left bottom and right native geometry constraints');d['guideCornerOwnership']='bottom owns lower corners';atomic(planp,d)
 atomic(str(gp)+'.derived.json',{'purpose':'generation geometry guide only; never final pixels','operation':'opaque native crop/paste onto prior layout guide; right then bottom owns lower corner','coordinates':d['coordinates'],'sources':[base.ref(Z/'guides'/f'{p}.native-edge-layout.png','prior layout/native guide'),rr,bottom],'finalArt':False})
 print(json.dumps({'guide':str(gp),'plan':str(planp),'right':rr},ensure_ascii=False))
def selection(tile,version):
 d=json.loads((Z/'records'/f'{tile}.working-selection.json').read_text(encoding='utf-8-sig'));keys=[f'{tile}_p{r}{c}' for r in range(1,5) for c in range(1,5)];assert set(d)==set(keys)
 f=Z/'records'/f'{tile}.selection-root-{version}.json';assert not f.exists();atomic(f,{'schemaVersion':1,'tile':tile,'createdAtUtc':base.now(),'status':'explicit_native_candidate_selection_pending_whole_tile_QA','formalAccepted':False,'patches':{p:base.ref(Z/'native'/d[p],'provisionally selected native') for p in keys}});print(str(f))
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('op');q.add_argument('patch');q.add_argument('--version',default='v1');q.add_argument('--note');a=q.parse_args()
 if a.op=='select':select(a.patch,a.version,a.note)
 elif a.op=='rightprep':rightprep(a.patch)
 elif a.op=='selection':selection(a.patch,a.version)
