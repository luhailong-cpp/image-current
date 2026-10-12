from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).resolve().parent
b=p.parents[2]
s=b/'r04_c11/candidate/r04_c11-4096-candidate-v2.png'
box=[512,2957,1766,4211]
im=Image.new('RGB',(1254,1254))
im.paste(Image.open(s).crop((512,2957,1766,4096)),(0,0))
paths=[b/'r04_c11/native/p41-v1.png',b/'r04_c11/native/p42-v1.png']
im.paste(Image.open(paths[0]).crop((627,1139,1139,1254)),(0,1139))
im.paste(Image.open(paths[1]).crop((115,1139,857,1254)),(512,1139))
im.save(p/'target-native.png')
sources=[{'file':str(t),'sha256':hashlib.sha256(t.read_bytes()).hexdigest()} for t in [s,*paths]]
(p/'target-derivation.json').write_text(json.dumps({'sources':sources,'tileBox':box,'globalBox':[41472,15245,42726,16499],'operation':'unscaled native candidate crop plus unscaled original bottom halos; original halo context below assigned tile is retained only as reference','dimensions':[1254,1254],'haloPlacements':[{'source':str(paths[0]),'crop':[627,1139,1139,1254],'paste':[0,1139]},{'source':str(paths[1]),'crop':[115,1139,857,1254],'paste':[512,1139]}]},indent=2),encoding='utf-8')
print('target ready')
