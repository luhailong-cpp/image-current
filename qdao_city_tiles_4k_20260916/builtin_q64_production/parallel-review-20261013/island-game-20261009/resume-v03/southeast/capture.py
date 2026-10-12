from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
PROD=BASE/'island-game-20261009/southeast'
REVIEW=BASE/'parallel-review-20261013/island-game-20261009'
OUT=Path(__file__).parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
prior=read(REVIEW/'resume-v02/southeast/metadata-snapshot.json')
priormap={Path(x['file']).name:x for x in prior['checks']}
start=now(); docs={}; checks=[]
names=set()
for pat in ['progress*.json','selection*.json','selected-native*.json','*native-spec*.json','current-zone-counts*.json','production-state.json','returned-output-check-resume*.json','*quick-review*.json']:
    names.update(PROD.glob(pat))
for p in sorted(names):
    a=p.stat(); b=p.read_bytes(); z=p.stat(); h=hashlib.sha256(b).hexdigest()
    old=priormap.get(p.name)
    c={'file':str(p),'sha256':h,'bytes':len(b),'mtimeNs':a.st_mtime_ns,'stableDuringRead':a.st_mtime_ns==z.st_mtime_ns and a.st_size==z.st_size,'baselineSha256':old['sha256'] if old else None,'changedSinceV02':h!=old['sha256'] if old else True}
    checks.append(c); docs[p.name]=json.loads(b.decode('utf-8-sig'))
write('metadata-snapshot.json',{'startedAtUtc':start,'capturedAtUtc':now(),'documents':docs,'checks':checks,'instructions':{str(p):sha(p) for p in [ROOT/'AGENTS.md',ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json']}})
print(json.dumps({'metadataFiles':len(checks),'changed':[Path(x['file']).name for x in checks if x['changedSinceV02']],'adopted':docs['progress.json'].get('currentAdoptedCandidates'),'zoneCounts':docs.get('current-zone-counts-20261013.json'),'active':{n:docs[n] for n in ['selection-r13_c11.json','progress-r13_c11.json','progress-r13_c13.json','selection-r14_c11.json','progress-r14_c11.json','progress-r14_c12.json','progress-r14_c14.json','r14_c14-quick-review-20261013.json']}},ensure_ascii=False))
