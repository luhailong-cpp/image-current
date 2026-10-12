from pathlib import Path
from PIL import Image
import hashlib,json,sys,os
from datetime import datetime,timezone
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid,source,x,y,description=sys.argv[1:];x=int(x);y=int(y);source=R/'tiles'/source
im=Image.open(source).convert('RGB');assert 0<=x and 0<=y and x+1254<=4096 and y+1254<=8192
if y+1254>4096:
 neighbor=R/os.environ.get('ISLAND_R08_NEIGHBOR_FILE','tiles/r09_c12.candidate-v02.png')
 extended=Image.new('RGB',(4096,8192));extended.paste(im,(0,0));extended.paste(Image.open(neighbor).convert('RGB'),(0,4096));im=extended
guide=R/'guides'/f'{pid}.native-context.png';im.crop((x,y,x+1254,y+1254)).save(guide)
guide_record={'file':str(guide),'sha256':sha(guide),'operation':'mechanical native candidate crop, no resize','source':str(source),'sourceSha256':sha(source),'sourceCrop':[x,y,x+1254,min(4096,y+1254)]}
if y+1254>4096:
 guide_record['bottomNeighbor']={'file':str(neighbor),'sha256':sha(neighbor),'sourceCrop':[x,0,x+1254,y+1254-4096],'destination':[0,4096-y]}
write(Path(str(guide)+'.generation.json'),guide_record)
refs=[{'file':str(guide),'sha256':sha(guide),'role':'EDIT TARGET: exact native candidate crop; no resize, repositioning or object addition'}]+read(R/'references.json')
prompt='Use case: precise-object-edit. Edit attached image1, a native1254x1254 exact unscaled crop of our daylight Q Daoist game map. Return native1254x1254. Last three images are full map for layout only, material detail only, approved painting style only. Do not reconstruct full map or UI. Keep outer115pixels on all four sides unchanged; exact native world position must remain fixed. Repair only the described central seam defects while keeping all existing objects, scale, colors and coordinates. No blur, feathering, photographic depth of field, new structures, characters, text or watermark. '+description+' Single opaque square. The map core is [115,115,1139,1139]; the core returns to tile-local['+str(x+115)+','+str(y+115)+']. Global native extent['+str(45056+x)+','+str(28672+y)+','+str(45056+x+1254)+','+str(28672+y+1254)+'].'
pf=R/'prompts'/f'{pid}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
req={'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'nativeTileBox':[x,y,x+1254,y+1254],'baseCandidate':str(source),'baseCandidateSha256':sha(source)}
write(R/'prompts'/f'{pid}.request.json',req)
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))

