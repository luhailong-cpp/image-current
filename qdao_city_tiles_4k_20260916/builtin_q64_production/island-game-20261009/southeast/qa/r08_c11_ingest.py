from pathlib import Path
from PIL import Image
import json,hashlib,os,sys,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid,ver,source=sys.argv[1:4];receipt=R/'receipts'/f'{pid}_{ver}.json';requestfile=R/'prompts'/f'{pid}_{ver}.request.json';req=rd(requestfile);out=R/'native'/f'{pid}_{ver}.png';assert not out.exists() and receipt.exists()
shutil.copy2(source,out);im=Image.open(out);im.load();assert im.size==(1254,1254)
for ref in req['references']:assert sh(ref['file'])==ref['sha256']
assert sh(req['promptPath'])==req['promptSha256']
prog=rd(R/'progress-r08_c11.json');rec={'file':str(out),'sha256':sh(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':source,'sourceOutputSha256':sh(source),'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'request':str(requestfile),'requestSha256':sh(requestfile),'references':req['references'],'receipt':str(receipt),'receiptSha256':sh(receipt),'configSnapshotTargetOnly':prog['configSnapshotTargetOnly'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool does not disclose actual model/quality; target configuration is not actual evidence.','coordinate':req['coordinate'],'resizedAfterGeneration':False,'status':'candidate_pending_visual_and_seam_review'}
wr(Path(str(out)+'.generation.json'),rec);prog.update({'status':'native_saved_pending_QA','currentPatch':pid,'generatedNativeCount':len(list((R/'native').glob('r08_c11_*.png'))),'inFlight':False,'lastNative':str(out),'lastNativeSha256':sh(out),'updatedAt':rec['generatedAt']});wr(R/'progress-r08_c11.json',prog)
print(json.dumps({'file':str(out),'sha256':sh(out),'size':list(im.size)}))
