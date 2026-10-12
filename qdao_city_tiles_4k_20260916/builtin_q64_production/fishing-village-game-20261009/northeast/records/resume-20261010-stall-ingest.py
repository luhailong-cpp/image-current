from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil,datetime
B=Path(__file__).resolve().parent.parent
name,src=sys.argv[1:3];src=Path(src);dst=B/'native'/f'resume-20261010-stall-{name}.png';shutil.copy2(src,dst)
im=Image.open(dst);assert im.size==(1254,1254)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((B/f'records/resume-20261010-stall-{name}.submission.json').read_text(encoding='utf-8'))
req.update({'file':str(dst),'sha256':sha(dst),'nativeSize':list(im.size),'copiedFrom':str(src),'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receiptFile':str(B/f'records/resume-20261010-stall-{name}.receipt.json'),'metadata':im.info,'isAIGenerated':True,'usable':False,'formalAccepted':False,'status':'pending_native_edge_visual_review'})
Path(str(dst)+'.generation.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'path':str(dst),'sha256':sha(dst),'nativeSize':list(im.size)}))
