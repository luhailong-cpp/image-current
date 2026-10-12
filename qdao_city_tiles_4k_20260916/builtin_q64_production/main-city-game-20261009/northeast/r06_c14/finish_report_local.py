from pathlib import Path
import json
T=Path(__file__).resolve().parent
progress=json.loads("{\"tile\":\"r06_c14\",\"status\":\"complete_4k_candidate_internal_north_and_west_seams_reviewed\",\"nativeCount\":22,\"selectedCoreCount\":16,\"selectedRepairCount\":4,\"unselectedRepairCount\":2,\"remainingCoreCount\":0,\"fullyCovered4kCount\":1,\"completeCandidateCount\":1,\"internalReviewed4kCount\":1,\"internalPassed4kCount\":1,\"externalAllSidesPassed4kCount\":0,\"formalAcceptedCount\":0,\"candidate\":\"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r06_c14/candidates/r06_c14.candidate.png\",\"candidateSha256\":\"609ed58611561a612eec2f87ec95b21ca0c7a3712a2ef07585368f4287b99a66\",\"review\":\"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r06_c14/qa/internal-seam-review.json\",\"evidenceAudit\":\"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r06_c14/qa/evidence-check.json\",\"sourceReplay\":\"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r06_c14/qa/final-review/source-replay.json\",\"inflightGeneration\":null,\"nextPatch\":null,\"nextStep\":\"Root closes existing 2x2 with this stable candidate. No further coordinate claimed.\",\"actualModel\":null,\"actualQuality\":null}")
(T/'tile-progress.json').write_text(json.dumps(progress,indent=2)+'\n',encoding='utf8')
p=T/'native'/'m03.png.generation.json';d=json.loads(p.read_text(encoding='utf8'));d['status']='unselected-superseded-by-m02-and-m04';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
for name in ['m02','m04','m05','m06']:
 p=T/'native'/(name+'.png.generation.json');d=json.loads(p.read_text(encoding='utf8'));d['status']='integrated-and-native-seams-reviewed';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
print('Tile progress and repair status saved; no art pixels changed.')

