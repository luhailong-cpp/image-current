from pathlib import Path
import json,hashlib,shutil,sys
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parent;ident=sys.argv[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reqp=W/'receipts'/(ident+'.request.json');rp=W/'receipts'/(ident+'.receipt.json');q=read(reqp);r=read(rp);p=B/'native'/(ident+'.png')
assert not p.exists();shutil.copy2(r['originalFile'],p);im=Image.open(p);assert im.size==(1254,1254)
g=read(B/'native/r04_c02_s04_s01_v01.png.generation.json')
g.pop('globalCoreBox',None);g.pop('nativeCoreCropBox',None)
g.update({'file':str(p),'sha256':sha(p),'generatedAt':r['returnedAt'],'evidence':{'receipt':str(rp),'request':str(reqp),'fields':['output_hint']},'prompt':q['promptFile'],'references':[{'file':f,'sha256':sha(f),'role':role} for f,role in zip(q['referenced_image_paths'],q['referenceRoles'],strict=True)],'globalNativeBox':q['globalNativeBox'],'geometryNote':q['geometryNote'],'status':'whole-object-candidate-pending-mask-QA'})
Path(str(p)+'.generation.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(p),'sha256':g['sha256'],'nativeSize':list(im.size)}))
