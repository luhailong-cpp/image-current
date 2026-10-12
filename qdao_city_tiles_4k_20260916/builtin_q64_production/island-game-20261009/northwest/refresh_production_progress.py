from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
pp=Z/'progress.json'; p=json.loads(pp.read_text(encoding='utf-8-sig'))
natives=list((Z/'native').glob('*.png'));receipts=list((Z/'receipts').glob('*.receipt.json'))
p.update(status='native_4k_candidate_internal_repairs_in_progress',generatedNativeCount=len(natives),generationAttemptCount=len(receipts),usableNativeCount=16,complete4kCount=0,assembledCandidateTileCount=1,formalAcceptedCount=0,currentTile='r03_c03',currentPatch='r03_c03_whole_tile_native_repairs',latest4kCandidate='tiles/r03_c03_candidate-v3_4096.png',nextStep='Complete paving and upper red-beam material repairs, review their binary native boundaries, then close internal QA. Adjacent r03_c04 first patch under roof-layout correction.',updatedAtUtc=now,candidateCountMeaning='16 selected subcell positions cover one 4096 native candidate; composite and whole-object native repair chain preserve full pixel provenance. Neither internal tile completion nor external formal acceptance is claimed.')
pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((Z/'r03_c03.candidate-v1.manifest.json').read_text(encoding='utf-8-sig'))
selections=[]
for row,entries in enumerate(manifest['patchMatrix'],1):
 for col,e in enumerate(entries,1):
  selections.append(dict(patchId=f'r03_c03_s{row:02d}_{col:02d}',**e,status='base_candidate_source_with_required_tile_level_repairs',qaEvidence='qa/assembly_r03_c03_candidate-v1_4096'))
selected=dict(schemaVersion=2,status='complete_coverage_candidate_pending_internal_repairs_and_external_edge_QA',formalAccepted=False,selectionRule='Explicit reviewed source per coordinate plus explicit same-coordinate repair records; never choose greatest attempt automatically.',selections=selections,tileLevelRepairs=[dict(path=f'tiles/r03_c03_candidate-v{n}_4096.native-repair.json',sha256=sha(Z/f'tiles/r03_c03_candidate-v{n}_4096.native-repair.json')) for n in (2,3)],currentCandidate=dict(path='tiles/r03_c03_candidate-v3_4096.png',sha256=sha(Z/'tiles/r03_c03_candidate-v3_4096.png')),updatedAtUtc=now)
(Z/'selected-native.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(generatedNativeCount=len(natives),receiptCount=len(receipts),assembledCandidateTileCount=1,complete4kCount=0,formalAcceptedCount=0)))
