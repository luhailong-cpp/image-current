from pathlib import Path
import argparse,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tile',required=True);p.add_argument('--selected',nargs='+',required=True);p.add_argument('--inflight',nargs='*',default=[]);a=p.parse_args()
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
s=Z/'west-current-selection-20261012.json';d=json.loads(s.read_text(encoding='utf-8-sig'));partial=next(x for x in d['partialTiles'] if x['tileId']==a.tile)
records=[]
for stem in a.selected:
 assert stem.startswith(a.tile+'_s')
 im=Z/'native'/(stem+'.png');rec=im.with_suffix('.png.generation.json');g=json.loads(rec.read_text(encoding='utf-8-sig'))
 assert info(im)['sha256']==g['sha256']
 records.append({'stem':stem,'image':info(im),'generationRecord':info(rec)})
assert len({x[9:14] for x in a.selected})==len(a.selected)
partial.update({'selectedNativeStems':a.selected,'selectedNative':records,'nativeCount':len(a.selected),'inflightStems':a.inflight,'status':str(len(a.selected))+'of16_native_internal_QA_pending','updatedAtUtc':datetime.now(timezone.utc).isoformat()})
s.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
print(json.dumps({'selection':info(s),'nativeCount':len(a.selected),'inflightCount':len(a.inflight)}))

