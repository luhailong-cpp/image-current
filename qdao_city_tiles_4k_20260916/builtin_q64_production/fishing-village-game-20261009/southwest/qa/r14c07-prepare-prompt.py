import sys,json,hashlib
from pathlib import Path
Z=Path(__file__).resolve().parent.parent;R=Z.parents[3]
stem=sys.argv[1];req=json.loads((Z/'native'/(stem+'.request.json')).read_text(encoding='utf-8-sig'))
scene=sys.argv[2]
prompt='Use case: stylized-concept. Native game map patch '+stem+'. Output exactly 1254 x 1254 native pixels. Image 1 is the precise coordinate edit guide: preserve all existing sharp native overlap strips at their exact pixels and extend matching coherent hand-painted detail through the coarse/pixelated layout area. The coarse portion is layout-only, redraw as fine original detail. Image 2 is whole-map layout; image 3 is materials/style; image 4 is approved Daoist Q hand-painted style (do not copy UI, characters or night lighting). Image 5 is broader tile placement context only, do not zoom out or copy its entire composition. '+scene+' Match existing cyan turquoise water shade, hand-painted scale, ripples and daylight exactly. Avoid repeating the same wave pattern, no dense grain/noise, no photorealism, no pixels or blur. Do not invent shore, boats, buildings, animals or props. Preserve exact guide framing and positions, no horizon, no UI/text, no crop, no camera shift.'
p=Z/'native'/(stem+'.prompt.txt');assert not p.exists();p.write_text(prompt+'\n',encoding='utf-8')
rules=(R/'AGENTS.md').read_text(encoding='utf-8-sig');split=json.loads((R/'docs/MAP_PARALLEL_SPLIT_20261013.json').read_text(encoding='utf-8-sig'))
reserved=[x for b in split['batches'] if b['map']=='fishing-village-game-20261009' and b['status']=='allocated_root_reserved' for x in b['tiles']];assert req['tile'] not in reserved
print(json.dumps({'job':req,'prompt':prompt,'rulesReread':{'AGENTSsha256':hashlib.sha256(rules.encode()).hexdigest(),'splitUpdated':split['updatedAtUtc'],'reserved':reserved}},ensure_ascii=False))
