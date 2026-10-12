from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
p=R/'run-timing.json';j=json.loads(p.read_text(encoding='utf-8'))
j['status']='selected_offline_after_normal_and_quarter_speed_review'
j['updatedAt']=now
for d,group in j['directions'].items():
 group['status']='selected_offline'
 q=R/group['phaseReview'];phase=json.loads(q.read_text(encoding='utf-8'))
 phase.update({'status':'passed_offline_normal_and_quarter_speed','reviewedAt':now,'clientValidated':False})
 for i,row in enumerate(phase['frames']):
  row['sha256']=hashlib.sha256((R/'run'/d/f'{i+1:02d}.png').read_bytes()).hexdigest()
  row['durationMs']=group['durationsMs'][i]
 if d=='E':
  phase['frames'][6].update({'phase':'右腿下降、准备落地','observation':'近右膝开始伸展，远左腿折回；不记为承重。'})
  phase['frames'][10]['rightArm']='经过近侧髋旁的中间后摆，接10前摆与12后摆。'
 q.write_text(json.dumps(phase,ensure_ascii=False,indent=2),encoding='utf-8')
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
reviews=json.loads((R/'review.json').read_text(encoding='utf-8'))
assert len(reviews)==196
assert all(v['visualStatus']=='passed' and hashlib.sha256((R/(k+'.png')).read_bytes()).hexdigest()==v['sha256'] for k,v in reviews.items())
(R/'audit/final-visual-review.json').write_text(json.dumps({'reviewedAt':now,'count':196,'status':'passed_offline','scope':['full contact sheets','selected enlarged native and registered frames','independent per-direction anatomy and shoe-axis review','normal240px playback and enlarged quarter-speed playback','uniform 75ms x 16 = 1200ms run'],'ground':[512,942],'globalScale':0.8,'remainingKnownArtFixes':[],'clientValidated':False,'limitations':['Short robe/fox naturally occlude some joints; alternate support traced across sequences.','World movement speed, root, shadow and combat events require client integration.'],'records':'review.json'},ensure_ascii=False,indent=2),encoding='utf-8')
