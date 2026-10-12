from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil

d=Path(__file__).resolve().parent
version='narrow-upper-joint-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
v=d/version;v.mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
base=read(d/'prepare.json');request=read(d/'request.json')
target=v/'target-native-1254.png';shutil.copyfile(base['target'],target)
assert sha(target)==base['targetSha256']
prompt=('Use case: precise local geometry repair. Output exactly 1254 by 1254 opaque pixels. '
'The first 3 images are approved style references only. The final image is the sole actual native-pixel edit target. '
'Edit ONLY the small UPPER RIGHT stone-grout discontinuity at target coordinate x625,y414. The dark diagonal stone joint entering from the left reaches approximately x624,y410, but on the right it restarts near y427, producing a visible 17-pixel step. '
'Make this ONE dark grout line continue cleanly from the exact unchanged left endpoint into the existing upper-right diagonal grout. Work only within x625..880,y260..470. Smoothly join the same existing grout at the right end. Preserve its narrow bevel and width. '
'The entire area x0..624 is ABSOLUTELY FIXED. Every pixel outside the small named upper-right repair region should remain visually identical, including the still-unrepaired lower cross seam, all red paper, stone grain, shadows and the wood corner. '
'Do not improve or redraw other seams. Do not change slab size or perspective. Preserve natural light-grey stone hue and existing fine grain. No scene reconstruction, global recoloring, texture replacement, new paper, new cracks, zoom, reframe, resize, text, border or watermark. Return the same full image with this one local grout step repaired.')
(v/'prompt.txt').write_text(prompt,encoding='utf-8')
request['prompt']=prompt;request['referenced_image_paths'][-1]=str(target)
write(v/'request.json',request)
write(v/'preparation.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'version':version,'sourceCornerPreparation':str(d/'prepare.json'),'sourceCornerPreparationSha256':sha(d/'prepare.json'),'target':str(target),'targetSha256':sha(target),'nativeSize':[1254,1254],'intendedRepairBounds':[625,260,880,470],'immutableQuadrant':[0,0,625,625],'resized':False,'formalAccepted':False,'requestSha256':sha(v/'request.json')})
print(json.dumps({'directory':str(v),'request':request}))
