from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
from PIL import Image
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-852c0670-126b-480b-afb1-714ea3dd2aaf.png')
expected='29377f332db4bded672974c0e446e09b5c7b595e2271d5f941fdce257e2855cf';assert sha(src)==expected
D=B/'r09_c06/refinement/versions/resume-20261012-v01';D.mkdir(parents=True,exist_ok=True);dest=D/'p01_03.rejected-native.png';assert not dest.exists();shutil.copy2(src,dest);assert sha(dest)==expected
with Image.open(dest) as im:size=im.size;mode=im.mode;fmt=im.format;opaque=im.mode=='RGB' or im.getextrema()[-1]==(255,255)
rq=B/'r09_c06/pipeline/prompts/p01_03.resume-20261012-v01.request.json';receipt=B/'r09_c06/pipeline/receipts/p01_03.resume-20261012-v01.tool-result.json'
now=datetime.now(timezone.utc).isoformat();rec={'file':str(dest),'sha256':expected,'width':size[0],'height':size[1],'mode':mode,'format':fmt,'opaque':opaque,'request':str(rq),'requestSha256':sha(rq),'receipt':str(receipt),'receiptSha256':sha(receipt),'sourceOutputPath':str(src),'nativePixelsPreserved':True,'resizedAfterGeneration':False,'selected':False,'explicitlyRejected':True,'formalAccepted':False,'savedAtUtc':now}
atomic_json(D/'preservation.json',rec)
rp=B/'production-resume-20261012.json';r=read(rp);r.update(updatedAtUtc=now,status='first_native_return_saved_geometry_repair_required',firstNewOutput=rec,latestSavedOutput=rec,rootNextCoordinate='r09_c06:p01_03 targeted repair; do not redo original request',currentPermissionErrors=[{'worker':w,'error':'Fatal error: application network permission was revoked','observedAtUtc':now} for w in ['resume_r11c06','resume_r10c06','resume_crossedge_audit']]);atomic_json(rp,r)
p=read(B/'progress.json');p.update(updatedAtUtc=now,status='native_return_saved_repair_pending',rootImageGenerationInFlight=False,imageGenerationInFlight=False,latestResumedOutput=str(dest),latestResumedOutputSha256=expected,activeCoordinate='r09_c06:p01_03_repair',currentWorkerNetworkPermissionErrors=r['currentPermissionErrors'],nextStep='Check current root builtin availability once for targeted saved-native geometry repair; no paid API fallback or permission bypass.');atomic_json(B/'progress.json',p)
print(json.dumps(rec,ensure_ascii=False))

