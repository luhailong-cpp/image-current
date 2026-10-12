from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g=R/'guides/r12_c13_p31.native-context-v03.png';m=read(Path(str(g)+'.generation.json'));im=Image.open(g).convert('RGB')
body=R/'native/r12_c13_p31_v02.png';im.paste(Image.open(body).convert('RGB').crop((230,230,1024,850)),(230,230))
o=R/'native/r12_c12_board_end_joint_v01.png';im.paste(Image.open(o).convert('RGB').crop((1024,256,1254,1139)),(0,0))
west=R/'tiles/r12_c12.candidate-sol-20261012-v01.png';im.paste(Image.open(west).convert('RGB').crop((3981,1933,4096,3187)),(0,0))
n=R/'native/r12_c13_p21_v02.png';im.paste(Image.open(n).convert('RGB').crop((0,1024,1254,1254)),(0,0));im.save(g)
m['sha256']=sha(g);m['derivedFrom'].extend([{'file':body.as_posix(),'sha256':sha(body),'role':'upper native complete T end joint only'},{'file':o.as_posix(),'sha256':sha(o),'role':'accepted west whole-board overlay'},{'file':west.as_posix(),'sha256':sha(west),'role':'adopted exact west 115 core strip; candidate pixel source proof verified by root'}])
m['placements'].extend([{'source':body.as_posix(),'sourceCrop':[230,230,1024,850],'destination':[230,230],'resampled':False},{'source':o.as_posix(),'sourceCrop':[1024,256,1254,1139],'destination':[0,0],'resampled':False},{'source':west.as_posix(),'sourceCrop':[3981,1933,4096,3187],'destination':[0,0],'resampled':False},{'source':n.as_posix(),'sourceCrop':[0,1024,1254,1254],'destination':[0,0],'resampled':False}]);m['usableAsFinalArt']=False;write(Path(str(g)+'.generation.json'),m)
p=R/'prompts/r12_c13_p31_v03.request.json';d=read(p);d['references'][0]['sha256']=sha(g);write(p,d)
print(json.dumps({'guide':g.as_posix(),'sha256':sha(g)}))
for x in [0,114,115,229,1024,1138]:
 runs=[];s=None
 for y in range(850,1254):
  px=im.getpixel((x,y));dark=max(px)<110
  if dark and s is None:s=y
  elif not dark and s is not None:runs.append([s,y-1]);s=None
 if s is not None:runs.append([s,1253])
 print(x,runs)

