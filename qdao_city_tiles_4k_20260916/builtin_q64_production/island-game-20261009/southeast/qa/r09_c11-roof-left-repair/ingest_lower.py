from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pid='r09_c11_roof_color_lower_v01';src=Path(sys.argv[1]);out=R/'native'/f'{pid}.png';assert not out.exists();shutil.copy2(src,out);assert Image.open(out).size==(1254,1254)
q=rd(R/'prompts'/f'{pid}.request.json')
record={'file':str(out),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshotTargetOnly':rd(R/'progress.json').get('configSnapshot'),'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'prompt':q['promptPath'],'promptSha256':sha(Path(q['promptPath'])),'references':q['references'],'nativeGlobalBox':q['nativeGlobalBox'],'originRelativeR09c11':q['originRelativeR09c11'],'upperNative':q['upperNative'],'upperNativeSha256':q['upperNativeSha256'],'evidence':{'toolReceipt':str(R/'receipts'/f'{pid}.json')},'resizedAfterGeneration':False,'status':'native_received_pending_assembly_QA'}
for ref in q['references']:assert sha(Path(ref['file']))==ref['sha256']
wr(Path(str(out)+'.generation.json'),record)
print(json.dumps({'file':str(out),'sha256':sha(out),'size':[1254,1254]},indent=2))

