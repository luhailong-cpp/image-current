from pathlib import Path
from datetime import datetime, timezone
import json

B=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=B/'migration-freeze-20261011.json'
v=read(p)
workers={}
for tile in ['r02_c03','r02_c04','r05_c04']:
    wp=B/f'work-{tile}'/'migration-freeze-20261011.json'
    workers[tile]={'checkpoint':str(wp),'exists':wp.exists()}
    if wp.exists(): workers[tile]['contents']=read(wp)
v['workerFreezeCheckpoints']=workers
v['savedAtUtc']=datetime.now(timezone.utc).isoformat()
v['workerCheckpointsAllPresent']=all(x['exists'] for x in workers.values())
v['workerNotificationEvidence']={
  'notified':['/root/paving_resume','/root/e3_integration_resume','/root/north_joint_resume'],
  'olderWorkers':['/root/cloth_center_column','/root/cloth_wall_column','/root/coordinate_audit'],
  'olderWorkersStatus':'Not listed as live at freeze. Old worker messages not used to trigger further production. Root workspace freeze applies to all workers.',
  'instructions':'Stop all new generation/repair/expansion, only save existing successful outputs and in-flight returns, write freeze checkpoint, then end.'
}
write(p,v)
cp=B/'continuation-round-20261011.json'
c=read(cp)
c.update(status='migration-frozen',generationStopped=True,freezeCheckpoint=str(p),latestCompleteCandidate='work-r04_c02/repair-v3/r04_c02.candidate.png',latestCompleteCandidateAccepted=False)
c['firstNewOutput']['status']='saved-and-composed-into-repair-v3-pending-visual-QA'
c['remaining']=['latest paving mask edges and full-core scan','repair-v3 assembly base provenance correction','worker handoff review and future adjacent tiles after migration']
write(cp,c)
print(json.dumps({'checkpoint':str(p),'workerCheckpointsAllPresent':v['workerCheckpointsAllPresent'],'workers':{k:x['exists'] for k,x in workers.items()}},ensure_ascii=False))
