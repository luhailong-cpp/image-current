from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g=R/'guides/r12_c13_p31.native-edit-v05.png';m=read(Path(str(g)+'.generation.json'));im=Image.open(g).convert('RGB')
body=R/'tiles/r12_c13.candidate-sol-20261012-v01.png';im.paste(Image.open(body).convert('RGB').crop((0,2048,1024,3072)),(115,115))
o=R/'native/r12_c12_board_end_joint_v01.png';w=R/'native/r12_c12_p34_v02.png';n=R/'native/r12_c13_p21_v02.png';e=R/'native/r12_c13_p32_v01.png'
for p,c,dest in [(w,(1024,0,1254,1254),(0,0)),(o,(1024,256,1254,1139),(0,0)),(e,(0,0,230,1254),(1024,0)),(n,(0,1024,1254,1254),(0,0))]:
 im.paste(Image.open(p).convert('RGB').crop(c),dest)
 m['placements'].append({'source':p.as_posix(),'sourceCrop':c,'destination':dest,'resampled':False})
m['derivedFrom'].extend([{'file':body.as_posix(),'sha256':sha(body),'role':'native pixel-derived coherent lower board body; guide internal end joint requires native correction'},{'file':o.as_posix(),'sha256':sha(o),'role':'accepted exact west overlay'}])
im.save(g);m['sha256']=sha(g);m['usableAsFinalArt']=False;write(Path(str(g)+'.generation.json'),m)
p=R/'prompts/r12_c13_p31_v05.request.json';d=read(p);d['references'][0]['sha256']=sha(g)
pp=Path(d['promptPath']);pp.write_text("""Use case: precise-object-edit. Edit image 1 into the SAME 1254-square native hand-painted golden wood dock crop. Last three references give layout, materials and painting style only. Preserve left230, right230 and top230 pixels and every outer edge endpoint exactly.
Repair ONLY the broken complete plank-end seam at native x310..365,y600..690. The upper short end joint shifts sideways at a horizontal source boundary near y634. Rebuild this entire perpendicular end connection between the adjacent actual long black board grooves as one physically coherent continuous seam; its ends must meet the long board edges as proper T junctions. No disconnected notch, floating endpoint or horizontal rectangle edge.
Keep every other plank, gap, complete end joint, wood grain, color, camera and crop unchanged. No extra rows, props, rail or text. One opaque square.""",encoding='utf-8');write(p,d)
print(json.dumps({'guide':g.as_posix(),'sha256':sha(g)}))

