"""Stitch final top joint and two lower native contexts, preserving every source pixel."""
import sys
sys.dont_write_bytecode=True
import argparse,json,hashlib,importlib.util,re
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent
QA=Z/'qa'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def verify(r):
 p=Path(r['path'])
 assert p.is_file() and sha(p)==r['sha256'],str(p)
 return p
def rgb(r,size):
 p=verify(r)
 with Image.open(p) as im:
  assert im.size==size,(p,im.size,size)
  if im.mode=='RGBA': assert im.getextrema()[3]==(255,255)
  return np.array(im.convert('RGB'))
def main():
 a=argparse.ArgumentParser();a.add_argument('--manifest',required=True);opt=a.parse_args()
 m=read(opt.manifest);pre=m['outputPrefix'];assert re.fullmatch(r'block2x2-[A-Za-z0-9_-]+',pre),'Use a simple output prefix inside qa'
 assert not list(QA.glob(pre+'-*')),'Choose fresh output prefix'
 helper=Z/'tools/seam_helpers.py'
 spec=importlib.util.spec_from_file_location('native_hard_seam',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 top=rgb(m['topJoint'],(8422,4326));left=rgb(m['southwest'],(4326,4326));right=rgb(m['southeast'],(4326,4326))
 for p in m['provenance']: verify(p)
 v=mod._minimum_vertical_seam(left[:,-230:],right[:,:230])
 assert v.shape==(4326,) and np.issubdtype(v.dtype,np.integer) and np.all((0<=v)&(v<230))
 vm=np.arange(230)[None,:]>=v[:,None]
 bottom=np.empty((4326,8422,3),dtype=np.uint8)
 bottom[:,:4096]=left[:,:4096];bottom[:,4096:4326]=np.where(vm[:,:,None],right[:,:230],left[:,-230:]);bottom[:,4326:]=right[:,230:]
 bid=np.ones((4326,8422),dtype=np.uint8);bid[:,4096:4326]=np.where(vm,2,1);bid[:,4326:]=2
 h=mod._minimum_vertical_seam(np.transpose(top[-230:],(1,0,2)),np.transpose(bottom[:230],(1,0,2)))
 assert h.shape==(8422,) and np.issubdtype(h.dtype,np.integer) and np.all((0<=h)&(h<230))
 hm=np.arange(230)[:,None]>=h[None,:]
 canvas=np.empty((8422,8422,3),dtype=np.uint8);ids=np.zeros((8422,8422),dtype=np.uint8)
 canvas[:4096]=top[:4096];canvas[4096:4326]=np.where(hm[:,:,None],bottom[:230],top[-230:]);canvas[4326:]=bottom[230:]
 ids[4096:4326]=np.where(hm,bid[:230],0);ids[4326:]=bid[230:]
 assert np.array_equal(canvas[:4326][ids[:4326]==0],top[ids[:4326]==0])
 assert np.array_equal(canvas[4096:,:4326][ids[4096:,:4326]==1],left[ids[4096:,:4326]==1])
 assert np.array_equal(canvas[4096:,4096:][ids[4096:,4096:]==2],right[ids[4096:,4096:]==2])
 def png(name,arr):
  p=QA/(pre+'-'+name+'.png');Image.fromarray(arr).save(p);return {**ref(p),'dimensions':[arr.shape[1],arr.shape[0]]}
 trace={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_2x2_candidate_pending_visual_qa','manifest':ref(opt.manifest),'sources':{k:m[k] for k in ['topJoint','southwest','southeast']},'provenance':m['provenance'],'globalContextBox':[12173,32653,20595,41075],'nativePixelsResampled':False,'hardSourceChoice':True,'sourcePixelIdentity':True,'sourceIdLegend':{'0':'topJoint','1':'southwest','2':'southeast'},'helper':ref(helper),'script':ref(__file__),'verticalBottomSeam':v.tolist(),'horizontalSeam':h.tolist(),'formalAcceptedCount':0}
 trace['context']=png('context-native',canvas)
 p=QA/(pre+'-source-ids.npy');np.save(p,ids,allow_pickle=False);trace['sourceIds']=ref(p)
 trace['tiles']=[]
 for tid,x,y in [('r09_c04',115,115),('r09_c05',4211,115),('r10_c04',115,4211),('r10_c05',4211,4211)]:
  trace['tiles'].append({'tile':tid,**png(tid+'-candidate-4096',canvas[y:y+4096,x:x+4096]),'contextBox':[x,y,x+4096,y+4096]})
 trace['qa']=[]
 for label,ori,x,y in [('north-shared','vertical',4211,115),('south-shared','vertical',4211,4211),('west-shared','horizontal',115,4211),('east-shared','horizontal',4211,4211)]:
  for part,off in enumerate([0,800,1600,2400,3196],1):
   box=[x-345,y+off,x+345,y+off+900] if ori=='vertical' else [x+off,y-345,x+off+900,y+345]
   l,t,r,b=box
   assert 0<=l<r<=8422 and 0<=t<b<=8422,box
   trace['qa'].append({'edge':label,'part':part,**png(label+f'-{part}-100pct',canvas[t:b,l:r]),'contextBox':box,'operation':'integer crop only, native scale'})
 trace['qa'].append({'edge':'central-junction',**png('central-junction-100pct',canvas[3761:4661,3761:4661]),'contextBox':[3761,3761,4661,4661],'operation':'integer crop only, native scale'})
 for k in ['topJoint','southwest','southeast']: verify(m[k])
 p=QA/(pre+'-trace.json');p.write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'trace':ref(p),'context':trace['context'],'tiles':trace['tiles'],'qaCount':len(trace['qa'])}))
if __name__=='__main__':main()

