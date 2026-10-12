from pathlib import Path
from PIL import Image
import json, hashlib, shutil, datetime
b=Path(__file__).resolve().parents[1]
r=b/'refinement'
h=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,d: Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
req=read(r/'p01_01.v03.request.json')
receipt=read(r/'p01_01.v03.receipt.json')
src=Path(receipt['sourceOutputPath'])
dst=r/'native'/'p01_01.png'
dst.parent.mkdir(exist_ok=True)
assert not dst.exists()
im=Image.open(src)
assert im.size==(1254,1254) and im.format=='PNG'
shutil.copy2(src,dst)
rec=read(b/'native'/'p01_01.png.generation.json')
rec.update(file=str(dst),sha256=h(dst),generatedAt=receipt['returnedAtUtc'],generatedAtEvidence='Observed built-in tool return time; host generation time undisclosed',mode=im.mode,sourceOutputPath=str(src),sourceOutputSha256=h(src),prompt=req['promptFile'],promptSha256=req['promptSha256'],request=str(r/'p01_01.v03.request.json'),requestSha256=h(r/'p01_01.v03.request.json'),references=req['references'],visualStatus='candidate_QA_foliage_corrected_macro_geometry_preserved',formalAccepted=False)
rec['evidence']={'toolReceipt':str(r/'p01_01.v03.receipt.json'),'toolReceiptSha256':h(r/'p01_01.v03.receipt.json'),'pngMetadata':im.info}
write(str(dst)+'.generation.json',rec)
write(r/'selection.json',{'p01_01':'refinement/native/p01_01.png.generation.json'})
write(r/'selection-qa.json',{'p01_01':{'v01':'superseded: upper-right foliage misread as metal connector','v02':'rejected: correct foliage but roof rim moved downward','v03':'selected candidate: foliage restored while roof geometry remains aligned','formalAccepted':False,'pending':['Cross-zone top neighbor r08_c01 unavailable','Full 4K and neighboring patch seam QA pending']}})
print(json.dumps({'native':str(dst),'sha256':h(dst),'size':im.size}))
