import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def mod(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def png(p,a):
 assert not p.exists(),p
 Image.fromarray(a).save(p);return {**ref(p),'dimensions':[a.shape[1],a.shape[0]]}
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return ref(p)
pre='block2x2-r09r10c06c07-v2';basepath=Q/'block2x2-r09r10c06c07-v1-trace.json';t=read(basepath)
assert sha(t['context']['path'])==t['context']['sha256']
base=np.array(Image.open(t['context']['path']).convert('RGB'));out=base.copy();ids=np.zeros(base.shape[:2],np.uint8)
c=mod('mask_for_c07',Q/'repair-compose.py');h=mod('seam_for_c07',Z/'tools/seam_helpers.py');repairs=[]
for i,rid in enumerate(['lamp','grout','notch'],1):
 stem='r10_c07_localrepair_joint_'+rid+'_v1';req=read(Z/f'native/{stem}.request.json');gen=Z/f'native/{stem}.png.generation.json';generation=read(gen);co=req['coordinates'];box=co['contextBox'];l,top,r,bottom=box
 source=Path(req['references'][0]['path']);repair=Z/f'native/{stem}.png';old=np.array(Image.open(source).convert('RGB'));new=np.array(Image.open(repair).convert('RGB'))
 assert np.array_equal(old,base[top:bottom,l:r]) and new.shape==(1254,1254,3) and generation['sha256']==sha(repair)
 bounds=co['repairBounds']
 if rid=='notch':bounds=[580,490,950,880]
 mask,paths=c.closed_mask(old,new,bounds,60,box,h._minimum_vertical_seam);sel=mask.astype(bool)
 assert not ids[top:bottom,l:r][sel].any()
 out[top:bottom,l:r][sel]=new[sel];ids[top:bottom,l:r][sel]=i
 maskpath=Q/(pre+'-'+rid+'-mask.npy');np.save(maskpath,mask,allow_pickle=False)
 repairs.append({'id':rid,'source':ref(source),'repair':ref(repair),'generationRecord':ref(gen),'request':ref(Z/f'native/{stem}.request.json'),'contextBox':box,'repairBounds':bounds,'margin':60,'mask':ref(maskpath),'paths':paths,'after':png(Q/(pre+'-'+rid+'-after-100pct.png'),out[top:bottom,l:r])})
assert np.array_equal(out[ids==0],base[ids==0])
result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_four_block_repaired_pending_visual_qa','baseTrace':ref(basepath),'baseContext':t['context'],'globalContextBox':t['globalContextBox'],'script':ref(__file__),'method':'native imagegen edits selected using four closed minimum-error hard boundaries, no resizing, feathering or color adjustment','repairs':repairs,'context':png(Q/(pre+'-context-native.png'),out),'tiles':[],'qa':[],'haloQA':[],'nativePixelsResampled':False,'formalAcceptedCount':0}
idpath=Q/(pre+'-repair-source-ids.npy');np.save(idpath,ids,allow_pickle=False);result['repairSourceIds']=ref(idpath)
for tid,x,y in [('r09_c06',0,0),('r09_c07',4096,0),('r10_c06',0,4096),('r10_c07',4096,4096)]:
 result['tiles'].append({'tile':tid,'context':png(Q/(pre+'-'+tid+'-context-native.png'),out[y:y+4326,x:x+4326]),'contextBox':[x,y,x+4326,y+4326],'candidate':png(Q/(pre+'-'+tid+'-candidate-4096.png'),out[y+115:y+4211,x+115:x+4211]),'coreBox':[x+115,y+115,x+4211,y+4211]})
for a in t['qa']:
 l,top,r,bottom=a['contextBox'];ar=out[top:bottom,l:r];label=a['edge']+('-'+str(a['part']) if 'part' in a else '')
 result['qa'].append({'edge':a['edge'],'part':a.get('part'),'contextBox':a['contextBox'],'unchangedFromBase':bool(np.array_equal(ar,base[top:bottom,l:r])),**png(Q/(pre+'-'+label+'-100pct.png'),ar)})
for label,box in [('north-halo',[3866,0,4556,900]),('south-halo',[3866,7522,4556,8422]),('west-halo',[0,3866,900,4556]),('east-halo',[7522,3866,8422,4556])]:
 l,top,r,bottom=box;result['haloQA'].append({'edge':label,'contextBox':box,**png(Q/(pre+'-'+label+'-100pct.png'),out[top:bottom,l:r])})
tr=write(Q/(pre+'-trace.json'),result)
print(json.dumps({'trace':tr,'context':result['context'],'tiles':result['tiles'],'modifiedQA':[a['edge']+'-'+str(a['part']) for a in result['qa'] if not a['unchangedFromBase']]}))
