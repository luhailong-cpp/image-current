from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'review/run_SE_contactpairs_20261004.json';report=json.loads(p.read_text(encoding='utf-8'))
resolved=report['resolvedIndependentFindings'][0]
p=R/'review/independent_NE_SW_SE_20261004.json';r=json.loads(p.read_text(encoding='utf-8'))
for f in r['findings']:
 if f['id']=='SE07-08-scale-watch':
  f['resolution']=resolved['resolution'];f['resolvedBy']=resolved['resolvedBy'];f['status']='resolved-static-review'
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'tools/review_se_contactpairs_20261004.py';s=p.read_text(encoding='utf-8');s=s.replace('本轮修正11帧：04、05、06、08、09、10、11、12、13、14、15。保留00、01、02、03、07五帧。','本轮修正12帧：04、05、06、07、08、09、10、11、12、13、14、15。保留00、01、02、03四帧。06/07末轮局部收头消除相邻头肩体量跳变，保留初接脚位。');p.write_text(s,encoding='utf-8')
p=R/'review/run_SE_contactpairs_20261004.md';s=p.read_text(encoding='utf-8');s=s.replace('本轮修正11帧：04、05、06、08、09、10、11、12、13、14、15。保留00、01、02、03、07五帧。','本轮修正12帧：04、05、06、07、08、09、10、11、12、13、14、15。保留00、01、02、03四帧。06/07末轮局部收头消除相邻头肩体量跳变，保留初接脚位。');p.write_text(s,encoding='utf-8')
print(json.dumps({'technicalIssues':report['technicalIssues'],'resolvedBy':resolved['resolvedBy']},ensure_ascii=False))
