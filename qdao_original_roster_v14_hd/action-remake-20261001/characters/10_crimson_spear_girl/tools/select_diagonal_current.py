from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'source-selection.json'
s=json.loads(p.read_text(encoding='utf-8-sig'))
for slot,source in {
'run/NE/01':'generation/run-NE-01-v3/native.png',
'run/NE/05':'generation/run-NE-05-v4/native.png',
'run/NE/07':'generation/run-NE-07-v2/native.png',
'run/NE/08':'generation/run-NE-08-v2/native.png',
'run/SW/07':'generation/run-SW-07-v2/native.png',
'run/SW/08':'generation/run-SW-08-v2/native.png'
}.items():s['slots'][slot]=source
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'LATEST_REQUIREMENTS_20261003.md'
p.write_text(p.read_text(encoding='utf-8')+'\n## 最新追加（优先于上文历史时长）\n\n用户现在指定已认可的09竹弓少女为同方向姿态参考；实际只读查看并保留10自身造型、长枪与双手握持。全八方向继续逐帧对照，正确帧保留。\n\n跑步正常播放固定16×75ms=1200ms，移除当前预览中的480/640/720/800档，取消分相位权重。保留慢放、暂停、逐帧；不满16帧方向不得跳过缺槽播放短循环。战斗40/30/45ms保持。最新规定覆盖前文720试播及承重时长试验。客户端未改。\n',encoding='utf-8')

