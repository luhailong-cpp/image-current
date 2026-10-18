from pathlib import Path
import json
T=Path(__file__).resolve().parent
p=T/'active-native-map.json';a=json.loads(p.read_text(encoding='utf-8'));v=a.pop('p02_01');p.write_text(json.dumps(a,indent=2)+'\n',encoding='utf-8')
(T/'review/p02_01-first-rejected.json').write_text(json.dumps({'version':v,'result':'rejected_before_dependency','retained':True,'findings':['Artificial x115 boundary; false y230 and y810 courses conflict with y145 and y963 native anchors.']},indent=2)+'\n',encoding='utf-8')
