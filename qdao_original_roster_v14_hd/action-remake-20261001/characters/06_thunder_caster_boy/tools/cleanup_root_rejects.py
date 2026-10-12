"""Remove explicitly rejected root drafts after current replacements exist; keep source text."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
rejected={
 'run_S_00_v1':'run/S/00',
 'run_SE_00_v1':'run/SE/00',
 'run_S_02_v4':'run/S/02',
 'run_S_10_v2':'run/S/10',
 'run_S_09_v2':'run/S/09',
 'run_S_09_v3':'run/S/09',
 'run_S_07_v2':'run/S/07',
 'run_S_14_v3':'run/S/14',
 'run_S_15_v3':'run/S/15'
}
active_sources=set()
for sidecar in (ROOT/'runtime').rglob('*.png.generation.json'):
 record=json.loads(sidecar.read_text(encoding='utf-8-sig'))
 for source in record.get('derivedFrom',[]):
  if isinstance(source,dict) and source.get('file'):active_sources.add((ROOT/source['file']).resolve())
deleted=[]
for stem,slot in rejected.items():
 p=(ROOT/'work'/f'{stem}.png').resolve();successor=ROOT/'runtime'/f'{slot}.png';rec=p.with_name(p.name+'.generation.json')
 if not p.exists():continue
 if not p.is_relative_to(ROOT.resolve()):raise ValueError('Outside character')
 if p in active_sources:raise ValueError('Still production source: '+str(p))
 if not successor.exists() or not rec.exists():raise ValueError('Replacement/provenance missing')
 record=json.loads(rec.read_text(encoding='utf-8-sig'));row={'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'successor':successor.relative_to(ROOT).as_posix(),'reason':'Rejected/superseded draft; current candidate and its provenance exist; no active runtime reference','removedAt':datetime.now(timezone.utc).isoformat()}
 record['retention']={'imageRemoved':True,**row};rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');p.unlink();deleted.append(row)
(ROOT/'records'/'root_rejected_cleanup_20261003.json').write_text(json.dumps({'deleted':deleted,'scope':'root-owned explicit rejected drafts only; active agent/native references preserved'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'removed':len(deleted),'keptTextProvenance':True}))
