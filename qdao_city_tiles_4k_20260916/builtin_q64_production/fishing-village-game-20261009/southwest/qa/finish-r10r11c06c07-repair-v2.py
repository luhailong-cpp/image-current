import sys
sys.dont_write_bytecode=True
import json,hashlib,importlib.util
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa';N=Z/'native';PRE='block2x2-r10r11c06c07-v2'
def ref(p):p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def mod(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def png(name,a):
 p=Q/(PRE+'-'+name+'.png');assert not p.exists();Image.fromarray(a).save(p);return {**ref(p),'size':[a.shape[1],a.shape[0]]}
def npy(name,a):
 p=Q/(PRE+'-'+name+'.npy');assert not p.exists();np.save(p,a,allow_pickle=False);return ref(p)
def write(p,a):assert not p.exists();p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return ref(p)
p=mod('record_local',Z/'production.py');orig=p.write;p.write=lambda path,obj:None if path.name=='progress.json' else orig(path,obj);p.record('r11_c07_north_rail_repair_v1')
tpath=Q/'block2x2-r10r11c06c07-v1-trace.json';t=read(tpath);base=rgb(t['context']['path']);out=base.copy();box=[7168,3740,8422,4994];l,y,r,b=box
source=rgb(Q/'r11_c07-north-rail-repair-v1-source-native.png');repair=rgb(N/'r11_c07_north_rail_repair_v1.png');assert repair.shape==(1254,1254,3) and np.array_equal(source,base[y:b,l:r])
c=mod('mask',Q/'repair-compose.py');h=mod('seam',Z/'tools/seam_helpers.py');mask,paths=c.closed_mask(source,repair,[140,440,1254,760],45,box,h._minimum_vertical_seam);sel=mask.astype(bool);out[y:b,l:r][sel]=repair[sel];assert np.array_equal(out[y:b,l:r][~sel],source[~sel])
ids=np.load(t['sourceIds']['path']);ids[y:b,l:r][sel]=3
result={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_candidate_pending_visual_qa','baseTrace':ref(tpath),'globalContextBox':t['globalContextBox'],'provenance':t['provenance']+[ref(tpath),ref(N/'r11_c07_north_rail_repair_v1.png.generation.json')],'context':png('context-native',out),'sourceIds':npy('source-ids',ids),'sourceLegend':{'0':'original top joint','1':'original southwest','2':'original southeast','3':'native rail repair'},'repair':{'source':ref(Q/'r11_c07-north-rail-repair-v1-source-native.png'),'native':ref(N/'r11_c07_north_rail_repair_v1.png'),'contextBox':box,'repairBounds':[140,440,1254,760],'margin':45,'mask':npy('rail-mask',mask),'hardMaskPaths':paths,'after':png('rail-after-100pct',out[y:b,l:r])},'tiles':[],'qa':[],'sharedC06Deltas':[],'validation':{'allFinalPixelsMatchNativeSource':True,'nativePixelsResampled':False,'noFeather':True,'noColorCorrection':True},'formalAcceptedCount':0}
for idx,item in enumerate(t['tiles']):
 x0=4096*(idx%2);y0=4096*(idx//2);ctx=out[y0:y0+4326,x0:x0+4326];core=ctx[115:4211,115:4211]
 cand=ref(item['path']) if np.array_equal(core,rgb(item['path'])) else png(item['tile']+'-candidate-4096',core)
 result['tiles'].append({'tile':item['tile'],'context':png(item['tile']+'-context-native',ctx),'candidate':{**cand,'size':[4096,4096]},'contextBox':[x0,y0,x0+4326,y0+4326],'coreBox':[x0+115,y0+115,x0+4211,y0+4211]})
 if item['tile'].endswith('c06'):
  prior=Q/('pair-r10r11c06-final-v5-'+item['tile']+'-context-native.png');old=rgb(prior);diff=np.any(ctx!=old,axis=2);ys,xs=np.where(diff)
  result['sharedC06Deltas'].append({'tile':item['tile'],'comparisonBase':ref(prior),'updatedContext':result['tiles'][-1]['context'],'changedMask':npy(item['tile']+'-delta-mask',diff),'changedPixels':int(diff.sum()),'contextBBox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'coreChangedPixels':int(diff[115:4211,115:4211].sum()),'west3840ColumnsUnchanged':not bool(diff[:,:3840].any())})
for item in t['qa']:
 a,b,c,d=item['contextBox'];old=rgb(item['path']);current=out[b:d,a:c];same=np.array_equal(old,current)
 result['qa'].append({**item,**({} if same else png(item['edge']+'-'+str(item.get('part','junction'))+'-100pct',current)),'unchangedFromV1':same})
print(json.dumps({'trace':write(Q/(PRE+'-trace.json'),result),'deltas':result['sharedC06Deltas'],'changedQA':[v['path'] for v in result['qa'] if not v['unchangedFromV1']]}))
