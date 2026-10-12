from pathlib import Path
import json
from PIL import Image
import tile_native_workflow as w
T=w.ZONE/'r11_c10';S=T/'repairs';stem='joint-p31-p32-sharpness-v1'
box=[37261,42723,38515,43977];x,y=w.read(T/'coordinate-plan.json')['tileOrigin']
src=T/'r11_c10-candidate-4096.png';out=S/(stem+'-input.png')
Image.open(src).crop([box[0]-x,box[1]-y,box[2]-x,box[3]-y]).save(out)
w.write(out.with_suffix('.png.derivation.json'),{'operation':'unscaled native composite crop','source':str(src),'sha256':w.sha(src),'globalBox':box,'dimensions':[1254,1254],'resamplingApplied':False})
prompt="""Native detail restoration, one 1254 x 1254 image. Image 1 is the exact aligned native shipyard close-up to edit; keep all geometry and dimensions exactly. Image 2 overall layout only, 3 material/daylight style only, 4 approved Q painterly style only.
The horizontal wood crosspiece and nearby floor grain/nail heads around the upper-middle center-left of Image 1 are noticeably soft compared with the crisp right half. Repaint ONLY those soft materials at the same sharpness and polish as the surrounding native art: solid clean rounded wood edges, individually resolved controlled grain, distinct round metal nail heads. Keep every board boundary, beam silhouette, nail center, all groove endpoints and cast shadows in exactly the same place. This is material detail completion, not a geometry or design change. Do not add knots or nails, rotate boards, thicken the beam, warp edges, resize objects or change lighting/color. Preserve all outer borders. All timber remains clean rounded Q painted wood, no photorealism, no grain noise, no text/watermarks."""
refs=[str(out)]+[r['path'] for r in w.approved_refs()]
(S/(stem+'.prompt.txt')).write_text(prompt,encoding='utf-8')
w.write(S/(stem+'.request.json'),{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':{'1':'exact native edit target for local detail restoration','2':'layout only','3':'daylight material style','4':'approved primary style'},'submittedParameters':{'model':None,'quality':None},'coordinate':{'globalBox':box,'dimensions':[1254,1254]}})
print(json.dumps({'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}))

