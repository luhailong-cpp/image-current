from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for version in sys.argv[1:]:
 D=BASE/version
 p=D/'generated.png'
 south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
 N=Image.open(p).convert('RGB');S=Image.open(south).convert('RGB')
 n=np.array(N).astype(float).mean(axis=2);s=np.array(S).astype(float).mean(axis=2)
 hard=Image.new('RGB',(1254,640));hard.paste(N.crop((0,819,1254,1139)),(0,0));hard.paste(S.crop((0,115,1254,435)),(0,320))
 out=D/'south-hard-join-native.png'
 if out.exists():raise FileExistsError(out)
 hard.save(out)
 hard.crop((600,200,1120,450)).save(D/'rail-boundary-native.png')
 diff=np.abs(np.array(N.crop((0,1024,1254,1254))).astype(np.int16)-np.array(S.crop((0,0,1254,230))).astype(np.int16))
 samples=[]
 for y in [1100,1120,1137,1160,1200]:
  samples.append({'newY':y,'southY':y-1024,'newOuterRightX':int(980+np.argmin(np.diff(n[y-1:y+2].mean(axis=0))[980:1100])),
                  'southOuterRightX':int(980+np.argmin(np.diff(s[y-1025:y-1022].mean(axis=0))[980:1030]))})
 result={'file':str(p),'sha256':sha(p),'nativePixels':list(N.size),'sourceSouth':str(south),'sourceSouthSha256':sha(south),
         'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'overlapMAE':float(diff.mean()),
         'identicalOverlapPixels':int(np.all(diff==0,axis=2).sum()),'overlapPixels':1254*230,'samples':samples,
         'formalAccepted':False,'diagnosticOnly':True}
 (D/'native-and-boundary-metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result,indent=2))
