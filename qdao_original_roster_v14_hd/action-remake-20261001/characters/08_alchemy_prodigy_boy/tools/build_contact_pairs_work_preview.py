"""Temporary review page: combine selected native candidates and retained runtime."""
from pathlib import Path
import hashlib, json, re
ROOT = Path(__file__).resolve().parents[1]
selection = {}
for name in ['east', 'south-east', 'north', 'south', 'west']:
    p=ROOT/'provenance/contact-pairs-20261004'/(name+'-selection.json')
    if not p.exists(): continue
    selection.update(json.loads(p.read_text(encoding='utf-8-sig')))
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
groups = []
for d in ['N','NE','E','SE','S','SW','W','NW']:
    urls = []
    for i in range(1,17):
        slot = f'run/{d}/{i:02}'
        p = ROOT / selection.get(slot, {}).get('source', 'runtime/'+slot+'.png')
        urls.append('../'+p.relative_to(ROOT).as_posix()+'?v='+hashlib.sha256(p.read_bytes()).hexdigest()[:12])
    groups.append({'key':'run/'+d, 'ms':75, 'frames':urls})
data = 'window.PREVIEW_DATA='+json.dumps(groups,ensure_ascii=False)+';'
(ROOT/'preview/contact-pairs-work-data.js').write_text(data,encoding='utf-8')
html = (ROOT/'preview/index.html').read_text(encoding='utf-8')
html = re.sub(r'src="data\.js[^\"]*"', 'src="contact-pairs-work-data.js?v='+hashlib.sha256(data.encode()).hexdigest()[:12]+'"', html)
html = html.replace('08 炼丹童子 · 动作复核','08 炼丹童子 · 候选序列复核')
html = html.replace('<a id="contact" target="_blank">打开逐帧联系表</a>', '<a id="contact" target="_blank" hidden>联系表</a>')
(ROOT/'preview/contact-pairs-work.html').write_text(html,encoding='utf-8')
print(json.dumps({'selected':len(selection),'candidateGroups':len(groups)}))
