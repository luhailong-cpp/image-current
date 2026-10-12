import json
from pathlib import Path
from PIL import Image
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl');m=json.loads((r/'manifest.json').read_text(encoding='utf-8'))
j=json.loads((r/'preview/derivations.json').read_text(encoding='utf-8'));errors=[]
for a in j['artifacts']:
 if not a['path'].endswith('.png'):continue
 im=Image.open(r/a['path']);values=[]
 for i in range(im.n_frames):im.seek(i);values.append(im.info['duration'])
 if len(values)!=len(a['durationsMs']) or any(abs(x-y)>0.01 for x,y in zip(values,a['durationsMs'])):errors.append(a['path'])
images=[p for p in r.rglob('*') if p.suffix.lower() in ('.png','.jpg','.jpeg','.gif','.webp')]
print(json.dumps({'gamePNG':len(list((r/'frames').rglob('*.png'))),'totalRetainedImages':len(images),'expected196plus42':238,'apngTimingErrors':errors,'clientIntegration':m['clientIntegration']}))
assert len(images)==238 and not errors

