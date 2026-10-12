from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((ROOT/'audit/full-limb-revision-before.json').read_text(encoding='utf-8'))['beforeFrames']
rows=[]
for r in before:
 parts=r['file'].split('/')
 if parts[1] in ['hit','attack','cast'] and parts[2]=='W':
  assert sha(ROOT/r['file'])==r['sha256']
  rows.append({'file':r['file'],'beforeSha256':r['sha256'],'actuallyViewedOriginal':True})
assert len(rows)==34
out={'reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'All 34 current W combat originals plus existing hit/attack/cast contacts, actual view_image inspection','method':'Trace visible shoulder-elbow-wrist-hand/weapon and hip-knee-ankle-boot; compare neighboring phases. Do not interpret rigid clothes edges or fixed screen pants coordinates as hidden joint identity.','frames':rows,'confirmedIssues':[],'repairSlots':[],'findings':{'hit/W':'01–03软膝后仰受击、04回重心、05–06收回站姿；左手持续握弓，右空手胸前保护到放下，手腕自然接袖口，未见手数/弓手交换。鞋头均在后跟左前方，没有单靴反向横撇。','attack/W':'01–03右手取箭，04搭箭到05–06拉弦，07–08松弦开手，09–12收手；可见持弓手包住握把，右手和箭尾/拉开的弦汇点连接。张腿和软膝随拉弓承重变化，两靴保持朝左前，没有孤立脚掌外扭。','cast/W':'01–02空手起势，03–04取箭，05–09搭箭/逐步满弓，10–11松弦开手，12–16回收；当前空手五指表现和袖口接腕连续，未见反肘或多手。双靴前掌朝左前、后跟在右后，宽站姿用于支撑拉弓，不按跑步窄轨迹强制改成并腿。'},'limits':['Sleeves conceal exact elbow contours; no invented exact joint angle','No browser real-time or client grounding/playback acceptance','This records no demonstrated defect in reviewed W combat frames, not blanket sequence visual approval'],'sourceReferenceUse':'User video/screenshot were actually inspected in preceding video-axis pass; motion only, approved character style retained','dynamicVisualAcceptance':False,'imageEdits':False}
(ROOT/'audit/full-limb-combat-W-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('W combat full-limb review saved:34 inspected,0 confirmed targeted defects.')
