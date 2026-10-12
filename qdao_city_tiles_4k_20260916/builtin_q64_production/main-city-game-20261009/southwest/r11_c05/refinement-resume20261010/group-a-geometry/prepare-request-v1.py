from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
D=Path(__file__).resolve().parent;SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
contract=json.loads((SW.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
crop=json.loads((D/'input/crop-record.json').read_text(encoding='utf-8'))
paths=[Path(crop['target']),Path(contract['layoutReference']),Path(contract['detailStyleReference']),Path(contract['primaryStyleReference'])]
prompt="""Use case: precise-object-edit. Edit ONLY image 1, a native 1254 by 1254 stone paving crop. Preserve its exact framing, scale and every existing complete joint position. Images 2-4 are approved style references only; do not copy their composition or restyle the stone.
Repair exactly THREE defects, using image-1 pixel coordinates with origin at top left:
A. Near (533,365), the upper long up-right diagonal grout has a small misaligned/doubled notch. Join its two existing sides into one continuous clean narrow groove with continuous bright stone bevel. Keep the line unchanged outside a tiny neighborhood x495..580,y325..405.
B. The down-right diagonal begins falsely at (533,810) inside a slab and continues correctly to the existing junction near (838,1097). Keep that whole existing segment EXACTLY in place. ADD ONLY its missing northwest continuation, following that SAME straight line backward from (533,810) through about (440,722),(350,637), to naturally meet the upper existing long diagonal near (264,555). Form a clean T-junction there without moving or crossing the upper existing diagonal. No hanging endpoint remains at (533,810). Match the original narrow recessed groove, shadow and bevel, with no new pattern or other grid lines.
C. At the bottom junction near (838,1097), a SHORT southwest branch terminates falsely near (716,1173). REMOVE ONLY this short southwest branch and its bevel, restoring the original unbroken pale gray slab surface where that short branch was. Preserve the long northwest-to-southeast main groove through the junction and the northeast branch, giving a clean T-junction. Do not extend this short southwest branch and do not move the junction. Work only near x690..875,y1060..1205.
Everything else is locked: all other complete joints including the upper vertical joints and the upper/right three-way corner; original stone texture, gray palette, light, grain and shadows; the original outer image boundary. Do not shift, straighten, tilt, widen or redraw entire existing lines. No added seams except the one explicitly missing continuation B; no extra objects, cracks, markings, words or material/color change. No crop, zoom, resizing or broad repaint. Deliver exactly the same 1254 by 1254 image with only those three local geometry corrections."""
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
promptfile=D/'prompts/group-a-v1.prompt.txt';promptfile.write_text(prompt,encoding='utf-8')
req={'id':'group-a-v1','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptFile':str(promptfile),'promptSha256':sha(promptfile),'references':[{'role':['edit-target','approved-layout','approved-detail','approved-primary-style'][i],'path':str(p),'sha256':sha(p)} for i,p in enumerate(paths)],'referenced_image_paths':[str(p) for p in paths],'sourceCrop':crop,'expectedNativePixels':[1254,1254],'tool':'builtin image_gen','actualModel':None,'actualQuality':None,'apiUsed':False}
(D/'request-v1.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'id':req['id'],'refs':len(paths),'promptSha256':req['promptSha256']}))

