"""Native two-tile joining with horizontal or vertical neighbors."""
import sys
sys.dont_write_bytecode=True
import argparse,json,hashlib,importlib.util,re
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent;QA=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def verify(r):
 p=Path(r['path']);assert p.is_file() and sha(p)==r['sha256'];return p
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--manifest',required=True);args=parser.parse_args()
 m=read(args.manifest);pre=m['outputPrefix'];assert re.fullmatch(r'pair-[a-z0-9_-]+',pre)
 assert not list(QA.glob(pre+'-*')),'Output prefix used'
 refs=m['inputs'];assert len(refs)==2
 coords=[list(map(int,re.fullmatch(r'r(\d+)_c(\d+)',v['tile']).groups())) for v in refs]
 vertical=coords[1]==[coords[0][0]+1,coords[0][1]]
 assert vertical or coords[1]==[coords[0][0],coords[0][1]+1],'Not adjacent'
 arr=[]
 for r in refs:
  with Image.open(verify(r['context'])) as im:
   assert im.size==(4326,4326)
   if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
   arr.append(np.array(im.convert('RGB')))
 for r in m['provenance']:verify(r)
 helper=Z/'tools/seam_helpers.py';sp=importlib.util.spec_from_file_location('pair_seam',helper);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 a,b=arr
 if vertical:a=a.transpose(1,0,2);b=b.transpose(1,0,2)
 path=mod._minimum_vertical_seam(a[:,-230:],b[:,:230]);assert len(path)==4326 and path.min()>=0 and path.max()<230
 mask=np.arange(230)[None,:]>=path[:,None]
 out=np.concatenate([a[:,:4096],np.where(mask[:,:,None],b[:,:230],a[:,-230:]),b[:,230:]],axis=1)
 ids=np.zeros((4326,8422),np.uint8);ids[:,4096:4326]=mask.astype(np.uint8);ids[:,4326:]=1
 assert np.array_equal(out[:,:4326][ids[:,:4326]==0],a[ids[:,:4326]==0])
 assert np.array_equal(out[:,4096:][ids[:,4096:]==1],b[ids[:,4096:]==1])
 if vertical:out=out.transpose(1,0,2);ids=ids.T
 def png(s,ar):
  p=QA/(pre+'-'+s+'.png');Image.fromarray(ar).save(p);return {**ref(p),'size':[ar.shape[1],ar.shape[0]]}
 ox,oy=(coords[0][1]-1)*4096-115,(coords[0][0]-1)*4096-115
 t={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_pair_pending_visual_qa','inputs':refs,'provenance':m['provenance'],'axis':'vertical' if vertical else 'horizontal','globalContextBox':[ox,oy,ox+out.shape[1],oy+out.shape[0]],'manifest':ref(args.manifest),'script':ref(__file__),'helper':ref(helper),'hardSeamPathIn230Overlap':path.tolist(),'sourcePixelIdentity':True,'nativePixelsResampled':False,'context':png('context-native',out),'tiles':[],'qa':[],'repairTargets':[],'formalAcceptedCount':0}
 npy=QA/(pre+'-source-ids.npy');np.save(npy,ids,allow_pickle=False);t['sourceIds']=ref(npy)
 for i,r in enumerate(refs):
  x=0 if vertical else i*4096;y=i*4096 if vertical else 0
  t['tiles'].append({'tile':r['tile'],'context':png(r['tile']+'-context-native',out[y:y+4326,x:x+4326]),'contextBox':[x,y,x+4326,y+4326],'candidate':png(r['tile']+'-candidate-4096',out[y+115:y+4211,x+115:x+4211]),'coreBox':[x+115,y+115,x+4211,y+4211]})
 for part,start in enumerate([0,800,1600,2400,3196],1):
  box=[115+start,3866,1015+start,4556] if vertical else [3866,115+start,4556,1015+start]
  l,top,r,bottom=box
  t['qa'].append({**png(f'shared-part{part:02d}-100pct',out[top:bottom,l:r]),'contextBox':box,'globalBox':[l+ox,top+oy,r+ox,bottom+oy]})
 for v in m.get('repairTargets',[]):
  assert re.fullmatch(r'[a-z0-9_-]+',v['id'])
  box=[x+115 for x in v['tileContextBox']];l,top,r,bottom=box
  assert r-l==1254 and bottom-top==1254 and 0<=l<r<=out.shape[1] and 0<=top<bottom<=out.shape[0]
  t['repairTargets'].append({**v,'contextBox':box,'globalContextBox':[l+ox,top+oy,r+ox,bottom+oy],'source':png(v['id']+'-source-native',out[top:bottom,l:r])})
 for r in refs:verify(r['context'])
 p=QA/(pre+'-trace.json');p.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'trace':ref(p),'context':t['context'],'tiles':t['tiles'],'qaCount':len(t['qa'])}))
if __name__=='__main__':main()

