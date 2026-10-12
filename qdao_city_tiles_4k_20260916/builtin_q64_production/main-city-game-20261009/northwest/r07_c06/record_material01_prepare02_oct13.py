from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;D=T/'repair-batches/c3c4-material-01';H=Path('C:/Users/luyua/.codex/generated_images/01a1354f-cb97-7770-b80e-7bd82866ed6d/exec-f16d4919-e9ce-4f5f-9bf4-d5c9f19d9300.png')
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def wj(f,r):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert ref(H)['sha256']==ref(D/'native.png')['sha256'];im=Image.open(D/'native.png');assert im.size==(1254,1254)
wj(D/'generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceHostFile':str(H),'sourceNativeFile':ref(D/'native.png'),'request':ref(D/'request.json'),'parameters':ref(D/'parameters.json'),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'hostByteIdentical':True,'nativeWorldBox':[22925,24576,24179,25830],'tileOriginXY':[2445,0],'newSourceAdopted':False,'formalAccepted':False})
im.crop((537,490,717,750)).save(D/'material-detail-native.png')
wj(D/'review.json',{'source':ref(D/'native.png'),'status':'needs_repair_not_adopted','actuallyViewed':True,'finding':'The original vertical pale cutoff remains above and below the closed connector. Geometry remains closed but texture request did not resolve the seam.','attempt':1,'formalAccepted':False})
B=T/'repair-batches/c3c4-material-02';B.mkdir(exist_ok=False)
base=Image.open(D/'edit-target.png');base.save(B/'reference-original.png');guide=base.copy();draw=ImageDraw.Draw(guide)
rects=[[602,520,655,569],[602,642,655,708]]
for r in rects:draw.rectangle(r,fill=(255,0,255))
guide.save(B/'masked-layout-guide.png')
prompt='''Use case: precise-object-edit. Complete the TWO SMALL MAGENTA MISSING-TEXTURE REGIONS in image 1. Image 1 is a layout-only masked edit guide, exact native 1254 by 1254. Image 2 is the unmarked original for position and grout geometry only. Replace every magenta pixel with newly hand-painted native stone surface matching the surrounding fine diagonal crosshatched gray-beige stone grain. The two small rectangles are just above and below the short central vertical brown grout connector. Each region must have continuous natural stone texture and no vertical white stripe or rectangular patch boundary. Do NOT copy the defective vertical white texture cutoff from image 2 into the filled regions. Continue the crosshatched stone grain through those regions at the same scale and soft tone. The brown vertical grout connector between the two missing regions, its two diagonal endpoints, all other grout lines, gold vertices, stone shapes and blue border are LOCKED and unchanged. Paint only those two missing material areas; preserve all existing geometry and framing. Remove ALL magenta. No blur, new objects, straightened grid, moved vertices, rescaling, cropping or reframing. Output exact opaque RGB 1254 x 1254.'''
args={'prompt':prompt,'referenced_image_paths':[str(B/'masked-layout-guide.png'),str(B/'reference-original.png')],'transparent_background':False}
wj(B/'parameters.json',args);(B/'prompt.txt').write_text(prompt,encoding='utf-8');wj(B/'request.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'parameters':args,'referenceOriginal':ref(B/'reference-original.png'),'maskedLayoutGuide':ref(B/'masked-layout-guide.png'),'guideOnlyNotProductionPixels':True,'maskedGuideRects':rects,'nativeWorldBox':[22925,24576,24179,25830],'tileOriginXY':[2445,0],'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'paidApiUsed':False,'sourceResampled':False,'formalAccepted':False,'attempt':2})
print(json.dumps(args))
