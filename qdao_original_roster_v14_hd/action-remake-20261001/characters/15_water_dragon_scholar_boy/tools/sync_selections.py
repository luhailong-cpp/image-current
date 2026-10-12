from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'sources-index.json';index=json.loads(p.read_text(encoding='utf-8'))
frames=[r for r in index['frames'] if r['action']=='run']
for candidate in sorted((ROOT/'audit').glob('run-*-selection.json')):
    data=json.loads(candidate.read_text(encoding='utf-8-sig'))
    incoming=data['frames']
    slots={(r['action'],r['direction'],r['frame']) for r in incoming}
    frames=[r for r in frames if (r['action'],r['direction'],r['frame']) not in slots]
    frames.extend(incoming)
for action in ('hit','attack','cast'):
    candidate=ROOT/'audit'/f'{action}-selection.json'
    if candidate.exists():
        data=json.loads(candidate.read_text(encoding='utf-8-sig'))
        frames.extend(data['frames'])
index['frames']=frames
p.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print({action:sum(r['action']==action and r.get('accepted') is True for r in frames) for action in ('run','hit','attack','cast')})
