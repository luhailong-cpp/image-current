from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':str(p),'sha256':sha(p)}
paths={'p24':B/'native/r06_c12_p24-v2.png','p33':B/'native/r06_c12_p33-v1.png','p43':B/'native/r06_c12_p43-v1.png','p34':B/'native/resume-20261010-stall-upper-v1.png','p44':B/'native/resume-20261010-stall-lower-v1.png'}
images={k:Image.open(v).convert('RGB') for k,v in paths.items()}
out=[]
for a,b,d in [('p24','p34','h'),('p33','p34','v'),('p34','p44','h'),('p43','p44','v')]:
 im=Image.new('RGB',(1254,256) if d=='h' else (256,1254))
 if d=='h':im.paste(images[a].crop((0,1011,1254,1139)),(0,0));im.paste(images[b].crop((0,115,1254,243)),(0,128))
 else:im.paste(images[a].crop((1011,0,1139,1254)),(0,0));im.paste(images[b].crop((115,0,243,1254)),(128,0))
 p=B/f'qa/resume-20261010-stall-final-{a}-{b}.native-1to1.png';im.save(p);out.append(rec(p))
 Path(str(p)+'.derived.json').write_text(json.dumps({'purpose':'native 1:1 core-boundary QA','sources':[rec(paths[a]),rec(paths[b])],'orientation':d,'joint':128,'resized':False},indent=2)+'\n',encoding='utf-8')
 joint=Image.new('RGB',(1254,2278));joint.paste(images['p34'].crop((0,0,1254,1139)),(0,0));joint.paste(images['p44'].crop((0,115,1254,1254)),(0,1139));jp=B/'qa/resume-20261010-stall-final-joint.native-1to1.png';joint.save(jp)
 Path(str(jp)+'.derived.json').write_text(json.dumps({'purpose':'native stitched proposal only','sources':[rec(paths['p34']),rec(paths['p44'])],'operation':'opaque native core cut1139; bottom source cropped top115; no resizing'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stripes':out,'joint':str(jp)}))
