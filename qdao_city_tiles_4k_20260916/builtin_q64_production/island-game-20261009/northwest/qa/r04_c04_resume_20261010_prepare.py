from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
Z=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
Q=Z/'qa'/'r04_c04_resume_20261010'
Q.mkdir(exist_ok=True)
C=json.loads((Z.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
src=Path(C['layoutReference'])
im=Image.open(src)
box=[245,245,383,383]
o=Q/'layout_CONTEXT_ONLY_NOT_GAME.png'
im.crop(box).resize((828,828),Image.Resampling.NEAREST).save(o)
rec={'scope':'r04_c04 16 native slots + internal seam QA','status':'waiting_top_anchor_for_first_patch','resumeAtUtc':datetime.now(timezone.utc).isoformat(),'existingNativeAtResume':list(p.name for p in (Z/'native').glob('r04_c04*.png')),'leftAnchor':'r04_c03_s01_04_a02','topAnchorRequestedFrom':'right_tile_resume r03_c04_s04_01','preparationOnly':'r04_c04_s01_01_a01 guide prepared with left source; no generation attempted','reviewContext':{'path':o.as_posix(),'layoutSource':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'cropBox':box,'resizingForQADisplayOnly':True,'forbiddenInFinalArt':True},'builtinOnly':True,'noProgressMutation':True,'noRuntimeValidation':True}
(Q/'resume.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(o)

