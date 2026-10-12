from pathlib import Path
from datetime import datetime,timezone
import json,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
p=B/'progress.json';d=json.loads(p.read_text(encoding='utf-8'));a=json.loads((B/'r09_c05/pipeline/output/270f210e60b79873/assembly.json').read_text(encoding='utf-8'))
d.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),activeTile='r09_c06',activeCoordinate='r09_c06:p01_01',primaryNewTile='r09_c06',primaryNewTileNativeCount=0,activeTiles=['r09_c06','r12_c05','r09_c01','r09_c07'],nextStep='Root produces r09_c06 adjacent arena coverage; r09_c05 full candidate remains pending macro and seam corrections. Dedicated r12_c05 repair lane and other production lanes continue.',lastNewCompleteCandidate={'tile':'r09_c05','assembly':str(B/'r09_c05/pipeline/output/270f210e60b79873/assembly.json'),'candidate':a['output']['file'],'candidateSha256':a['output']['sha256'],'contextSha256':a['contextOutput']['sha256'],'nativeSlots':16,'internalAccepted':False,'formalAccepted':False},rootImageGenerationInFlight=True,imageGenerationInFlight=True)
atomic_json(p,d); print('progress updated; actual counts preserved')

