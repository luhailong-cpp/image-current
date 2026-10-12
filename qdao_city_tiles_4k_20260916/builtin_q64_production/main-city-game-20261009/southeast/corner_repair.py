"""Prepare a native four-core corner edit; crops/pastes only, no artwork synthesis."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ZONE=Path(__file__).resolve().parent
OUT=ZONE/'corner-repair-20261011'
REF=ZONE.parents[1]/'parallel_20261005'/'daylight-only-20261009'
BOXES=[(3471,3471,4096,4096),(0,3471,629,4096),(3471,0,4096,629),(0,0,629,629)]
DEST=[(0,0),(625,0),(0,625),(625,625)]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def prepare():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'prepare.json').exists(),'Preparation already exists'
    progress=json.loads((ZONE/'progress.json').read_text(encoding='utf-8-sig'))
    target=Image.new('RGB',(1254,1254)); sources=[]
    for rec,box,dest in zip(progress['tiles'],BOXES,DEST):
        p=Path(rec['candidate']['path']); assert sha(p)==rec['candidate']['sha256']
        im=Image.open(p).convert('RGB'); crop=im.crop(box); target.paste(crop,dest)
        sources.append({'tile':rec['tile'],'candidate':str(p),'candidateSha256':sha(p),'cropBox':box,'destination':dest,'cropPixelSha256':hashlib.sha256(crop.tobytes()).hexdigest(),'writable':rec['tile']!='r13_c13'})
    tp=OUT/'four-core-corner-edit-target-1254.png'; target.save(tp)
    refs=[REF/'tianyong'/'tianyong-spring-natural-stone-v9.png',REF/'tianyong'/'tianyong-natural-stone-detail-v1.png',REF/'user-references-20261009'/'mail-daoist-style.jpg',tp]
    prompt='''Use case: precise-object-edit / compositing.
Asset: one native map seam repair, exactly 1254 x 1254 opaque pixels.
Input images 1-3 are approved layout/style/detail references only, never compositions to recreate. Image 4 is the sole edit target, an unscaled four-tile corner of an existing chibi Taoist Spring Festival city map.
Repair the pavement geometry and daylight color transitions around the cross at x=625 and y=625. The upper-left 625 by 625 quadrant is immutable: preserve every stone edge, grout line, texture and paper fragment there. Match the upper-right, lower-left and lower-right quadrants to the stone geometry entering from this fixed upper-left quadrant, and connect the grout lines already entering from all four outer edges. Remove the sudden cross-shaped tile boundary and broken or doubled grout. Preserve the outermost 100-pixel perimeter and all line endpoint positions there; local changes should settle smoothly before the perimeter. At the center, each diagonal dark grout line must continue as a single clean consistent-width line, without an abrupt jog, gap or duplicate shadow.
Keep the same isometric camera, scale, existing irregular large grey-blue stone slabs, soft clean daylight, small red firecracker paper fragments, and hand-painted rounded game-art finish. Preserve all existing objects and overall stone layout, with only local geometric correction needed for continuous stone joints. Match natural grey-blue stone values continuously without a new blue or dark rectangular band. No zoom, crop, resize, rotation, buildings, trees, pots, furniture, letters, labels, new ornament, people, UI or watermark. Return only the edited full-size 1254-square image.''' 
    (OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
    request={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
    write(OUT/'request.json',request)
    write(OUT/'prepare.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'target':str(tp),'targetSha256':sha(tp),'size':[1254,1254],'globalBox':[52623,52623,53877,53877],'sources':sources,'references':[{'path':str(p),'sha256':sha(p)} for p in refs],'resized':False,'status':'prepared_not_generated'})
    print(json.dumps({'target':str(tp),'request':str(OUT/'request.json')},ensure_ascii=False))

if __name__=='__main__': prepare()
