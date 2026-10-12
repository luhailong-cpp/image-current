from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r02_c03';D=W/'resume-20261012-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,a:Path(p).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
n='r02_c03_stair_rail_join_v02';target=D/'stair-rail-join.target.png';box=[8704,4403,9958,5657]
write(str(target)+'.derivation.json',{'file':str(target),'sha256':sha(target),'globalNativeBox':box,'source':str(D/'composition-v1/full-pair.png'),'sourceSha256':sha(D/'composition-v1/full-pair.png'),'sourceCropBox':[627,422,1881,1676],'resampled':False,'role':'actual native edit target at stair/rail stone and planting join'})
P='D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009'
refs=[str(target).replace('\\','/'),P+'/donghai-natural-stone-clear-routes-v10.png',P+'/donghai-natural-stone-detail-v1.png',P+'/user-references-20261009/mail-daoist-style.jpg']
roles=['EDIT TARGET: exact current native stair and rail junction; geometry lock','REFERENCE: whole village layout only','REFERENCE: material detail only','PRIMARY REFERENCE: Q-style Daoist game painting']
prompt='''Use case: precise-object-edit
Asset type: exact native 1254x1254 local repair for a daylight isometric Q-style Daoist fishing-village game map.
Input images: Image 1 is the actual EDIT TARGET; image 2 is whole-village LAYOUT ONLY; image 3 supplies material detail; image 4 is the PRIMARY Q-style Daoist painting reference.
Primary request: Repair only the straight vertical assembly artifact near x=627 in image 1, from about y=220 to y=850, where the gray stair stone, gray rail-post foundation, small natural rocks, ground plants and curb abruptly change at a perfectly vertical source boundary. Make this a coherent physical meeting of the stairs with the existing rocks and plants: remove the chopped rectangular halves of rocks and curb, give the stair's left stone boundary its natural perspective, and connect the existing gray stone surfaces and tiny greenery without a visible straight cut. Preserve the exact stair step count, elevations and tread placement, the left tall wooden rail post, the short upper wooden rail post, the round stone pillar base, and every existing object.
Style/lighting: retain the same bright warm daylight, hand-painted material texture, natural gray/cyan stone and orange wooden rails.
Constraints: output an opaque 1254x1254 PNG at native dimensions. Restrict changes to the narrow damaged join around x=540..730,y=220..850 and its tiny existing shadow. Keep the exterior 180-pixel border, camera, framing, all non-junction paving lines and all rail beams unchanged. No added architectural elements, no new planting, no text or watermark.'''
pp=D/(n+'.prompt.txt');pp.write_text(prompt,encoding='utf8')
write(D/(n+'.request.json'),{'requestedAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','globalNativeBox':box,'promptFile':str(pp),'prompt':prompt,'referenced_image_paths':refs,'referenceRoles':roles,'references':[{'file':p,'role':r,'sha256':sha(p)} for p,r in zip(refs,roles)],'transparent_background':False,'actualModel':None,'actualQuality':None,'modelQualityReason':'Built-in tool exposes no model or quality selectors; no metadata inference.'})
print(str(D/(n+'.request.json')))
