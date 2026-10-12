from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(z/'clothpass-selected.json')
qa=z/'r10_c09/qa/clothpass-review.json'
assert Path(m['candidate']['file']).exists()
local={'tile':'r10_c09','patches':m['patches'],'status':'internal_ready_external_seams_pending','internalReady':True,'formalAccepted':False,'derivedSelection':{'file':str(z/'clothpass-selected.json'),'sha256':sha(z/'clothpass-selected.json')},'qa':{'file':str(qa),'sha256':sha(qa)},'candidate':m['candidate'],'updatedAt':datetime.now(timezone.utc).isoformat()}
write(z/'r10_c09/selected-patches.json',local)
dest=z/'ready-for-edge-QA/r10_c09.png';dest.parent.mkdir(exist_ok=True)
shutil.copy2(m['candidate']['file'],dest)
asset={'file':str(dest),'sha256':sha(dest),'dimensions':[4096,4096],'classification':'internally reviewed 4K native composite; external seams pending','internalReady':True,'formalAccepted':False,'sourceSelection':{'file':str(z/'r10_c09/selected-patches.json'),'sha256':sha(z/'r10_c09/selected-patches.json')},'sourceDerivation':{'file':str(z/'clothpass-selected.json'),'sha256':sha(z/'clothpass-selected.json')},'nativeCoveragePixels':4096*4096,'singleGeneration4k':False,'upsamplingApplied':False,'processing':'16 cropped1024 native cores; recorded bounded color correction and cloth-only AI texture repair; integer alignment, no pixel resampling','actualModel':None,'actualQuality':None,'actualMetadataExplanation':'See individual builtin generation receipts; host did not disclose selectors or returned model/quality','qa':local['qa'],'externalEdges':{'north':'not_generated','east':'candidate_adjacent_tile_in_progress','south':'candidate_adjacent_tile_in_progress','west':'candidate_adjacent_tile_in_progress'},'capacity5000Validated':False,'clientMappingValidated':False}
write(dest.with_suffix('.png.asset.json'),asset)
print(json.dumps({'file':str(dest),'sha256':asset['sha256'],'internalReady':True,'formalAccepted':False},indent=2))

