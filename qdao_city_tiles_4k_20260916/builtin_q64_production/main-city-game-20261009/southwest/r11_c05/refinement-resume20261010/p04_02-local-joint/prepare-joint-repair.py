from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
sw=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
out=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/p04_02-local-joint")
out.mkdir(parents=True,exist_ok=True)
for d in ['prompts','receipts','native','output','qa','evidence']: (out/d).mkdir(exist_ok=True)
contract=json.loads((sw.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
target=sw/'r11_c05/native/p04_02.png'
refs=[target,Path(contract['layoutReference']),Path(contract['detailStyleReference']),Path(contract['primaryStyleReference'])]
prompt="""Use case: precise-object-edit.
Edit the FIRST image only, preserving the exact original 1254 by 1254 pixel framing and stone texture. Images 2, 3 and 4 are approved layout/detail/style references only, never substitute their composition.
Surgical paving-joint repair: the first image has a broken short diagonal grout groove in its lower-left quarter. It enters the left edge near (0,1174), runs upward-right through approximately (230,1000), then fades out around (370,895), falsely ending inside one stone slab. CONTINUE THIS SAME GROOVE in a straight upward-right path with matching existing width, recessed shadow and narrow bright stone bevel. It must naturally meet the ALREADY EXISTING long upper-left to lower-right diagonal main groove near (800,570), forming a clean believable T-junction. Preserve the main diagonal exactly; do not extend the new groove past the main diagonal. The repair is only between the fading end and that junction.
All coordinates are pixel positions on the original 1254 square image, origin top left. Match the slope of the lower-left groove already present. Keep the existing groove portion below-left fully intact. Keep the original texture and lighting on both sides; NO global material repaint, color correction, contrast change, new cracks, new vertical/horizontal lines, props, objects or text. Keep all other complete paving joints and their geometry unchanged.
LOCK the entire outer 230 pixels on all FOUR edges of image 1 exactly. The only permitted change is the small interior continuation and T-junction approximately inside x=250..890,y=500..1010. All original surface detail elsewhere stays identical. Output exactly one native 1254 by 1254 image, same scale, same perspective and original crop. No resize or broad restyling."""
p=out/'prompts/p04_02-joint-v1.prompt.txt'
p.write_text(prompt,encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req={'id':'p04_02-joint-v1','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptPath':str(p),'promptSha256':sha(p),'referenced_image_paths':[str(p) for p in refs],'references':[{'role':('edit-target' if i==0 else ['approved-layout','approved-detail','approved-primary-style'][i-1]),'path':str(p),'sha256':sha(p)} for i,p in enumerate(refs)],'expectedPixels':[1254,1254],'actualModel':None,'actualQuality':None,'tool':'builtin image_gen','apiUsed':False,'attemptLimit':1,'lockedEdgePixels':230,'geometryIntent':'continue existing incomplete lower-left groove to main diagonal inside frozen edges'}
(out/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(req,ensure_ascii=False))

