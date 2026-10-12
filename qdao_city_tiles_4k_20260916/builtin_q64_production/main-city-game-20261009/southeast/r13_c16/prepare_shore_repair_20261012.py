from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;D=T/'repairs/shore-water-join-20261012-v1';D.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):
 with Image.open(p) as im:size=list(im.size)
 return {'path':str(p),'sha256':sha(p),'pixels':size}
def png(p,im):
 if not p.exists():
  with p.open('xb') as f:im.save(f,format='PNG')
 else:assert Image.open(p).tobytes()==im.tobytes()
def write(p,d):
 if not p.exists():
  with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
L=read(T/'candidate/latest-assembly.json')
assert L['candidate']['sha256']=='9f88d247bd253656e79f9d888844719bdd1478526c87ba661ca1449511d64f82'
for k in ('candidate','context','manifest'):assert sha(L[k]['path'])==L[k]['sha256']
box=[660,0,1914,1254]
source=Image.open(L['candidate']['path']).convert('RGB').crop(box)
unmarked=D/'reference-native-1254.png';png(unmarked,source)
target=source.copy();draw=ImageDraw.Draw(target)
draw.rectangle((100,0,699,1253),fill=(255,0,255))
targetpath=D/'edit-target-native-1254.png';png(targetpath,target)
guide=T/'layout-only/tile-layout-only.png'
prompt='''Use case: precise-object-edit, stylized daylight Taoist chibi game illustration.
Output one real native opaque 1254x1254 PNG, at exactly the framing and scale of the last image.
Image 1 is the approved coarse WHOLE-TILE layout guide only; do not render its coarse pixels or copy complete objects. Image 2 is the exact unmarked 1254-square native crop, showing the existing stone and water. Image 3, the LAST IMAGE, is the edit target; only its magenta rectangle x100..699 is editable.
Repair the false straight vertical division formerly around image x513 (tile x1173), running from the rock at the top through water below. It is not a real rock edge, wall or shadow. Make the existing single rounded grey shore boulder one uninterrupted painted material surface and smoothly continuous submerged contour. Continue the surrounding blue-teal pond, shadows and restrained sunlight ripple texture with no straight line, rectangular color step or hard patch border.
Within this magenta region remove ALL three wrongly added little floating green lotus leaves and their shadows, including the two cut-off half leaves that formerly stopped at the false vertical division. The approved tile guide has quiet water in this exact area. Replace them only with matching water and existing boulder reflection. Preserve the approved single leaf partly cropped at image right and all objects outside magenta.
Keep exact boulder shape/position, same water depth, warm daylight and clean rounded hand-painted finish. No new stone, leaf, plant, flower, fish, boat, lantern, post, furniture, architecture or text. Do not move or rescale anything. Match unchanged native textures and ripple centerlines along all mask edges. Remove all magenta; output no border, blur, glow, label, UI or watermark. Outside magenta preserve the reference exactly.'''
req={'prompt':prompt,'referenced_image_paths':[str(guide),str(unmarked),str(targetpath)],'transparent_background':False}
write(D/'request.json',req)
write(D/'preparation.json',{'schemaVersion':1,'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':T.name,'version':D.name,'sourceCandidate':L['candidate'],'sourceContext':L['context'],'sourceAssembly':L['manifest'],'cropBoxIn4096':box,'nativeAdoptionCrop':[100,0,700,1254],'pasteBoxIn4096':[760,0,1360,1254],'references':[dict(art(p),role=r) for p,r in [(guide,'whole-tile layout only'),(unmarked,'same native crop unmarked reference'),(targetpath,'sole edit target')]],'target':art(unmarked),'markedTarget':art(targetpath),'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'resampling':False,'formalAccepted':False})
if not (D/'prompt.txt').exists():
 with (D/'prompt.txt').open('x',encoding='utf-8') as f:f.write(prompt)
print(json.dumps({'request':str(D/'request.json'),'target':str(targetpath),'reference':str(unmarked),'guide':str(guide)}))
