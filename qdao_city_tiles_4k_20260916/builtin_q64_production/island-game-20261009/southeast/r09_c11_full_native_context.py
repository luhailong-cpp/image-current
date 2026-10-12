from pathlib import Path
import json
from PIL import Image
from workflow import ROOT,read,write,sha,patch
pid='r09_c11_p43';name='r09_c11_p43_v03'
base=ROOT/'native'/f'{pid}_v01.png';img=Image.open(base).convert('RGB');box=patch(pid)['nativeGlobalBox'];sources=[{'file':base.as_posix(),'sha256':sha(base),'role':'original native target; preserve chime/frame/geometry'}];placements=[]
for n in ['r09_c11_p44_v01.png','r09_c11_p42_v01.png','r09_c11_p33_v01.png']:
 np=ROOT/'native'/n;nb=read(Path(str(np)+'.generation.json'))['coordinate']['nativeGlobalBox'];im=Image.open(np)
 inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
 crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
 img.paste(im.crop(crop),tuple(dest));placements.append({'file':np.as_posix(),'sourceCrop':crop,'destination':dest});sources.append({'file':np.as_posix(),'sha256':sha(np)})
out=ROOT/'guides'/f'{pid}.native-context-v03.png';assert not out.exists();img.save(out);write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'operation':'unscaled adjacent native border strips pasted into original native target; no resize painting or alteration','derivedFrom':sources,'placements':placements})
refs=[{'file':out.as_posix(),'sha256':sha(out),'role':'actual native target with immutable neighbor bands'}]+read(ROOT/'references.json')
prompt='Edit the first attached image, an existing native1254 game art crop. Keep its framing and all objects absolutely unchanged. There is a vertical stitch line at x1024, ONLY in the pale stone steps on the RIGHT. Make the short stone step contour and texture segments around x950-1070 join the fixed right border x1100-1254 exactly. Preserve the large gold disc, orange upright timber pole extending beyond the bottom edge, horizontal orange lower rail, their current silhouettes and placements pixel for pixel. No new foot, support, ornament, bracket or object. Do not terminate the upright pole above the bottom. Do not move any geometry on the top or left. Original bottom edge geometry is fixed. Repair only the local stair discontinuity and its light/shadow while retaining all original stone blocks. Last three references are layout, material, approved painting style; same bright daytime rounded Q Daoist painting. No text, UI, people or watermark. Output one opaque square of the same1254 size.'
pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8');write(ROOT/'prompts'/f'{name}.request.json',{'promptPath':pf.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))

