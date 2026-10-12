import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;BASE=HERE.parent.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
left=BASE/'r12_c08/native/p14-v2.png'
sel=BASE/'r12_c09/selected-patches.json';selected=json.loads(sel.read_text(encoding='utf-8-sig'))
right=BASE/'r12_c09'/selected['patches']['p11']
images=[Image.open(p).convert('RGB') for p in (left,right)]
assert all(i.size==(1254,1254) for i in images)
box=[32150,44941,33404,46195];split=32768-32150
im=Image.new('RGB',(1254,1254));im.paste(images[0].crop((521,0,1139,1254)),(0,0));im.paste(images[1].crop((115,0,751,1254)),(split,0))
output=HERE/'r12c08-rail-input-100pct.png';im.save(output)
rec={'globalBox':box,'tileBoundaryGlobalX':32768,'tileBoundaryNativeX':split,'sourceDimensions':[1254,1254],'sources':[{'file':str(left),'sha256':sha(left),'status':'root unselected p14-v2 explicitly authorized as left target','crop':[521,0,1139,1254],'destination':[0,0]},{'file':str(right),'sha256':sha(right),'selection':str(sel),'selectionSha256':sha(sel),'crop':[115,0,751,1254],'destination':[split,0]}],'operation':'exact native assembly including source halos; no interpolation, scaling or color change','output':str(output),'outputSha256':sha(output),'selected':False,'formalAccepted':False}
(HERE/'r12c08-rail-input.qa.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec))
