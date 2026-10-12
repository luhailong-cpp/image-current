from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'candidate-inventory.json').read_text(encoding='utf-8'))
records=[]
seen={}
for group,frames in data['groups'].items():
    for f in frames:
        p=ROOT/f['url'][3:]
        im=Image.open(p).convert('RGBA')
        a=im.getchannel('A')
        solid=a.point(lambda v:255 if v>=32 else 0)
        box=solid.getbbox()
        edges={'left':solid.crop((0,0,1,im.height)).getbbox() is not None,'top':solid.crop((0,0,im.width,1)).getbbox() is not None,'right':solid.crop((im.width-1,0,im.width,im.height)).getbbox() is not None,'bottom':solid.crop((0,im.height-1,im.width,im.height)).getbbox() is not None}
        pixel_hash=hashlib.sha256(im.tobytes()).hexdigest()
        key=group+'/'+str(f['frame']).zfill(2)
        rec={'slot':key,'file':p.relative_to(ROOT).as_posix(),'sha256':f['sha256'],'pixelSha256':pixel_hash,'alphaRange':list(a.getextrema()),'bboxAtAlpha32':list(box) if box else None,'marginAtAlpha32':[box[0],box[1],im.width-box[2],im.height-box[3]] if box else None,'touchesCanvasEdgeAtAlpha32':edges,'requiresBoundaryInspection':any(edges.values()),'duplicatePixelsOf':seen.get(pixel_hash)}
        seen[pixel_hash]=key
        records.append(rec)
out={'status':'technical measurements only; not visual acceptance','candidateCount':len(records),'edgeTouchingSlots':[r['slot'] for r in records if r['requiresBoundaryInspection']],'pixelDuplicates':[r['slot'] for r in records if r['duplicatePixelsOf']],'records':records}
(ROOT/'geometry-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='records'}))

