from production import *
from datetime import datetime,timezone
D=W/'resume-20261012-v1';n='r02_r03_roof_west_bridge_v02';target=D/'neighbor-qa/west-roof-current-proposed.png';b=[7565,8077,8819,9331]
refs=[str(target).replace('\\','/')]+[str(p).replace('\\','/') for p in REFS]
roles=['EDIT TARGET: exact native current west roof junction, includes actual adopted west neighbor and current r02/r03 proposed roof','REFERENCE: whole village layout only','REFERENCE: material detail only','PRIMARY REFERENCE: Q-style Daoist game painting']
prompt='''Use case: precise-object-edit
Asset type: exact native 1254x1254 local west roof-junction repair for a daylight isometric Q-style Daoist fishing-village map.
Input images: Image 1 is the EDIT TARGET composed from actual current native pixels; image 2 is whole-village LAYOUT ONLY; image 3 is material detail; image 4 is the PRIMARY Q-style Daoist painting reference.
Primary request: Repair only the blue ceramic tile misalignment at the straight vertical source join near x=512 in image 1. Existing diagonal cylindrical tile rows on either side must become continuous single blue barrel tiles with one matching rim line. Eliminate clipped cylinders, doubled rims, thin white slivers and abrupt angular shifts at that central vertical join. The corrected cylinders must follow the existing rows on both sides and preserve the blue tile end-cap positions along the same orange wooden eave.
Composition/materials: keep exactly the same camera, crop, roof silhouette, diagonal rows, tile sizes, blue glaze, warm daylight, orange wooden eave, supporting timber, wall and window. Maintain the original hand-painted Q-style texture.
Constraints: output an opaque 1254x1254 PNG. Confine repairs to the narrow damaged blue ceramic connector around x=380..720,y=160..850 and tiny existing roof shadows. Preserve all exterior 160-pixel borders and all non-blue architecture exactly. Preserve the row direction, number and spacing; no whole-roof rephasing or shifts, no additional rows, no added objects, no text, no watermark.'''
pp=D/(n+'.prompt.txt');pp.write_text(prompt,encoding='utf8')
write(D/(n+'.request.json'),{'requestedAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','globalNativeBox':b,'promptFile':str(pp),'prompt':prompt,'referenced_image_paths':refs,'referenceRoles':roles,'references':[{'file':p,'role':r,'sha256':sha(p)} for p,r in zip(refs,roles)],'transparent_background':False,'actualModel':None,'actualQuality':None,'modelQualityReason':'Built-in exposes no model/quality selectors or actual response metadata.'})
print(str(D/(n+'.request.json')))
