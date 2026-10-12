import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib,datetime
z=Path(__file__).resolve().parents[1];q=z/'qa';ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
stem='r08_c06_r09_c06_repair_south_canopy_right_v1';b=[1324,3500,2578,4754];cb=[v+115 for v in b]
base=q/'pair-r08c06-r09c06-v1-context-native.png';src=q/(stem+'-source-1254.png')
assert not src.exists();im=Image.open(base).convert('RGB').crop(cb);im.save(src)
left=z/'native/r08_c06_r09_c06_repair_south_canopy_v1.png';guide=im.copy();guide.paste(Image.open(left).convert('RGB').crop((1024,0,1254,1254)),(0,0));gp=q/(stem+'-continuity-1254.png');assert not gp.exists();guide.save(gp)
trace={'guide':ref(gp),'baseCrop':ref(src),'nativeSource':ref(left),'sourceCropBox':[1024,0,1254,1254],'pasteBox':[0,0,230,1254],'nativePixelsResampled':False}
(q/(stem+'-guide-trace.json')).write_text(json.dumps(trace,indent=2),encoding='utf-8')
prompt="Edit the attached exact 1254 x 1254 native crop and output exactly one 1254 x 1254 image without shifting the camera or any contours. The left 230-pixel strip is an exact adjacent native blue canopy anchor. Continue its cloth colors, fine geometric weave and broad soft diagonal fold into the rest of the existing blue canopy. Smooth away the artificial vertical material boundary at x=230. Preserve the far RIGHT 230 pixels as the other exact material anchor: its deeper blue, diagonal weave, existing folds and silhouette must stay unchanged. Paint a natural continuous transition across the middle x=230..1024 so the left and right cloth belong to one canopy. The shallow fold and weave should change gradually with the existing canopy curvature, no hard material blocks, no abrupt patches, no new folds. Preserve the single stitched front hem and all wood architecture exactly. Do not recolor the entire crop; the outer left and right strips are fixed lighting anchors. Same crisp hand-painted isometric daylight game art. No text, no added objects, no blur."
pp=z/'native'/(stem+'.prompt.txt');pp.write_text(prompt,encoding='utf-8')
req={'stem':stem,'tile':'r08_c06/r09_c06','tool':'image_gen__imagegen','route':'builtin','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':{'tileContextBoxFromNorthTile':b,'pairContextBox':cb,'sourceContext':ref(base)},'sourceCrop':ref(src),'references':[dict(ref(gp),role='exact native overlap guide, no resizing')],'submittedParameters':{'transparent_background':False,'referenced_image_paths':[gp.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None}
(z/'native'/(stem+'.request.json')).write_text(json.dumps(req,indent=2),encoding='utf-8')
print(json.dumps(dict(req,promptText=prompt)))

