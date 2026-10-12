from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'audit/full-limb-revision-before.json'
assert not p.exists(),'Preserve immutable start snapshot'
rows=[{'file':q.relative_to(ROOT).as_posix(),'sha256':sha(q)} for q in sorted((ROOT/'runtime').rglob('*.png'))]
assert len(rows)==196
p.write_text(json.dumps({'startedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Full current 196-frame limbs and hand/weapon inspection; correct only demonstrated pose defects','request':'全部已有方向跑步、受击、普攻、施法，手脚一起实际核查；正确帧保留；75ms×16=1200ms不变，两帧一位置过渡。','priorDelivery':'audit/current-revision-delivery.json','priorDeliverySha256':sha(ROOT/'audit/current-revision-delivery.json'),'beforeFrames':rows,'dynamicVisualAcceptance':False},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'audit/live-work-state.json').write_text(json.dumps({'state':'continuing_full_limb_and_weapon_review','writeBoundary':'This character only','sourceRequest':'audit/full-limb-revision-before.json','assignments':{'finish_e_ne':'run N NE E NW 64','finish_south':'run S SE SW W 64','finish_sw_nw':'combat E 34','root':'combat W 34 plus independent repair assessment and final delivery'},'dynamicVisualAcceptance':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('196-frame before-state saved; targeted full-limb audit started.')
