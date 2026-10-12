from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
base=T/'candidate/r05_c11-4096-candidate-v2.png';im=Image.open(base).convert('RGB');p=T/'repairs/sand-halo-v1/proposal.json';pr=read(p);source=Path(pr['nativeRepair']['file']);maskp=Path(pr['mask']['file']);box=pr['tileTargetBox'];raw=Image.open(source).convert('RGB');mask=Image.open(maskp).convert('L')
assert raw.size==(1254,1254) and sha(source)==pr['nativeRepair']['sha256'] and sha(maskp)==pr['mask']['sha256']
im.paste(Image.composite(raw,im.crop(box),mask),box[:2]);out=T/'candidate/r05_c11-4096-candidate-v3.png';im.save(out)
preview=im.copy();preview.thumbnail((1254,1254));preview.save(T/'qa/candidate-v3-preview.png')
step={'name':'sand-halo-v1','operation':'Image.composite(raw,current native crop,saved Lmask),no resize','tileBox':box,'source':str(source),'sourceSha256':sha(source),'sourceDimensions':list(raw.size),'mask':str(maskp),'maskSha256':sha(maskp),'proposal':str(p),'proposalSha256':sha(p),'generationRecord':pr['nativeRepair']['generationRecord'],'generationRecordSha256':sha(pr['nativeRepair']['generationRecord'])}
manifest={'file':str(out),'sha256':sha(out),'dimensions':list(im.size),'base':str(base),'baseSha256':sha(base),'baseManifest':str(base.with_suffix('.manifest.json')),'baseManifestSha256':sha(base.with_suffix('.manifest.json')),'steps':[step],'nativePixelsResized':False,'overviewPixelsUsedInFinal':False,'actualModel':None,'actualQuality':None,'formalAccepted':False,'status':'candidate_pending_final_QA','changedBoxVersusV2':ImageChops.difference(im,Image.open(base)).getbbox(),'createdAt':datetime.now(timezone.utc).isoformat()}
out.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'changedBox':manifest['changedBoxVersusV2']}))
