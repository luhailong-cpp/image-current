from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,numpy as np
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012');T=D/'blue-infill-control-left-v06';T.mkdir(exist_ok=True)
src=D/'integrated-local-v10/r12_c05.candidate.context.png';box=[2560,2160,3814,3414];clean=Image.open(src).convert('RGB').crop(box);clean.save(T/'clean-original-support.png');a=np.array(clean).astype('int16');qa=np.array(clean).copy();mask=np.zeros((1254,1254),dtype='uint8');profiles=[]
for x in range(1254):
 desired=1080-1250/1765*x
 col=a[:,x];ys=np.where((col[:,2]-col[:,0]>5)&(col[:,2]>col[:,1]))[0];old=int(ys[0]);top=max(0,int(min(old-6,desired))-18);bottom=min(1253,int(max(old,desired))+18)
 for y in range(top,bottom+1):
  qa[y,x]=(255,0,255) if y<desired else (0,255,255);mask[y,x]=255
 if x in [0,200,400,600,680,800,1000,1253]:profiles.append({'x':x,'desiredThinEdgeY':desired,'originalFirstBlueY':old,'QAControlRows':[top,bottom]})
# Expand annotation neighborhood mechanically so the old bevel corner is fully covered.
mask=np.array(Image.fromarray(mask).filter(ImageFilter.MaxFilter(51)))
for x in range(1254):
 desired=1080-1250/1765*x
 ys=np.where(mask[:,x]>0)[0]
 for y in ys:qa[y,x]=(255,0,255) if y<desired else (0,255,255)
Image.fromarray(qa).save(T/'input.png');Image.fromarray(mask).save(T/'QA-control-corridor-not-final.png')
prompt='''Use case: precise-object-edit. Inpaint only the temporary two-color annotation corridor in image1 at native1254x1254. Image2 approved city layout, image3 natural stone detail, image4 approved Daoist style; image5 is the unannotated original for unchanged texture, material, grout and roof.
The magenta and cyan are temporary inpainting labels, not art. Replace all MAGENTA pixels with the adjacent CREAM paving texture. Replace all CYAN pixels with the adjacent MUTED BLUE-GRAY paving texture. The exact straight interface between these two annotation colors is the required finished cream/blue boundary. Render a thin groove and cream bevel precisely on that interface, while respecting the exact existing marked coordinates: left endpoint(0,1080), right endpoint(1253,193). Cream above, blue below. Do not move the interface or shrink the cream band. The annotations fully cover the old disconnected fragments and notch; all of those old fragments must disappear in favor of this one boundary.
Keep all unannotated source pixels exactly like image5, including upper gray/cream band, unrelated descending joints, roof gold/teal silhouette and its colors. The existing descending grout ends cleanly at the corrected cream/blue boundary, without moving the source joint elsewhere. Match the original natural brush texture, quiet stone, line weight and daylight. Preserve native pixel scale. Return exactly1254x1254; no magenta, cyan, red, guide line, rectangle, text, new object, layout shift or rescaling. The only change is natural painted cream/blue material and its continuous thin boundary within the temporary corridor.'''
(T/'prompt.txt').write_text(prompt,encoding='utf-8');(T/'input-derivation.json').write_text(json.dumps({'sourceContext':{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()},'cropContextBox':box,'annotationOnly':True,'annotationNeverCopiedToFinal':True,'controlMethod':'two-color QA inpaint corridor at shared true native anchor line; generated source required for every final copied pixel','sharedContextLineAnchors':[[2560,3240],[4325,1990]],'profiles':profiles,'sourceResampling':False,'maximumFeatherPixels':2},ensure_ascii=False,indent=2),encoding='utf-8');print(str(T))
