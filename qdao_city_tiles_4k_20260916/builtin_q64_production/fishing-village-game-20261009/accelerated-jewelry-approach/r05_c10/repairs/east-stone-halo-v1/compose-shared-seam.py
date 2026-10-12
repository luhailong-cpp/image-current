from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import json,hashlib
import numpy as np
d=Path(__file__).resolve().parent;b=d.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=d/'native-result.png';gp=d/'native-result.generation.json';im=Image.open(raw).convert('RGB')
y,x=np.mgrid[0:1254,0:1254]
ax=np.minimum(np.clip((x-685)/40,0,1),np.clip((820-x)/45,0,1))
ay=np.minimum(np.clip((y-650)/50,0,1),np.clip((960-y)/50,0,1))
mask=Image.fromarray(np.rint(ax*ay*255).astype('uint8'),'L');mp=d/'shared-seam-native-alpha-mask.png';mask.save(mp)
finals=[]
for t,box in [('r05_c10',[3354,950,4608,2204]),('r05_c11',[-742,950,512,2204])]:
 base=b/t/'candidate'/f'{t}-4096-candidate-v3.png';bm=base.with_suffix('.manifest.json');dest=b/t/'candidate'/f'{t}-4096-candidate-v4.png';assert not dest.exists()
 old=Image.open(base).convert('RGB');local=Image.composite(im,old.crop(box),mask);out=old.copy();out.paste(local,(box[0],box[1]));out.save(dest)
 change=ImageChops.difference(out,old).getbbox()
 step={'name':'shared-bottom-stone-seam-v1','operation':'Image.composite(shared raw,current native crop,saved L mask),no resize; native paste clipped at tile boundaries','tileBox':box,'source':str(raw),'sourceSha256':sha(raw),'sourceDimensions':[1254,1254],'mask':str(mp),'maskSha256':sha(mp),'generationRecord':str(gp),'generationRecordSha256':sha(gp)}
 m={'file':str(dest),'sha256':sha(dest),'dimensions':[4096,4096],'base':str(base),'baseSha256':sha(base),'baseManifest':str(bm),'baseManifestSha256':sha(bm),'steps':[step],'nativePixelsResized':False,'overviewPixelsUsedInFinal':False,'actualModel':None,'actualQuality':None,'formalAccepted':False,'status':'candidate_pending_final_QA','changedBoxVersusV3':list(change),'sharedGenerationCountedOnce':True,'createdAt':datetime.now(timezone.utc).isoformat()}
 write(dest.with_suffix('.manifest.json'),m);finals.append(m)
 pair=locals().get('pair')
pair=Image.new('RGB',(8192,4096));pair.paste(Image.open(finals[0]['file']),(0,0));pair.paste(Image.open(finals[1]['file']),(4096,0))
pair.crop((3920,1550,4270,1950)).save(d/'shared-seam-final-native.png')
pair.crop((3900,970,4270,1900)).save(d/'all-repaired-stones-native.png')
write(d/'shared-seam-proposal.json',{'selectedFiles':finals,'nativePixelsResized':False,'newGeneratedRawCount':0,'existingRawUsedAtNativeScale':str(raw),'mask':str(mp),'maskSha256':sha(mp),'scope':'Only bottom stone tonal cut across actual c10/c11 seam; original stone geometry and sand preserved.'})
print(json.dumps([{'file':m['file'],'sha256':m['sha256'],'changedBox':m['changedBoxVersusV3']} for m in finals]))
