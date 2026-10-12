from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
reasons={
 'run-E-03-20261005-full-limb-01.json':'实际看图只有四张火符，未满足右手五符；未采用。',
 'run-E-04-20261005-full-limb-01.json':'持铃臂仍在后伸端，没有形成所需的身侧中间过渡；未采用。',
 'run-E-11-20261005-full-limb-01.json':'实际看图出现六张火符及重复阴阳腰饰；未采用。',
 'run-E-11-20261005-full-limb-02.json':'铜铃过早到下巴前方的前摆位，未形成从后摆端经过身侧的中间姿态；未采用。',
}
for name,reason in reasons.items():
 p=R/'records'/name;d=json.loads(p.read_text(encoding='utf-8'));assert d.get('selectionStatus')=='generated_not_current';d['selectionReason']=reason;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print({'rejectedRecordReasonsUpdated':len(reasons),'imagesDeleted':0})
