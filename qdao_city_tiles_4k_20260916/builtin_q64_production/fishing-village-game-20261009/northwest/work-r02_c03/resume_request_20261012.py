from resume_prepare_20261012 import W,D,sha,write,nb,target
from datetime import datetime,timezone

n='r02_r03_roof_connector_v02'
P='D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009'
refs=[str(target).replace('\\','/'),P+'/donghai-natural-stone-clear-routes-v10.png',P+'/donghai-natural-stone-detail-v1.png',P+'/user-references-20261009/mail-daoist-style.jpg']
roles=['EDIT TARGET: exact native currently assembled blue-roof connector; geometry and camera lock','REFERENCE: whole fishing-village layout only','REFERENCE: material detail only','PRIMARY REFERENCE: Q-style Daoist game painting']
prompt='''Use case: precise-object-edit
Asset type: exact native 1254x1254 local repair for a 57344x57344 isometric daylight Q-style Daoist fishing-village map.
Input images: Image 1 is the EDIT TARGET, the exact current local roof connector; image 2 is whole-village LAYOUT ONLY; image 3 is material-detail reference; image 4 is the PRIMARY Q-style Daoist painting reference.
Primary request: Correct only the visible source-join artifacts in the blue ceramic roof. Near the middle of image 1, several diagonal cylindrical tile rows show misregistered dark rims, doubled rim lines, thin pale ghost slivers, and small vertical rectangular joins. Make the existing blue barrel tiles continue as single clean, continuous diagonal cylinders with one consistent rim per tile, following the geometry and spacing that already exist on both sides. Keep the lower blue tile end caps smooth and aligned along the same orange wooden eave.
Composition/framing: exactly preserve image 1 framing, camera, perspective, roof silhouette, tile diameter, number and direction of diagonal rows, existing blue ridge at upper right, orange wooden beam, wall, supporting timber, red lantern, and shadows.
Lighting/materials: retain existing warm daylight, deep azure glazed ceramic, hand-painted Q-style texture and scale, orange wood and gold details.
Constraints: return a 1254x1254 opaque PNG at native dimensions. Change only the damaged blue ceramic tile connectors and their tiny adjacent shadows. Preserve the exterior 160-pixel border and all non-blue architecture exactly as in image 1. No overall restyling, no camera shift, no new tile rows, no new objects, no text or watermark. Do not reproduce the central assembly seam or doubled dark lines.'''
pp=D/(n+'.prompt.txt');pp.write_text(prompt,encoding='utf8')
rp=D/(n+'.request.json')
write(rp,{'requestedAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','globalNativeBox':nb,'promptFile':str(pp),'prompt':prompt,'referenced_image_paths':refs,'referenceRoles':roles,'references':[{'file':p,'role':r,'sha256':sha(p)} for p,r in zip(refs,roles)],'transparent_background':False,'actualModel':None,'actualQuality':None,'modelQualityReason':'Built-in tool exposes no model or quality selectors; no metadata inference.'})
print(str(rp))
