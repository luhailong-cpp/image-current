from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
D=Path(__file__).resolve().parent
old=json.loads((D/'request.json').read_text(encoding='utf-8'))
target=Path(old['references'][0]['path'])
crop=D/'evidence/original-incoming-groove-exact-crop.png'
Image.open(target).crop((180,780,440,1040)).save(crop)
prompt="""Use case: precise-object-edit. Make a surgical edit to image 1 only. Output exactly 1254 x 1254 pixels at the same original scale and crop.
The current lowest diagonal paving joint fades away midway inside a slab. Add ONLY its MISSING continuation, keeping every pixel of the existing incoming joint in its original location. Continue its own exact straight trajectory until it meets the already-existing long down-right diagonal joint, making a T-junction. Do not move either of those existing joints to manufacture the intersection.
Precise pixel anchors on image 1 (origin upper-left):
Existing lower-left groove is centered at (0,1174), (100,1097), (200,1018), (230,995), (280,955), (320,924), (350,901). These anchors and the existing groove must remain in EXACTLY their original locations. In particular do NOT shift it upward by 39 pixels. The groove fades shortly after (350,901).
Missing segment should extend upward-right along that SAME slope, through approximately (450,823), (550,745), (650,667), (750,589), reaching the existing main joint near (795,557). These are the only missing pixels to paint: a very narrow corridor around that segment with the same existing beveled width and natural gray recessed grout. Finish cleanly at the main joint; do NOT cross it.
Existing main diagonal passes (600,376), (700,468), (800,561), (830,589), (850,608). Keep its exact position, width, bevel and texture. Adjust only the tiny T-junction where the new segment touches it.
Image 5 is an unscaled exact crop of image 1 at native coordinates [180,780,440,1040]; it shows the incoming groove's ACTUAL precise location and fading endpoint. Its role is geometry evidence, never a separate output crop.
Images 2,3,4 are approved layout/material/style references only. Preserve image 1's surface and composition instead of repainting from references. No new texture, tonal changes, cracks, objects, words, horizontal/vertical lines or other geometry. Do not restyle the stones. The whole outer 230-pixel band on all four edges is completely locked. Everything outside the missing narrow continuation and tiny T junction must remain identical. Exact same 1254-square framing."""
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=D/'prompts/p04_02-joint-v2.prompt.txt';p.write_text(prompt,encoding='utf-8')
refs=old['references']+[{'role':'exact-incoming-groove-crop','path':str(crop),'sha256':sha(crop),'cropNativeBox':[180,780,440,1040],'resampled':False}]
req={'id':'p04_02-joint-v2','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptPath':str(p),'promptSha256':sha(p),'references':refs,'referenced_image_paths':[r['path'] for r in refs],'expectedPixels':[1254,1254],'actualModel':None,'actualQuality':None,'tool':'builtin image_gen','apiUsed':False,'lockedEdgePixels':230,'intent':'add only missing extension anchored to exact original incoming groove'}
(D/'request-v2.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'id':req['id'],'promptSha256':req['promptSha256'],'references':len(refs)}))

