"""Assemble exact native 1024-pixel cores and produce audit crops; no paint or upscale."""
from pathlib import Path
from PIL import Image
import json,sys
from workflow import ROOT,read,write,sha,now,progress
versions={'11':'01','12':'06','13':'02','14':'01','21':'01','22':'01','23':'01','24':'01','31':'01','32':'01','33':'01','34':'01','41':'01','42':'01','43':'02','44':'02'}
tile=Image.new('RGB',(4096,4096)); contributions=[]
for rc,v in versions.items():
 p=ROOT/'native'/f'r09_c12_p{rc}_v{v}.png'; im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
 r,c=map(int,rc); dest=[(c-1)*1024,(r-1)*1024];tile.paste(im.crop((115,115,1139,1139)),tuple(dest))
 contributions.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':[115,115,1139,1139],'destination':dest,'record':str(p)+'.generation.json'})
out=ROOT/'tiles'/'r09_c12.candidate.png';assert not out.exists();tile.save(out)
record={'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':4096,'height':4096,'operation':'exact native core crop and hard paste, no resampling, feathering or painting','nativeSourceDimensions':[1254,1254],'nativeCorePixels':1024,'contributions':contributions,'fullCoverage':True,'sourceNativePixelsUsed':16777216,'finalPixels':16777216,'resizedAfterGeneration':False,'status':'candidate_internal_review_pending_external_edges_unreviewed','actualModel':None,'actualQuality':None,'evidence':'Each source has separate native generation record; tool does not disclose actual model/quality.'}
write(Path(str(out)+'.generation.json'),record)
write(ROOT/'selected-native.json',{'tile':'r09_c12','selectionTime':now(),'entries':contributions,'allExternalEdgesAccepted':False})
for r in range(1,4):
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];q=ROOT/'qa'/f'r09_c12.junction_{r}{c}.png';tile.crop(box).save(q)
  write(Path(str(q)+'.generation.json'),{'file':q.as_posix(),'sha256':sha(q),'operation':'mechanical 100 percent native junction crop','source':out.as_posix(),'sourceSha256':sha(out),'sourceCrop':box})
preview=ROOT/'qa'/'r09_c12.preview-1024.png';tile.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
write(Path(str(preview)+'.generation.json'),{'file':preview.as_posix(),'sha256':sha(preview),'operation':'downscaled review preview only; never final pixels','source':out.as_posix(),'sourceSha256':sha(out),'dimensions':[1024,1024]})
progress(status='tile_internal_review',usableNativeCount=16,currentPatch=None,complete4kCount=1,nextStep='Review 24 internal seams and 9 junctions; external edges pending adjacent native tiles',formalAcceptedCount=0)
print(json.dumps({'file':out.as_posix(),'sha256':sha(out),'dimensions':[4096,4096],'exactSourcePixelCoverage':16777216}))

