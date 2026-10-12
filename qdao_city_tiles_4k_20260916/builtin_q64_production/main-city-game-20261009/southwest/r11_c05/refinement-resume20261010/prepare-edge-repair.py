from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;c=int(sys.argv[1]);name=f'p01_{c:02d}';id=name+'.edge-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((D/'prompts'/f'{name}.request.json').read_text(encoding='utf-8'))
source=D/'native'/f'{name}.png';refs=req['references'];refs[0]={'file':str(source),'sha256':sha(source),'role':'1254x1254 actual native edit target; straighten tiny stair-edge notches only','pixels':[1254,1254]}
prompt=f'''Use case: precise-object-edit. Edit IMAGE 1 ONLY, preserving its native 1254 x 1254 square size and exact crop. Return one opaque PNG.
This is a microscopic seam repair. At the narrow vertical join around x=230, a few otherwise horizontal stair grout lines have tiny 2-4 pixel stair-step notches. Repair ONLY those small notches: make each horizontal stair edge flow smoothly and continuously through this join. Pay particular attention to {'the dark line around y=347' if c==2 else 'the dark line around y=558'}. Preserve each edge everywhere else and preserve the original number, width, perspective and spacing of stairs. No new vertical joints.
Keep the existing stone colors, surface texture, shadows and highlights identical. Do not repaint broad surfaces or redesign anything. Top 230 pixels and bottom 230 pixels must remain unchanged. Only the narrow x=180..280 joining area around affected horizontal grooves needs correction. No zoom, no added objects, no text.
Image 2 is the actual upper neighbor overlap for continuity only; last three are approved layout/material/style references, not compositions to reproduce. Exact native output 1254 x 1254.'''
pp=D/'prompts'/f'{id}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
req.update(id=id,prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),references=refs,referenced_image_paths=[x['file'] for x in refs],createdAtUtc=datetime.now(timezone.utc).isoformat(),status='prepared_not_submitted',previousRepairNative={'file':str(source),'sha256':sha(source)})
(D/'prompts'/f'{id}.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(D/'prompts'/f'{id}.request.json'))
