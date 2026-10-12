from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).parent.parent;D=T/'continuity-repair/merged-v2';O=T/'qa/final-external';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((D/'derivation.json').read_text());E=4326;num=np.zeros((E,E,3),np.uint32);den=np.zeros((E,E),np.uint32)
for s,w in zip(m['sources'],m['sourceWeightMaps']):
 assert sha(s['file'])==s['sha256'] and sha(w['file'])==w['sha256']
 a=np.asarray(Image.open(s['file']).convert('RGB'));q=np.asarray(Image.open(w['file']),dtype=np.uint32);x,y=s['offsetXY'];assert q.shape==(1254,1254)
 num[y:y+1254,x:x+1254]+=q[:,:,None]*a;den[y:y+1254,x:x+1254]+=q
assert np.all(den==65535)
recon=np.rint(num.astype(np.float64)/65535).astype(np.uint8);assert np.array_equal(recon,np.asarray(Image.open(m['file'])))
cand=T/'candidate/r04_c05-pipeline-minimum-error-e2769dba9467-6e5fcf.png';im=Image.open(cand).convert('RGB');assert np.array_equal(recon[115:4211,115:4211],np.asarray(im))
west=T.parent/'r04_c04/candidate/r04_c04-pipeline-fixed-native-contexts-71cabb17b21f.png';wim=Image.open(west).convert('RGB');records=[]
def save(label,a,sources):
 p=O/(label+'.png');a.save(p);records.append({'file':str(p),'sha256':sha(p),'pixels':list(a.size),'sourceRecords':sources,'resampled':False,'nativePixelScale':1,'actuallyViewed':False,'verdict':'pending'})
for j in range(4):
 y=j*1024;dst=Image.new('RGB',(320,1024));dst.paste(wim.crop((3936,y,4096,y+1024)),(0,0));dst.paste(im.crop((0,y,160,y+1024)),(160,0))
 save(f'west-segment{j+1:02d}',dst.transpose(Image.Transpose.ROTATE_90),[{'file':str(west),'sha256':sha(west),'crop':[3936,y,4096,y+1024]},{'file':str(cand),'sha256':sha(cand),'crop':[0,y,160,y+1024]}])
inventory=json.loads((T.parent/'outer-neighbor-inventory.json').read_text())
south=next(e for e in inventory['edges'] if e['tile']=='r04_c05' and e['edge']=='south')
for j,s in enumerate(south['sources']):
 n=Image.open(s['file']).convert('RGB');dst=Image.new('RGB',(1024,320));dst.paste(im.crop((j*1024,3936,(j+1)*1024,4096)),(0,0));dst.paste(n.crop((115,115,1139,275)),(0,160))
 save(f'south-segment{j+1:02d}',dst,[{'file':str(cand),'sha256':sha(cand),'crop':[j*1024,3936,(j+1)*1024,4096]},{'file':s['file'],'sha256':sha(s['file']),'crop':[115,115,1139,275]}])
(O/'manifest.json').write_text(json.dumps({'candidate':str(cand),'candidateSha256':sha(cand),'externalCrops':records,'formalAccepted':False},indent=2))
v={'allSourceAndWeightHashesVerified':True,'sourceCount':len(m['sources']),'weightSums65535':True,'reconstructionPixelExact':True,'pipelineCandidateEqualsDerivedCrop':True,'resampled':False,'blended':True,'bandWidthPixels':128,'actualModel':None,'formalAccepted':False}
(D/'verification.json').write_text(json.dumps(v,indent=2));print(json.dumps({'verification':v,'externalQADirectory':str(O)}))

