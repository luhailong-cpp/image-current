from workflow import ROOT,read,write,sha,patch,context,now
from pathlib import Path
from PIL import Image
import sys
pid,ver,base,note=sys.argv[1:5];neighbors=sys.argv[5:]
assert pid[:7] in ['r13_c13','r14_c13','r13_c14','r12_c14']
if base=='layout':
 context(pid,neighbors,ver);guide=ROOT/'guides'/f'{pid}.native-context-{ver}.png'
else:
 guide=ROOT/'guides'/f'{pid}.precise-edit-{ver}.png';assert not guide.exists();bp=ROOT/'native'/base;im=Image.open(bp).convert('RGB');box=patch(pid)['nativeGlobalBox'];parts=[{'file':str(bp),'sha256':sha(bp),'role':'native edit body'}]
 for name in neighbors:
  np=ROOT/'native'/name;nb=read(Path(str(np)+'.generation.json'))['coordinate']['nativeGlobalBox'];inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])];crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(Image.open(np).convert('RGB').crop(crop),dest);parts.append({'file':str(np),'sha256':sha(np),'sourceCrop':crop,'destination':dest})
 im.save(guide);write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'derivedFrom':parts,'usableAsFinalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'ONLY edit target; exact composition and crop'}]+read(ROOT/'references.json')
prompt='Use case: precise-object-edit. Edit ONLY image 1, at its identical exact crop and scale. Deliver one opaque 1254 x 1254 square. It is a greatly magnified SMALL game-map patch, not a map overview. Image 1 is the ONLY composition authority. Keep its sharp native overlaps in exactly the same place and perspective. Replace its blurry areas with clean, matching native hand-painted detail, and unify any pasted guide border without shifting objects. Reference images 2, 3 and 4 are solely context for materials and style: never copy their full buildings, islands, miniatures, people, UI or composition into this crop. '+note+' Preserve clean daylight, polished warm wood, elegant Daoist Q painting, clean turquoise sea ripples at the scale in image 1. No extra objects, invented buildings, miniature structures, people, words, numbers, diagram lines or watermark. Output the whole original square, not a comparison.'
pp=ROOT/'prompts'/f'{pid}_{ver}.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8');req={'promptPath':str(pp),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}};write(ROOT/'prompts'/f'{pid}_{ver}.request.json',req);args={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False};write(ROOT/'prompts'/f'{pid}_{ver}.args.json',args);print(guide)
