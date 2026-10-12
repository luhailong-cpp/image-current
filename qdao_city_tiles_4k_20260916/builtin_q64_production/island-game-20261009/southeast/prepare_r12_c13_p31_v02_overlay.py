from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g=R/'guides/r12_c13_p31.native-edit-v02.png';m=read(Path(str(g)+'.generation.json'))
o=R/'native/r12_c12_board_end_joint_v01.png';assert sha(o)=='c6ed7435ab327e141d940883a4ec28ca947dbee935e27303da4dd33dbf1e9a00'
im=Image.open(g).convert('RGB');im.paste(Image.open(o).convert('RGB').crop((1024,256,1254,1139)),(0,0))
n=R/'native/r12_c13_p21_v02.png';im.paste(Image.open(n).convert('RGB').crop((0,1024,1254,1254)),(0,0));im.save(g)
m['sha256']=sha(g);m['derivedFrom'].append({'file':o.as_posix(),'sha256':sha(o),'role':'accepted whole-board west overlap authority'});m['placements'].extend([{'source':o.as_posix(),'sourceCrop':[1024,256,1254,1139],'destination':[0,0],'resampled':False},{'source':n.as_posix(),'sourceCrop':[0,1024,1254,1254],'destination':[0,0],'note':'north final precedence','resampled':False}]);m['usableAsFinalArt']=False;write(Path(str(g)+'.generation.json'),m)
p=R/'prompts/r12_c13_p31_v02.request.json';d=read(p);d['references'][0]['sha256']=sha(g);write(p,d)
print(json.dumps({'guide':g.as_posix(),'sha256':sha(g)}))

