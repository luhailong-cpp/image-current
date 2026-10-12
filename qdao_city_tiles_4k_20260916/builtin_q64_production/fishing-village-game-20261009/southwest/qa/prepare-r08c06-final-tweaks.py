import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Revised native request for exact small fascia fault.
j=rd(Z/'native/r08_c06_repair_f_goldedge_v1.request.json');j['stem']='r08_c06_repair_f_goldedge_v2'
p='Use case: precise-object-edit. Edit this exact native 1254x1254 game-art crop. Make an extremely small local repair ONLY within x=510..690,y=435..605: remove the little 3-pixel step in the diagonal gold platform rim at x=620,y=485 and the faint vertical join in its fascia immediately below. Connect each existing thin diagonal highlight with its exact original endpoints. Preserve every pixel outside this small rectangle, including the bracket at x=760, the complete front edge to left and right, every plank, the blue cloth and wooden pillars. Do not move, thicken, straighten or redesign the long beam or bracket. Retain the existing wood texture, light and perspective. Exact same image dimensions and framing, no blur, text, grid or watermark.'
pp=Z/'native/r08_c06_repair_f_goldedge_v2.prompt.txt';pp.write_text(p,encoding='utf-8');j['prompt']=pp.as_posix();(Z/'native/r08_c06_repair_f_goldedge_v2.request.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
# Native crop of the independent upper paving focus discontinuity.
j=rd(Z/'native/r08_c06_repair_a_lantern_v1.request.json');j['stem']='r08_c06_repair_h_upperpaving_v1';b=[2300,-115,3554,1139];cb=[v+115 for v in b]
src=Z/'qa/repair-r08_c06-h_upperpaving-source-1254.png';Image.open(Z/'qa/full-tile-r08_c06-context-native.png').crop(cb).save(src)
j['coordinates']['tileContextBox']=b;j['coordinates']['contextBox']=cb
j['references']=[{'path':src.as_posix(),'sha256':sha(src),'dimensions':[1254,1254],'role':'exact native upper paving edit target'}];j['submittedParameters']['referenced_image_paths']=[src.as_posix()]
p='Use case: precise-object-edit. Edit this exact native 1254x1254 game-art crop. Repair ONLY the abrupt straight vertical change in stone-paving sharpness and small mortar-line offsets near local x=650, from the top edge down to the lantern. Continue the same existing slab joints across that vertical seam with matching clear softly painted stone texture on both sides. The left paving is the fixed detail-style anchor; restore matching focus to the narrow blurry strip at the join, without making hard noisy outlines. Preserve every paving slab shape and location, shadows, lantern, gold beam, wood post and blue canopy. Do not change any object or framing. Do not fix the separate lantern lower-tip fault in this request. Exact 1254x1254; no text, grid, watermark or lens blur.'
pp=Z/'native/r08_c06_repair_h_upperpaving_v1.prompt.txt';pp.write_text(p,encoding='utf-8');j['prompt']=pp.as_posix();(Z/'native/r08_c06_repair_h_upperpaving_v1.request.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')

