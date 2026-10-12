from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'processed/joint-stairs';O.mkdir(parents=True,exist_ok=True)
src=R/'processed/colorpass/p24-colorpass.png';joint=R.parent/'r12_c10/repairs/west-stairs-joint-v2.png'
a=np.array(Image.open(src));b=np.array(Image.open(joint));out=a.copy()
# Original selected p24 world origin (35725,45965); joint origin (36237,45965).
# Keep the full lowest stair geometry and cut below it on the deck, using native pixels.
out[115:1254,592:1254]=b[115:1254,80:742]
p=O/'p24-stairs-joint-v2-candidate.png';Image.fromarray(out).save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d={'status':'provisional_geometry_candidate_not_selected','file':str(p),'sha256':sha(p),'derivedFrom':[{'file':str(src),'sha256':sha(src),'role':'selected original'},{'file':str(joint),'sha256':sha(joint),'role':'builtin common joint repair'}],'jointNativeCrop':[80,115,742,1254],'p24Destination':[592,115,1254,1254],'worldBox':[36317,46080,36979,47219],'coordinateShift':[0,0],'resampling':False,'pixelBlending':False,'formalAccepted':False}
(O/'p24-stairs-joint-v2-candidate.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
Image.fromarray(out[:,464:720]).save(O/'left-cut-100pct.png')
Image.fromarray(out[0:256,500:1254]).save(O/'top-cut-100pct.png')
# Full current candidate with only this provisional change, plus neighboring internal strips.
sel=json.loads((R/'selected-patches.json').read_text())['patches'];cv=np.zeros((4096,4096,3),np.uint8)
replacements={'p24':out}
for pid,dbox,sbox in [('p14',(592,1139,1254,1254),(80,115,742,230)),('p34',(592,0,1254,230),(80,1024,742,1254))]:
 orig=R/sel[pid];v=np.array(Image.open(orig));x,y,xx,yy=dbox;sx,sy,sxx,syy=sbox;v[y:yy,x:xx]=b[sy:syy,sx:sxx];replacements[pid]=v
 path=O/(pid+'-stairs-joint-v2-candidate.png');Image.fromarray(v).save(path)
 rec={'status':'provisional_geometry_candidate_not_selected','file':str(path),'sha256':sha(path),'derivedFrom':[{'file':str(orig),'sha256':sha(orig)},{'file':str(joint),'sha256':sha(joint)}],'jointNativeCrop':list(sbox),'destination':list(dbox),'coordinateShift':[0,0],'resampling':False,'pixelBlending':False,'formalAccepted':False}
 Path(str(path)+'.derivation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
manifest={'status':'provisional_not_selected','tile':R.name,'worldBox':[36317,46080,36979,47219],'replacements':{pid:str((O/(pid+'-stairs-joint-v2-candidate.png')).relative_to(R)) for pid in replacements}}
(O/'provisional-selection.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for pid,rel in sel.items():
 v=replacements[pid] if pid in replacements else np.array(Image.open(R/rel));rr=(int(pid[1])-1)*1024;cc=(int(pid[2])-1)*1024;cv[rr:rr+1024,cc:cc+1024]=v[115:1139,115:1139]
for name,box in [('p14-p24',(3072,896,4096,1152)),('p24-p34',(3072,1920,4096,2176))]:Image.fromarray(cv).crop(box).save(O/(name+'-100pct.png'))
Image.fromarray(cv).resize((1024,1024)).save(O/'provisional-preview-1024.png')
Image.fromarray(replacements['p34'][102:358,500:1254]).save(O/'bottom-cut-100pct.png')
print(json.dumps(d))
