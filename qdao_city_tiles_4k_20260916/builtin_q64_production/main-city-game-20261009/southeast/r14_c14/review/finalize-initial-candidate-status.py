import json
from pathlib import Path
from datetime import datetime,timezone
p=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14/progress.json")
d=json.loads(p.read_text(encoding="utf-8"))
d.update(status="candidate_failed_internal_and_external_visual_review",updatedAt=datetime.now(timezone.utc).isoformat(),activeNativeCount=16,generatedNativeCount=18,missingNativeCoordinateCount=0,missingNativeCount=0,complete4kCandidateCount=1,inFlightImageGenCount=0,currentPatch=None,internalArtQA="failed_grout_continuity_requires_native_repair",externalNeighborSeamQA="not_passed_core_to_core_boundaries",formalAccepted=False,visualQA=r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14/review/assembly-8ff54f4e9ec7de483b1a/visual-qa.json",nextStep="Repair native grout geometry and external core transitions, reassemble new immutable candidate, and repeat internal/external QA; no formal acceptance")
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:d[k] for k in ('status','activeNativeCount','generatedNativeCount','internalArtQA','externalNeighborSeamQA','formalAccepted')}))

