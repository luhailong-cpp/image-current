from pathlib import Path
import json,hashlib,shutil,sys
from datetime import datetime,timezone
from PIL import Image
D=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p): return {'path':str(Path(p)),'sha256':sha(p)}
job,original=sys.argv[1:3]
d=D/job; src=Path(original); digest=sha(src)
dest=d/('actual-native-'+digest[:16]+'.png')
if dest.exists(): assert sha(dest)==digest
else: shutil.copyfile(src,dest)
im=Image.open(dest)
p=json.loads((d/'preparation.json').read_text(encoding='utf-8-sig'))
for key in ['sourceCandidate','sourceContext','sourceManifest','immutableWestCore','alpha','fullAlpha','savedMask','request','prompt']:
 assert sha(p[key]['path'])==p[key]['sha256'],key
for v in p['references']: assert sha(v['path'])==v['sha256']
receipt={'schemaVersion':1,'job':job,'tool':'image_gen.imagegen','route':'builtin','status':'actual_builtin_output_saved','actualModel':None,'actualQuality':None,'savedAtUtc':datetime.now(timezone.utc).isoformat(),'timeMeaning':'local save time; actual generation timestamp not returned','original':info(src),'savedNative':info(dest),'dimensions':list(im.size),'request':info(d/'request.json'),'preparation':info(d/'preparation.json'),'references':p['references'],'byteCopyExact':sha(src)==sha(dest),'generatedByThisAgent':True,'RGBColorCorrection':False,'resampling':False,'formalAccepted':False}
out=d/('receipt-'+digest[:16]+'.json')
assert not out.exists(),'receipt already exists; inspect instead of overwrite'
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
assert im.size==(1254,1254),str(im.size)
print(json.dumps({'saved':info(dest),'receipt':info(out),'dimensions':list(im.size)}))

