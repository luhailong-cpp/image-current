import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,shutil,datetime
from PIL import Image
Z=Path(__file__).resolve().parents[1];stem=Z/'native'/sys.argv[1];src=Path(sys.argv[2]);dst=stem.with_suffix('.png')
assert not dst.exists();assert src.is_file();assert Image.open(src).size==(1254,1254);shutil.copyfile(src,dst)
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
request=rd(stem.with_suffix('.request.json'));old=rd(Z/'native/r09_c06_repair_d_frontpost_paving_v1.png.generation.json')
refs=[]
for index,path in enumerate(request['submittedParameters']['referenced_image_paths']):
 p=Path(path);refs.append({'path':p.as_posix(),'sha256':sha(p),'dimensions':list(Image.open(p).size),'role':['native edit target or exact continuity guide','approved full map layout','material close-up','approved user style'][index]})
rec={'file':dst.as_posix(),'sha256':sha(dst),'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','configSnapshot':old['configSnapshot'],'submittedParameters':request['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':old['unverifiedReason'],'evidence':{'receipt':stem.with_suffix('.receipt.json').as_posix(),'receiptFields':['result.output_hint'],'pngMetadataKeys':list(Image.open(dst).info)},'prompt':request['prompt'],'references':refs,'coordinates':request['coordinates'],'status':'candidate_pending_complete_object_seam_qa','nativePixelsResampled':False}
Path(str(dst)+'.generation.json').write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'file':dst.as_posix(),'sha256':sha(dst)}))
