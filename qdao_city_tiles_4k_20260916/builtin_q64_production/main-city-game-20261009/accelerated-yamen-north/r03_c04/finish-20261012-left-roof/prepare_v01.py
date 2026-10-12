from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
O=Path(__file__).resolve().parent
B=O.parent/'candidate/r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B).startswith('424e41dd0ce0')
box=[453,493,1707,1747]
im=Image.open(B).convert('RGB'); assert im.size==(4096,4096)
context=im.crop(box)
V=O/'v01';V.mkdir(exist_ok=True)
context.save(V/'context-native.png')
context.crop((90,455,875,785)).save(V/'before-qa-native.png')
mask=context.convert('RGBA'); mask.paste((0,0,0,0),(130,515,825,725));mask.save(V/'edit-guide-transparent.png')
prompt='''Use case: precise-object-edit. Edit this 1254 x 1254 original-pixel game roof texture; return exactly 1254 x 1254. Image 1 is the complete edit target. Image 2 is the same image with a transparent repair window, a LOCATION GUIDE only. Fill/reconstruct ONLY the local band x130..825, y515..725 in image coordinates. Everything outside it, including tile scale, rows, gutters, camera and lighting, must remain fixed.

Repair two adjacent broken ceramic roof junctions in that band. The turquoise barrel roof tiles have impossible sharp triangular shoulders, two overlapping cap curves and interrupted dark gutters where the current composite row joins. Reconstruct the few defective upper lips/caps as smoothly rounded, physically lapped ceramic tiles. Follow the visible exact gutter centerlines above AND below the repair; gently join those existing lines across the small band without shifting either anchor. Each barrel has one rounded lip, no doubled rim, no triangular flap, no pasted square. Carry the existing vertical glossy highlights through naturally. Make these few repaired tile joints indistinguishable in drawing style and color from the already intact joints nearby.

Keep all roof tiles outside the narrow repair window exactly as supplied. Do not redraw or move the lower row, rotate the roof, alter the tile count or tile width, add roof edges, gold ornament, sky, letters, borders or decorative patterns. This is a local geometric restoration, not a new roof design. The output is the opaque completed original composition with the repaired window; do not include the guide transparency.'''
params={'prompt':prompt,'referenced_image_paths':[str(V/'context-native.png'),str(V/'edit-guide-transparent.png')],'transparent_background':False}
(V/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8')
(V/'prompt.txt').write_text(prompt,encoding='utf-8')
(V/'preparation.json').write_text(json.dumps({'createdAt':datetime.now(timezone.utc).isoformat(),'base':{'file':str(B),'sha256':sha(B),'pixels':[4096,4096]},'contextTileBox':box,'contextWorldBox':[box[0]+12288,box[1]+8192,box[2]+12288,box[3]+8192],'ownedTileROIs':[[583,1008,943,1218],[903,1008,1278,1218]],'repairContextBox':[130,515,825,725],'referenceSources':[{'file':p,'sha256':sha(Path(p))} for p in params['referenced_image_paths']],'oldROIFailuresNotUsed':True,'actualModel':None,'actualQuality':None,'resampled':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'baseSHA':sha(B),'context':str(V/'context-native.png'),'params':str(V/'parameters.json')}))
