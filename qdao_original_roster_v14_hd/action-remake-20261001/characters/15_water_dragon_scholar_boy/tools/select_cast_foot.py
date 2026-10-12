from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
p=b/'audit/cast-selection.json';d=json.loads(p.read_text(encoding='utf-8'));ap=b/'audit/cast-foot-review.json';a=json.loads(ap.read_text(encoding='utf-8'))
for key in sys.argv[1:]:
 parts=key.split('-');di=parts[1];num=int(parts[2]);src=f'sources/new/{key}.png';rec=f'provenance/generation/{key}.json'
 assert (b/src).exists() and (b/rec).exists()
 f=next(f for f in d['frames'] if f['direction']==di and f['frame']==num)
 if f['source']!=src:
  f.setdefault('supersedes',[]).append({'source':f['source'],'sha256':f['sha256'],'generationRecord':f['generationRecord'],'reason':'后靴脚尖与身体朝向叉开，针对后靴/踝方向修正'})
  f['source']=src;f['sha256']=hashlib.sha256((b/src).read_bytes()).hexdigest();f['generationRecord']=rec
  f['review']['notes'].append('2026-10-03后靴专项修正已实际目检：后靴鞋尖与前靴同向，原手势、角色比例、前靴保留。方向通过静态复核，动态待完整试播。')
  f['review']['reviewedAt']=datetime.now(timezone.utc).isoformat()
 af=next(f for f in a['frames'] if f['direction']==di and f['frame']==num);af['rearBoot']='corrected_static_checked';af['source']=src;af['sha256']=f['sha256']
a['updatedAt']=datetime.now(timezone.utc).isoformat();a['correctedCount']=sum(f['rearBoot']=='corrected_static_checked' for f in a['frames'])
a['status']='all32_corrected_static_checked_dynamic_pending' if a['correctedCount']==32 else 'rear_boot_toe_orientation_repair_in_progress'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');ap.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print('cast foot selected',a['correctedCount'])

