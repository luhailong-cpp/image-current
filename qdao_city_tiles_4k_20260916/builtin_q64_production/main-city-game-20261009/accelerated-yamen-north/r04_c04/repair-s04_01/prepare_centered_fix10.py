from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib
B=Path(__file__).resolve().parent; ROOT=B.parents[1]; D=B/'fix10_centered'; D.mkdir(exist_ok=False)
north=B/'fix09_centered/generated-centered.png'; south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
N=Image.open(north).convert('RGB'); S=Image.open(south).convert('RGB')
base=Image.new('RGB',(1254,1254));base.paste(N.crop((0,0,1254,627)),(0,0));base.paste(S.crop((0,115,1254,742)),(0,627))
unmasked=D/'centered-native-context.png';base.save(unmasked)
masked=base.copy();dr=ImageDraw.Draw(masked)
boxes=[(644,145,785,627),(896,450,932,627)]
for box in boxes:dr.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=(255,0,255))
guide=D/'centered-repair-mask.png';masked.save(guide)
prompt='''Edit image 1. Restore the magenta missing areas with the stone rail that belongs there. Image 2 is the unmasked native scene for reference. Same 1254x1254 framing and pixel scale.
The bottom half below y627 is finished correct art: do not change it. Continue its EXACT geometry and values into the missing areas above. In particular, the left bevel of the long pale rail is a broad COOL GRAY face, with a narrow bright inner ridge and fine dark groove. The gray face visible at x670..725 below the horizontal center must continue UPWARD through the large magenta opening, with its same gray hue and shading at y627; let it gradually meet the existing upper stone around y145. Do not replace that gray face with ivory stone. The slim second missing area is the rail's right inset groove around x917: join that groove accurately without lateral steps or a horizontal notch. Remove all magenta by reconstructing stone.
No horizontal seam, no zigzag color edge, no notch at y627, no blurred transition. Preserve the rail's right silhouette around x1004, step edges, left green carving, pale coping, wall-panel lines and the rest of the image. Keep the entire lower half exactly as in the provided scene; no re-lighting, reframing, new ornament, text or objects. Output fully opaque at the same 1254x1254 native size.'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
params={'prompt':prompt,'referenced_image_paths':[str(guide),str(unmasked)],'transparent_background':False}
rec={'kind':'centered_native_context_with_repair_mask','worldBox':[12173,15757,13427,17011],'width':1254,'height':1254,'formalSeamLocalY':627,
 'sources':[{'file':str(north),'sha256':sha(north),'worldBox':[12173,15757,13427,17011],'crop':[0,0,1254,627],'targetBox':[0,0,1254,627]}, {'file':str(south),'sha256':sha(south),'worldBox':[12173,16269,13427,17523],'crop':[0,115,1254,742],'targetBox':[0,627,1254,1254]}],
 'maskBoxes':boxes,'maskRGB':[255,0,255],'maskPurpose':'Guide only. Removed by imagegen; no code-painted art is selected for final.',
 'sourceOperation':'Exact native crop and paste, no resizing','references':[{'file':str(p),'sha256':sha(p)} for p in [guide,unmasked]],'actualModel':None,'actualQuality':None}
for name,data in [('parameters.json',params),('preparation.json',rec)]: (D/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(str(D))
