import json,hashlib
from pathlib import Path
from PIL import Image
R=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
O=R/'parallel-review-20261013/island-game-20261009/resume-v02/residences'
j=json.loads((O/'snapshot.json').read_text(encoding='utf-8'))
inventory=json.loads((R/'parallel-review-20261013/island-game-20261009/root-audit-v01/inventory.json').read_text(encoding='utf-8-sig'))
t=next(t for t in inventory['tiles'] if t['tileId']=='r03_c13')
new=next(n for b in j['batches'] for n in b['native'] if n['id']=='r02_c12_p04_04_v03')
inputs=[(new['file']['path'],[883,883,1139,1139],[0,0],new['file']['sha256']),
(j['neighborSources']['r02_c13']['path'],[0,3840,256,4096],[256,0],j['neighborSources']['r02_c13']['sha256']),
(j['neighborSources']['r03_c12']['path'],[3840,0,4096,256],[0,256],j['neighborSources']['r03_c12']['sha256']),
(t['file'],[0,0,256,256],[256,256],t['sha256'])]
out=Image.new('RGB',(512,512));evidence=[]
for p,box,paste,expected in inputs:
    actual=hashlib.sha256(Path(p).read_bytes()).hexdigest()
    with Image.open(p) as im:out.paste(im.convert('RGB').crop(box),paste)
    evidence.append({'file':p,'sourceSha256':actual,'expectedSha256':expected,'hashMatches':actual==expected,'sourceCrop':box,'destination':paste})
path=O/'r02-r03-c12-c13-fourway-100pct.png';out.save(path)
data={'file':path.as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sources':evidence,'worldBox':[48896,7936,49408,8448],'intersection':[49152,8192],'operation':'exact unscaled 256px quadrant hard join; unselected candidate diagnosis at snapshot','visualReviewed':False}
(O/'corner.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2))
