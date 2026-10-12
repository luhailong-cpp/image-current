from pathlib import Path
from PIL import Image, ImageChops
from datetime import datetime, timezone
import json, hashlib
import numpy as np

d=Path(__file__).resolve().parent
b=d.parents[2]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=read(d/'request.json'); rec=read(d/'receipt.json'); attempt=read(d/'attempt.json')
raw=d/'native-result.png'; im=Image.open(raw).convert('RGB'); assert im.size==(1254,1254)
gp=d/'native-result.generation.json'
generation={'file':str(raw),'sha256':sha(raw),'nativeDimensions':list(im.size),'format':'PNG','nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin tool receipt exposes no verified model or quality metadata.','sourcePath':r'C:/Users/luyua/.codex/generated_images/01a12554-b67d-7fe1-ba4d-e1ee2a2a8f20/exec-987fa52c-59cd-45b9-8f50-0529015528cd.png','sourceSha256':sha(raw),'prompt':req['prompt'],'promptFile':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'references':[{'file':p,'sha256':sha(p),'role':'Exact unscaled native candidate crop with a narrow alpha inpaint slot'} for p in req['referenced_image_paths']],'requestFile':str(d/'request.json'),'requestSha256':sha(d/'request.json'),'receiptFile':str(d/'receipt.json'),'receiptSha256':sha(d/'receipt.json'),'requestedAt':attempt.get('requestedAtUtc',attempt.get('requestedAt')),'receivedAt':rec['completedAtUtc'],'formalAccepted':False}
assert sha(generation['sourcePath'])==sha(raw)
write(gp,generation)
base=b/'r05_c10/candidate/r05_c10-4096-candidate-v2.png'; bm=base.with_suffix('.manifest.json')
dest=b/'r05_c10/candidate/r05_c10-4096-candidate-v3.png'; assert not dest.exists()
box=[3354,950,4608,2204]; old=Image.open(base).convert('RGB'); target=old.crop(box)
y,x=np.mgrid[0:1254,0:1254]
ax=np.minimum(np.clip((x-570)/37,0,1),np.clip((700-x)/53,0,1))
ay=np.minimum(np.clip((y-40)/30,0,1),np.clip((910-y)/50,0,1))
mask=Image.fromarray(np.rint(ax*ay*255).astype('uint8'),'L'); mp=d/'native-alpha-mask.png';mask.save(mp)
local=Image.composite(im,target,mask); local.save(d/'native-composite-proposal.png')
out=old.copy();out.paste(local,(box[0],box[1]));out.save(dest)
changed=ImageChops.difference(out,old).getbbox()
assert ImageChops.difference(out.crop((4064,0,4096,4096)),old.crop((4064,0,4096,4096))).getbbox() is None
out.crop((3900,970,4096,1900)).save(d/'repair-native-band.png')
pair=Image.new('RGB',(8192,4096));pair.paste(out,(0,0));pair.paste(Image.open(b/'r05_c11/candidate/r05_c11-4096-candidate-v3.png').convert('RGB'),(4096,0))
pair.crop((3900,970,4270,1900)).save(d/'repair-and-core-boundary-native.png')
step={'name':'east-stone-halo-v1','operation':'Image.composite(raw,current native crop,saved L mask), no resize; paste clipped at tile boundary','tileBox':box,'source':str(raw),'sourceSha256':sha(raw),'sourceDimensions':[1254,1254],'mask':str(mp),'maskSha256':sha(mp),'generationRecord':str(gp),'generationRecordSha256':sha(gp)}
manifest={'file':str(dest),'sha256':sha(dest),'dimensions':[4096,4096],'base':str(base),'baseSha256':sha(base),'baseManifest':str(bm),'baseManifestSha256':sha(bm),'steps':[step],'nativePixelsResized':False,'overviewPixelsUsedInFinal':False,'actualModel':None,'actualQuality':None,'formalAccepted':False,'status':'candidate_pending_final_QA','changedBoxVersusV2':list(changed),'trueBoundaryLast32ColumnsUnchanged':True,'createdAt':datetime.now(timezone.utc).isoformat()}
write(dest.with_suffix('.manifest.json'),manifest)
resume=read(b/'production-resume-20261012.json');resume.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'firstNewOutput':{'file':str(raw),'sha256':sha(raw),'nativeDimensions':[1254,1254],'generationRecord':str(gp)},'rawGeneratedImageCount':117,'status':'six_tile_final_QA_in_progress'})
write(b/'production-resume-20261012.json',resume)
print(json.dumps({'candidate':str(dest),'sha256':sha(dest),'rawSha256':sha(raw),'changedBox':changed,'nativeDimensions':list(im.size)}))
