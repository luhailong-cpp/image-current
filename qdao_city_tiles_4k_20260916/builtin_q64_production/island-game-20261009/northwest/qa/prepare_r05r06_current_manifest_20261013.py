from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1]
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
base=Z/'tiles/connected-r05-r06-cross-v1'
record=base/'connected-cluster.json'
data=json.loads(record.read_text(encoding='utf8'))
tiles=[]
for item in data['outputs']:
 image=Path(item['output']['path']); projection=Path(item['projectionRecordPath'])
 assert info(image)['sha256']==item['output']['sha256']
 tiles.append(dict(tileId=item['tileId'],image=info(image),record=info(projection)))
out=Z/'qa/connected-r05-r06-current-v1.manifest.json'
with out.open('x',encoding='utf8') as f:json.dump(dict(schemaVersion=1,tiles=tiles),f,indent=2)
print(json.dumps(info(out)))
