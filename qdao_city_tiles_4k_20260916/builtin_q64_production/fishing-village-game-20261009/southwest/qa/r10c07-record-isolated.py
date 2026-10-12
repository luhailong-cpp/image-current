import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
z=Path(__file__).resolve().parent.parent
stem=sys.argv[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
image=z/f'native/{stem}.png';receiptpath=z/f'native/{stem}.receipt.json';requestpath=z/f'native/{stem}.request.json'
receipt=json.loads(receiptpath.read_text(encoding='utf-8-sig'));request=json.loads(requestpath.read_text(encoding='utf-8-sig'))
with Image.open(image) as im:size=list(im.size);fmt=im.format;keys=list(im.info)
refs=[{**r,'sha256':sha(r['path'])} for r in request['references']]
out=Path(str(image)+'.generation.json');assert not out.exists(),out
record={'file':image.as_posix(),'sha256':sha(image),'generatedAt':receipt['finishedAtUtc'],'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':None,'configSnapshotUnavailableReason':'Shared optional config file absent when resumed native record was saved; no model selector was submitted.','submittedParameters':request['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host does not expose or report actual model/quality. No claim of selected model is made.','evidence':{'receipt':receiptpath.as_posix(),'receiptSha256':sha(receiptpath),'receiptFields':['result.output_hint'],'pngMetadataKeys':keys},'prompt':(z/f'native/{stem}.prompt.txt').as_posix(),'promptSha256':sha(z/f'native/{stem}.prompt.txt'),'request':{'path':requestpath.as_posix(),'sha256':sha(requestpath)},'references':refs,'coordinates':request['coordinates'],'status':'candidate_pending_seam_qa','nativePixelsResampled':False}
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':image.as_posix(),'dimensions':size,'sha256':record['sha256'],'record':out.as_posix()}))
