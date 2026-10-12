from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
t=B/'r10_c07';d=t/'pipeline/prompts';parent=d/'p01_01.resume-sol-20261012.final.request.json';r=json.loads(parent.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=t/'pipeline/returned-originals/p01_01.resume-sol-20261012.png'
r['references'][0]={'file':str(p),'sha256':sha(p),'role':'exact native1254 edit target; preserve geometry and all pixels outside bottom red fragments'}
r['referenced_image_paths'][0]=str(p)
prompt='Use case: precise-object-edit. EDIT IMAGE 1 ONLY. One opaque native1254x1254 PNG with identical framing. Change only the blurry red and ivory clipped fragments at the very bottom (y1090 through1254) into crisp, clearly painted original material at their existing positions and scale. Keep the same outlines, colors and object silhouettes. Paint sharp bevels, fine clean contours and quiet hand-painted red and ivory surfaces. All other original architecture and stone geometry must stay exactly in place: straight ivory separator x735 continues from top to bottom, large broad stone faces, red wood at far left, sparse paving seams. No added horizontal seam y230, vertical seam x230 or x550, no new grout lines. No zoom, recentering, added props, blocks, full emblem, complete building, new stone border or new red shapes. The bottom fragments must be as sharply focused as the rest of the original native image: no defocus, bokeh, depth-of-field or blurry area. Do not alter all stone material to fix the red. Images2-4 are mandatory whole-city geometry/daylight natural grey stone/polished Q Daoist style references only, never copy a whole scene or object. Image5 is broad quiet stone material only; copy no geometry. Preserve every outer border pixel except the explicitly blurry bottom red pixels.\n'
pp=d/'p01_01.red-focus-v03-20261012.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),actualModel=None,actualQuality=None,parentSubmittedRequest=str(parent),parentSubmittedRequestSha256=sha(parent))
out=d/'p01_01.red-focus-v03-20261012.request.json';assert not out.exists();out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(out),'target':str(p)}))
