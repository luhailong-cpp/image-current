import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, shutil, hashlib, datetime
from PIL import Image
Z=Path(__file__).resolve().parents[1]
p=Z/'native/r09_c06_repair_d_floor_v2'
request=json.loads(p.with_suffix('.request.json').read_text(encoding='utf-8-sig'))
old=json.loads((Z/'native/r09_c06_repair_d_frontpost_paving_v1.png.generation.json').read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12553-952a-78d2-b4aa-26e2192fe9b9/exec-b4c213f5-ab3f-44a6-8497-5ff3d846fcbe.png')
dst=p.with_suffix('.png')
assert not dst.exists()
shutil.copyfile(src,dst)
im=Image.open(dst); assert im.size==(1254,1254)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt={'tool':'image_gen__imagegen','route':'builtin','savedAt':now,'sourceGeneratedImage':str(src),'projectFile':str(dst),'actualModel':None,'actualQuality':None,'result':{'output_hint':'Generated images are saved to '+str(src.parent)+' as '+str(src)+' by default. Copy saved unchanged; original retained.'}}
p.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
rec={'file':dst.as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'generatedAt':now,'width':1254,'height':1254,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','configSnapshot':old['configSnapshot'],'submittedParameters':request['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':old['unverifiedReason'],'evidence':{'receipt':p.with_suffix('.receipt.json').as_posix(),'receiptFields':['result.output_hint'],'pngMetadataKeys':list(im.info)},'prompt':request['prompt'],'references':request['references'],'coordinates':request['coordinates'],'status':'candidate_pending_seam_qa','nativePixelsResampled':False}
Path(str(dst)+'.generation.json').write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'file':str(dst),'sha256':rec['sha256'],'dimensions':im.size}))
