import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent;N=Z/'native'
def ref(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def save(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False)
 return ref(p)
def png(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(rgb(p),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pre='block2x2-r08r09c05c06-v3';basepath=Q/'block2x2-r08r09c05c06-v2-trace.json';t=read(basepath)
assert ref(t['context']['path'])['sha256']==t['context']['sha256'];base=rgb(t['context']['path']);out=base.copy();ids=np.zeros(base.shape[:2],np.uint8)
c=mod('r08c05mask',Q/'repair-compose.py');h=mod('r08c05seam',Z/'tools/seam_helpers.py');jobs=[read(Q/'r08c05-block-repair-jobs-v1.json')[1]]+read(Q/'r08c05-block-repair-jobs-qr-v1.json')
bounds=[[0,0,1254,1254],[325,515,510,675],[205,230,625,1040]];margins=[12,25,40]
repairs=[]
for i,(j,b,margin) in enumerate(zip(jobs,bounds,margins),1):
 stem=j['stem'];box=j['coordinates']['contextBox'];l,top,r,bottom=box;source=Path(j['submittedParameters']['referenced_image_paths'][0]);repair=N/(stem+'.png');gen=N/(stem+'.png.generation.json');new=rgb(repair)
 assert new.shape==(1254,1254,3) and read(gen)['sha256']==ref(repair)['sha256'];assert ref(j['coordinates']['sourceContext']['path'])['sha256']==j['coordinates']['sourceContext']['sha256'];submitted=Image.open(j['coordinates']['sourceContext']['path']).convert('RGB');assert np.array_equal(rgb(source),np.array(submitted.crop(box)))
 old=out[top:bottom,l:r].copy();mask,paths=c.closed_mask(old,new,b,margin,box,h._minimum_vertical_seam);sel=mask.astype(bool)
 out[top:bottom,l:r][sel]=new[sel];ids[top:bottom,l:r][sel]=i
 mp=Q/(pre+'-'+stem+'-mask.npy');assert not mp.exists();np.save(mp,mask,allow_pickle=False)
 repairs.append({'id':stem,'source':ref(source),'repair':ref(repair),'generationRecord':ref(gen),'request':ref(N/(stem+'.request.json')),'contextBox':box,'repairBounds':b,'margin':margin,'mask':ref(mp),'paths':paths})
assert np.array_equal(out[ids==0],base[ids==0])
for i,j in enumerate(jobs,1):
 l,top,r,bottom=j['coordinates']['contextBox'];sel=ids[top:bottom,l:r]==i
 assert np.array_equal(out[top:bottom,l:r][sel],rgb(N/(j['stem']+'.png'))[sel]);assert (ids==i).sum()==sel.sum()
for a in repairs:
 l,top,r,bottom=a['contextBox'];a['after']=png(Q/(pre+'-'+a['id']+'-after-100pct.png'),out[top:bottom,l:r])
result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_four_block_repaired_pending_visual_qa','baseTrace':ref(basepath),'baseContext':t['context'],'globalContextBox':t['globalContextBox'],'script':ref(__file__),'method':'native AI source pixel choice with closed minimum-error hard masks; sequential overlapping masks documented','repairs':repairs,'context':png(Q/(pre+'-context-native.png'),out),'tiles':[],'qa':[],'nativePixelsResampled':False,'sourcePixelIdentity':True,'formalAcceptedCount':0,'validation':{'allFinalPixelsExactlyMatchBaseOrRecordedNativeSource':True,'allSavedPixelsVerified':True}}
idp=Q/(pre+'-repair-source-ids.npy');assert not idp.exists();np.save(idp,ids,allow_pickle=False);result['repairSourceIds']=ref(idp)
for tid,x,y in [('r08_c05',0,0),('r08_c06',4096,0),('r09_c05',0,4096),('r09_c06',4096,4096)]:
 result['tiles'].append({'tile':tid,'context':png(Q/(pre+'-'+tid+'-context-native.png'),out[y:y+4326,x:x+4326]),'contextBox':[x,y,x+4326,y+4326],'candidate':png(Q/(pre+'-'+tid+'-candidate-4096.png'),out[y+115:y+4211,x+115:x+4211]),'coreBox':[x+115,y+115,x+4211,y+4211]})
for a in t['qa']:
 l,top,r,bottom=a['contextBox'];ar=out[top:bottom,l:r];label=a['edge']+('-'+str(a['part']) if 'part' in a else '')
 result['qa'].append({'edge':a['edge'],'part':a.get('part'),'contextBox':a['contextBox'],'unchangedFromBase':bool(np.array_equal(ar,base[top:bottom,l:r])),**png(Q/(pre+'-'+label+'-100pct.png'),ar)})
tr=save(Q/(pre+'-trace.json'),result);print(json.dumps({'trace':tr,'tiles':result['tiles']}))
