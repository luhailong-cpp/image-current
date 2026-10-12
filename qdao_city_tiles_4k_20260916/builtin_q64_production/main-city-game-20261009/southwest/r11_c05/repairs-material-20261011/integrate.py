from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
BASE=D.parents[1]
OUT=D/'output';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
source=BASE/'r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.context.png'
assert sha(source)=='0d6d89a6e6c97ef1b397a77268b83a745d4333579e18e64f4f827bd34fbc6906'
before=np.array(Image.open(source).convert('RGB'));after=before.copy();maskall=np.zeros(before.shape[:2],bool);patches=[]
for name in ['M01','M03']:
 p=D/(name+'.overlay-proposal.json'); rec=json.loads(p.read_text())
 for key in ['native','sourceInput','sourceCandidate','patch','pasteMask','alpha']:
  assert sha(rec[key]['file'])==rec[key]['sha256'],key
 box=rec['contextBox'];x0,y0,x1,y1=box
 patch=np.array(Image.open(rec['patch']['file']).convert('RGB'));mask=np.array(Image.open(rec['pasteMask']['file']))>0
 assert not maskall[y0:y1,x0:x1][mask].any()
 region=after[y0:y1,x0:x1];region[mask]=patch[mask];maskall[y0:y1,x0:x1]|=mask
 patches.append({'id':name,'proposal':str(p),'proposalSha256':sha(p),'contextBox':box,'activePixels':int(mask.sum()),'native':rec['native'],'patch':rec['patch'],'mask':rec['pasteMask']})
assert np.array_equal(before[~maskall],after[~maskall])
assert np.array_equal(before[:115],after[:115]) and np.array_equal(before[-115:],after[-115:])
assert np.array_equal(before[:,:115],after[:,:115]) and np.array_equal(before[:,-115:],after[:,-115:])
core=after[115:4211,115:4211]
ctxp=OUT/'r11_c05.material-repaired.candidate.context.png';corep=OUT/'r11_c05.material-repaired.candidate.png'
assert not ctxp.exists() and not corep.exists()
Image.fromarray(after).save(ctxp);Image.fromarray(core).save(corep)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':info(source),'patches':patches,'output':info(corep),'context':info(ctxp),'tileWorldOrigin':[16384,40960],'outsideMasksExact':True,'outer115pxHaloUnchanged':True,'coreEqualsContextCrop':True,'imageResampling':False,'actualModel':None,'actualQuality':None,'newNativeSuccessfulReturns':2,'geometryPassed':None,'internalPassed':False,'formalAccepted':False,'pending':['Independent local review of M01/M03','Broad repetitive material texture M02','Cross-tile repairs and renewed four-edge checks']}
(OUT/'assembly.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'core':record['output'],'context':record['context']}))
