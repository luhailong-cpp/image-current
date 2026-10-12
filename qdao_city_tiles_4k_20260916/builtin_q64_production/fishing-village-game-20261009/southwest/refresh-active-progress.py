import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest")
sp=importlib.util.spec_from_file_location('coverage_selector',z/'qa/full-tile-assemble.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
coverage={f'r{r:02d}_c{c:02d}':len(m.select(f'r{r:02d}_c{c:02d}')) for r in range(8,15) for c in range(1,8)}
p=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'))
p.update(status='active_art_and_seam_production',updatedAtUtc=datetime.now(timezone.utc).isoformat(),generatedNativeCount=len(list((z/'native').glob('*.png.generation.json'))),currentSelectedNativeSlotCount=sum(coverage.values()),missingNativeCoreSlotCount=784-sum(coverage.values()),fullyCovered4kCount=sum(v==16 for v in coverage.values()),internalPassed4kCount=3,internalPassedTiles=['r09_c04','r09_c05','r10_c05'],currentCoverageByTile={k:v for k,v in coverage.items() if v},nextStep='Complete staircase repair and 2x2 join; finish fish-market local repairs and continued r09_c07 native queue.',artOnly=True,runtimeGateActive=False)
p['internalQaPending']=['r10_c04 whole staircase repair','r09_c06 long-post material transitions and joint QA','r09_c07 remaining native patches']
p['sharedArtEdgesPassed']=['r09_c04/r09_c05','r09_c05/r10_c05']
(z/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:p[k] for k in ['generatedNativeCount','currentSelectedNativeSlotCount','missingNativeCoreSlotCount','fullyCovered4kCount','internalPassed4kCount','currentCoverageByTile']}))

