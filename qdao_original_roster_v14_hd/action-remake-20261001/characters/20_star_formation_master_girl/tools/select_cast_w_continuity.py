from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'cast-W-selection.json').read_text(encoding='utf-8-sig'))
old={int(f['frame']):f for f in d['frames']}
mapping={5:6,6:5,11:13,12:12,13:14,14:11}
out=[]
for i in range(1,17):
 s=mapping.get(i,i); f=dict(old[s]); f['frame']=i
 f['previousSlot']=s
 f['continuityNote']='按实际星盘高度整理聚势与收势顺序；没有新增、复制或编辑像素，保留原逐图来源。' if s!=i else '保留现有动作槽位'
 out.append(f)
d['frames']=out
d['continuityReview']={'method':'原生导出16格逐帧对照盘手高度，消除原05→06下降再抬升和10→11过早收盘；收势排序为原13/12/14/11/15/16','dynamicAccepted':False,'reordered':mapping}
(R/'cast-W-continuity-selection.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('W cast continuity selection written, 16 unique original sources')

