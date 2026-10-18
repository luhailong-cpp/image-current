from pathlib import Path
import json
Z=Path(__file__).resolve().parents[1]
old='cross_r06_c03c04_rail_ground_join_a01';new='cross_r06_c03c04_rail_ground_join_a02'
data=json.loads((Z/'guides'/f'{old}.input.json').read_text(encoding='utf-8-sig'))
data['stem']=new
data['retryNote']='Second local native edit uses the exact same immutable validated target and references as a01; latest disjoint paving-left operation does not affect this crop. No generation claimed for reuse.'
for name,obj in [(f'{new}.input.json',data),(f'{new}.references.json',dict(inputs=data['inputs']))]:
 p=Z/'guides'/name
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(prompt=(Z/'prompts'/f'{new}.prompt.txt').read_text(encoding='utf-8'),refs=[x['path'] for x in data['inputs']])))

