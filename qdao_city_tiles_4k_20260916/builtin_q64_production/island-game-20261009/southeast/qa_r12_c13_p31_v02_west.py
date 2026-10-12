from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
Q=R/'qa/r12_c13-resume-sol-20261012'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
n=R/'tiles/r12_c12.candidate-sol-20261012-v01.png'
t=R/'native/r12_c13_p31_v02.png'
o=Q/'r12_c13_p31_v02-west-adopted-core-seam.png'
im=Image.new('RGB',(512,1024))
im.paste(Image.open(n).convert('RGB').crop((3840,2048,4096,3072)),(0,0))
im.paste(Image.open(t).convert('RGB').crop((115,115,371,1139)),(256,0));im.save(o)
d={'operation':'exact candidate native-derived west pixels and target 1024 core crop hard paste','resampled':False,'output':str(o),'sha256':sha(o),'sources':[{'file':str(n),'sha256':sha(n),'crop':[3840,2048,4096,3072],'destination':[0,0]},{'file':str(t),'sha256':sha(t),'crop':[115,115,371,1139],'destination':[256,0]}],'status':'pending_visual'}
Path(str(o)+'.trace.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d))

