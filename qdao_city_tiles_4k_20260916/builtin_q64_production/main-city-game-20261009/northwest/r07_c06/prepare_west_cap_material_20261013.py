from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image, ImageDraw
T=Path(__file__).resolve().parent
D=T/'repair-batches/west-cap-material-01'
D.mkdir(parents=True,exist_ok=False)
def ref(f): return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def savej(f,v): f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C=T/'candidate/r07_c06-candidate-native-roi-v07.png'
W=T.parent/'r07_c05/candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/candidate.png'
im=Image.new('RGB',(1254,1254)); im.paste(Image.open(W).crop((3896,512,4096,1766)),(0,0)); im.paste(Image.open(C).crop((0,512,1054,1766)),(200,0))
im.save(D/'edit-target.png')
g=im.copy();dr=ImageDraw.Draw(g);dr.rectangle((201,510,430,650),outline=(255,0,255),width=3);g.save(D/'locator-guide.png')
prompt='''Use case: precise-object-edit. Asset: native 1254 by 1254 hand-painted Daoist chibi game map stone-floor repair. Image 1 is the exact unmarked edit target; image 2 is a locator only with a magenta rectangle around the one defect. Retain the target framing and exact 1254 by 1254 size.
Fix only the rectangular stone-grain cutoff and pale horizontal pasted band ABOVE the small triangular grout cap near (x200..410,y627). Make the tiny stone grain above the closed triangular cap flow continuously with the surrounding same stone surface, with no rectangular patch edge. Preserve the triangular cap's dark horizontal grout line and its two diagonal sides at their existing exact locations, preserve its gold vertex below, preserve all other dark grout paths and vertices without shifting any endpoints. The area left of x200 is a locked actual neighbor: keep it unchanged. Preserve the original fine diagonal pale square stone grain scale, color, relief and daylight. Do not regularize or redraw the grout grid. Do not add any cracks, flowers, red flecks, stars, ornaments, text or objects. This is a tiny material-only correction above an already closed triangle; outside the marked region copy the target unchanged. Remove all magenta locator ink. Opaque RGB image, no transparency, no crop, no enlargement or composition change.'''
args={'prompt':prompt,'referenced_image_paths':[str(D/'edit-target.png'),str(D/'locator-guide.png')],'transparent_background':False}
(D/'prompt.txt').write_text(prompt,encoding='utf-8');savej(D/'parameters.json',args)
savej(D/'request.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'paidApiUsed':False,'parameters':args,'inputReferences':[ref(C),ref(W)],'editTarget':ref(D/'edit-target.png'),'locatorGuide':ref(D/'locator-guide.png'),'guideOnly':True,'nativeWorldBox':[20280,25088,21534,26342],'tileOriginXY':[-200,512],'sourceResampled':False,'formalAccepted':False})
print(json.dumps({'directory':str(D),'args':args},ensure_ascii=False))
