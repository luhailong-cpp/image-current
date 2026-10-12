from pathlib import Path
import json,hashlib,sys,importlib.util
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(D/'joint-assembly.json');p=read(D/'joint-path.json')
for e in m['inputBaselines']+m['artifacts']+[m['algorithm'],m['script'],m['path']]:assert sha(e['file'])==e['sha256']
arrays={}
for s in m['sources']:
 assert sha(s['file'])==s['sha256'] and sha(s['generationRecord'])==s['generationRecordSha256']
 arrays[s['jointSourceId']]=np.asarray(Image.open(s['file']).convert('RGB'))
total=0
for tile,y,old in [('r03_c03',8192,m['inputBaselines'][0]['file']),('r04_c03',12288,m['inputBaselines'][1]['file'])]:
 a=np.asarray(Image.open(D/f'{tile}.joint-proposal.png'));ids=np.asarray(Image.open(D/f'{tile}.joint-source-id.png'));assert a.shape==(4096,4096,3)
 covered=0
 for s in m['sources']:
  yy,xx=np.nonzero(ids==s['jointSourceId'])
  if not len(xx):continue
  bx,by,_,_=s['globalNativeBox'];sx=xx+8192-bx;sy=yy+y-by
  assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254))
  assert np.array_equal(a[yy,xx],arrays[s['jointSourceId']][sy,sx]);covered+=len(xx)
 assert covered==4096*4096;total+=covered
 base=np.asarray(Image.open(old).convert('RGB'))
 assert np.array_equal(a[:-115],base[:-115]) if tile=='r03_c03' else np.array_equal(a[115:],base[115:])
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def row(tile,y):
 ss=sorted([s for s in m['sources'] if s['tile']==tile and s['globalNativeBox'][1]==y],key=lambda e:e['globalNativeBox'][0]);a=arrays[ss[0]['jointSourceId']];ids=np.full(a.shape[:2],ss[0]['jointSourceId'],np.uint8)
 for s in ss[1:]:a,ids,_=h.append_hard(a,ids,arrays[s['jointSourceId']],np.full((1254,1254),s['jointSourceId'],np.uint8),'check')
 return a,ids
up,ui=row('r03_c03',11149);dn,di=row('r04_c03',12173);a=up[1024:1254];b=dn[:230]
cut,cost=h.minimum_vertical_seam(a.transpose(1,0,2),b.transpose(1,0,2))
assert (cut+12173).tolist()==p['fullPathGlobalYByX'] and cost==p['pathCostSumSquaredRGB']
take=np.arange(230)[:,None]>=cut[None,:];band=np.where(take[:,:,None],b,a)[:,115:4211];ids=np.where(take,di[:230],ui[1024:1254])[:,115:4211]
assert np.array_equal(band,np.asarray(Image.open(D/'joint-overlap-band.png')))
assert np.array_equal(ids,np.asarray(Image.open(D/'joint-overlap-source-id.png')))
aup=np.asarray(Image.open(D/'r03_c03.joint-proposal.png'));adn=np.asarray(Image.open(D/'r04_c03.joint-proposal.png'))
assert np.array_equal(np.concatenate((aup[-115:],adn[:115]),axis=0),band)
result={'mechanicalCheck':'pass','diskPixelsVerified':total,'exactMinimumErrorPathReplay':True,'sameGlobalPathBothTiles':True,'outside230BandUnchanged':True,'originalCandidatesUnchanged':True,'newArtworkRequested':False,'formalAccepted':False}
(D/'mechanical-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
