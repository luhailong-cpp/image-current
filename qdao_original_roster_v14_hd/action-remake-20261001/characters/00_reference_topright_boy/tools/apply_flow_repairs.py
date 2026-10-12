"""Adopt the five root- and independently-reviewed motion transitions."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review/full-body-20261004'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
 t=p.with_name(p.name+'.write-tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
jobs=[
 ('W',3,'flow-03-v1','run-south-repairs.json','右远侧空臂经躯干与葫芦自然遮挡，形成后摆到前摆的经过位；左持物手与双腿保持。'),
 ('W',11,'flow-11-v1','run-south-repairs.json','右远侧空臂经躯干与葫芦自然遮挡，形成前摆到后摆的经过位；左持物手与双腿保持。'),
 ('NE',4,'flow-04-v1','run-north-repairs.json','右空臂上臂收至身侧，低拳与前臂形成可见肘弯，连接后摆到前摆；腿与持物侧保留。'),
 ('NE',12,'flow-12-v3','run-north-repairs.json','右空臂以低拳、开放肘弯连接前屈到后摆，避免一次展开；腿与持物侧保留。'),
 ('SW',6,'flow-06-v2','run-south-repairs.json','左悬空腿由后折收至近身经过位，连接下一帧前摆；右支撑脚和左右手保留。')]
changes=[]
for direction,number,stem,proof_name,observation in jobs:
 source=f'generation/run/{direction}/{stem}.png';p=ROOT/source
 proof=OUT/proof_name
 expected=sha(p)
 proof_data=read(proof)
 approvals=proof_data.get('candidates',proof_data.get('repairs',[]))
 assert any(x.get('sourceSha256',x.get('sourceSHA'))==expected and x.get('adoptable') is True for x in approvals),(source,'missing independent approval')
 with Image.open(p) as im:
  assert im.size==(1254,1254) and im.mode=='RGBA'
  pixels=hashlib.sha256(im.tobytes()).hexdigest()
 selection=ROOT/f'generation/run/{direction}/selection-middle4-side2-20261004.json'
 doc=read(selection);rows=doc if isinstance(doc,list) else doc['frames']
 row=next(x for x in rows if int(x['frame'])==number);before=dict(row)
 assert not row['source'].endswith(stem+'.png'),'already adopted'
 row.update(source=source,sourceSha256=expected,generationRecord=source+'.generation.json',status='static_reviewed_dynamic_pending',observation=observation,latestRevisionEvidence=proof.relative_to(ROOT).as_posix())
 if 'nativePixelSha256' in row:row['nativePixelSha256']=pixels
 if 'generationRecordSha256' in row:row['generationRecordSha256']=sha(ROOT/(source+'.generation.json'))
 save(selection,doc)
 independent=ROOT/('review/grounding-fourframes/S-SE-SW-independent-static-review.json' if direction=='SW' else f'review/grounding-fourframes/{direction}-independent.json')
 report=read(independent);old_report_sha=sha(independent);group=report['directions'][direction] if 'directions' in report else report
 evidence=next(x for x in group['frames'] if int(x['frame'])==number);previous=dict(evidence)
 evidence.update(source=source,sourceSha256=expected,observation=observation,staticObservation=observation,nativePixelSha256=pixels,generationRecordSha256=sha(ROOT/(source+'.generation.json')),revisionEvidence=proof.relative_to(ROOT).as_posix(),revisionReviewer='/root/full_body_run_south' if direction in ('W','SW') else '/root/full_body_run_north')
 group.setdefault('priorRevisions',[]).append(dict(reportSha256=old_report_sha,selection=group['selection'],replacedFrame=previous,reason='localized arm/airborne-leg transition follow-up'))
 group['selection']={'path':selection.relative_to(ROOT).as_posix(),'sha256':sha(selection)}
 group['latestRevision']=dict(atUtc=datetime.now(timezone.utc).isoformat(),review=proof.relative_to(ROOT).as_posix(),reviewSha256=sha(proof),frame=number,sourceSha256=expected,dynamicVerified=False)
 save(independent,report)
 changes.append(dict(direction=direction,frame=number,before=before,after=dict(row),independentReport=independent.relative_to(ROOT).as_posix(),repairReview=proof.relative_to(ROOT).as_posix()))
save(OUT/'adopted-repairs.json',dict(atUtc=datetime.now(timezone.utc).isoformat(),changes=changes,normalFrameMs=75,cycleMs=1200,dynamicVerified=False,clientIntegrated=False))
print(json.dumps({'adopted':len(changes),'frames':[f'{d}{n:02d}' for d,n,*_ in jobs]}))
