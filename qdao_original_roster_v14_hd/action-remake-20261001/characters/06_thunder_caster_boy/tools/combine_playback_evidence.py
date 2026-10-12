from pathlib import Path
import argparse,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('reports',nargs='+');a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={};sources=[]
for name in a.reports:
 q=(R/name).resolve();assert q.is_relative_to(R)
 report=json.loads(q.read_text(encoding='utf-8-sig'));assert report.get('completed') and not report.get('errors')
 sources.append({'file':q.relative_to(R).as_posix(),'sha256':sha(q)})
 for row in report['runs']:
  row['sourceReport']=q.relative_to(R).as_posix();rows[row['id']]=row
manifest=json.loads((R/'preview/manifest.json').read_text(encoding='utf-8'))
errors=[]
for seq in manifest['sequences']:
 row=rows.get(seq['id']);count=seq['expected_count']
 if not row:errors.append(seq['id']+' missing');continue
 if any(sha(R/f['path'])!=f['sha256'] for f in row['sourceBefore']):errors.append(seq['id']+' changed sources')
 if any(run['seen']!=list(range(count)) or run['nonRenderable'] or run.get('skippedTransitions') for run in row['runs']):errors.append(seq['id']+' playback issue')
 if len(row['runs'])!=2 or not row['sourceUnchanged'] or not row['manifestMatches']:errors.append(seq['id']+' metadata')
 if [x['frame'] for x in row['stepped']]!=list(range(count)) or any(not x['visible'] for x in row['stepped']):errors.append(seq['id']+' step issue')
 if not row['pauseAtLastFrame'] or row['nextWrap']!=0 or row['previousWrap']!=count-1:errors.append(seq['id']+' pause/wrap issue')
assert len(rows)==14 and not errors,errors
out={'verifiedAt':datetime.now(timezone.utc).isoformat(),'completed':True,'errors':errors,'clientConnected':False,'visualArtAcceptance':False,'method':'Consolidated actual browser recordings. Later same-sequence verification replaces earlier snapshot only after all current PNG hashes match.','sourceReports':sources,'manifestSha256':sha(R/'preview/manifest.json'),'runs':[rows[s['id']] for s in manifest['sequences']]}
(R/'review/current_playback_evidence_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sequences':len(rows),'sourceFrames':sum(len(x['sourceBefore']) for x in rows.values()),'passed':True}))
