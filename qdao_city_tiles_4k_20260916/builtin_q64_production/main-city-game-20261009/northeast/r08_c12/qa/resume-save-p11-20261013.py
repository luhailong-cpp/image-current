from pathlib import Path
import json
from datetime import datetime, timezone
t=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12')
s=json.loads((t/'selected-native.json').read_text(encoding='utf-8-sig'));s['p11']='p11-v20261013-resume.png';(t/'selected-native.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
p=json.loads((t/'tile-progress.json').read_text(encoding='utf-8-sig'));p.update(status='native_complete_local_QA_pending_P2',selectedCoreCount=16,nativePatchCount=16,remainingCoreCount=0,missingSelectedIds=[],nextPatch=None,inflightGeneration=None,successfulUnsavedOutputCount=0,lastSavedNative='p11-v20261013-resume.png',updatedAt=datetime.now(timezone.utc).isoformat(),note='Generation resumed under current AGENTS model clarification; 16 native cores saved. Four prior P2 findings still unpassed.');p.pop('pauseAuthority',None);p.pop('requestedExactImageModel',None);(t/'tile-progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
