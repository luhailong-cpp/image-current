from pathlib import Path
from PIL import Image
import json,hashlib
d=Path(__file__).parent
root=d.parents[2]
north=root/'r03_c10/candidate/r03_c10-4096-candidate-v2.png'
south=root/'r04_c10/candidate/r04_c10-4096-candidate-v1.png'
im=Image.new('RGB',(1254,1254))
im.paste(Image.open(north).crop((0,3469,1254,4096)),(0,0))
im.paste(Image.open(south).crop((0,0,1254,627)),(0,627))
out=d/'context-before-native.png';im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'file':str(out),'dimensions':[1254,1254],'globalPixelBox':[36864,11661,38118,12915],'sharedBoundaryLocalY':627,'noResampling':True,'sources':[{'file':str(north),'sha256':sha(north),'crop':[0,3469,1254,4096],'pasteAt':[0,0]},{'file':str(south),'sha256':sha(south),'crop':[0,0,1254,627],'pasteAt':[0,627]}],'sha256':sha(out)}
(d/'context-before-native.derivation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))

