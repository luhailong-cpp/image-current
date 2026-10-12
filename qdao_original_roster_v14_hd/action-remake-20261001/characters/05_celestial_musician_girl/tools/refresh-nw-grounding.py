from pathlib import Path
import json
r=Path(__file__).resolve().parent.parent
p=r/'provenance/run/grounding-NW-20261003.json'
d=json.loads(p.read_text(encoding='utf-8'))
s=json.loads((r/'provenance/run/selection-SE-NW.json').read_text(encoding='utf-8'))
for f in [8,9]:
    row=next(x for x in d['frames'] if x['frame']==f)
    row['priorVersionReview']={k:row[k] for k in ['file','generationRecord','observedPhase','footKneeAnkleCOM','phaseNote']}
    row.update(next(x for x in s if x['direction']=='NW' and x['frame']==f))
    row['observedPhase']='descent_candidate' if f==8 else 'contact_candidate'
    row['footKneeAnkleCOM']='前方较小鞋转成侧面薄底边并下降，后方大鞋折高露底；两腿可按前后层次追踪。' if f==8 else '前方较小鞋底近水平，膝略屈承重，后方大鞋高折，前景裤腿遮远侧支撑腿。'
    row['phaseNote']='v2鞋底朝向改善，跟08/09邻帧连续性和跨半圈异侧归属仍待动态。'
d['unresolved']=['08v2与09v2改善鞋底侧面下降到近水平承重；异侧归属仍须沿髋膝动态追踪，不能按提示词认定。','04与12经过轮廓相似，近远腿归属须完整动态追踪；NW不视为通过。','01/02压低差异小，需连播判断是否足够承重感。','比例、根锚配准、循环总时长、逐帧时长及客户端滑步未验收。']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
