import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
tile,active,assembly,note=sys.argv[1:]
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest'); P=B/tile/'pipeline'
state=P/'lane-state-20261012.json'
d=json.loads(state.read_text(encoding='utf-8-sig')) if state.exists() else {'tile':tile,'owner':'/root/sol_r12_repair_20261012','plannedNativeSlots':16}
d.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),status='native_production_active',activePatch=active,
    selectedNativeSlots=len(list((B/tile/'native').glob('p*.png.generation.json'))),
    successfulBuiltinCalls=len(list((P/'receipts').glob('*.receipt.json'))),actualModel=None,actualQuality=None,internalAccepted=False,formalAccepted=False,nextStep=note)
if assembly!='none': d['latestAssembly']={'file':assembly,'sha256':hashlib.sha256(Path(assembly).read_bytes()).hexdigest()}
state.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d))
