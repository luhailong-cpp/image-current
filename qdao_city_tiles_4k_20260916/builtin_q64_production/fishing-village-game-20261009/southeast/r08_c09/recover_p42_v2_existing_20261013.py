from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from PIL import Image
T=Path(__file__).resolve().parent
source=Path('C:/Users/luyua/.codex/generated_images/01a13018-0b2a-7290-b74e-dfd31ccbac73/exec-dea6782b-2b1c-478a-9fd7-ff65df47ba35.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
assert Image.open(source).size==(1254,1254)
raw=T/'raw/p42-v2-builtin-recovered.png';assert not raw.exists();shutil.copy2(source,raw)
receipt=dict(receivedAt=datetime.now(timezone.utc).isoformat(),sourcePath=str(raw),builtinSourcePath=str(source),tool='image_gen__imagegen',route='builtin',actualModel=None,actualQuality=None,nativeDimensions=[1254,1254],sha256=sha(raw),toolResponse=None,responseStatus='Tool result unavailable: exec cell148 not found after interruption; no stored result',recoveryEvidence=dict(outputDirectory='same builtin session generated_images/01a13018-0b2a-7290-b74e-dfd31ccbac73',recoveredFilename=source.name,discoveredFileMtime=source.stat().st_mtime,visualMatch='One partial red/cream lantern at left and bluegray stone pavement only, matching p42-v2 prompt',association='Strong temporal and visual association; actual returned tool receipt unavailable',modelVerified=False),notClaimed='No returned model metadata or successful tool response reconstructed')
write(T/'p42-v2.receipt.json',receipt)
write(T/'p42-v2.recovery.json',receipt)
sel=json.loads((T/'selected-patches.json').read_text(encoding='utf-8-sig'));sel['patches']['p42']='native/p42-v2.png';sel.update(status='local_recovered_candidate_pending_join_QA',internalReady=False,formalAccepted=False)
write(T/'selected-patches-recovered-candidate-20261013-v1.json',sel)
print(json.dumps(dict(sourcePath=str(raw),sha256=sha(raw),modelVerified=False,responseRecovered=False)))
