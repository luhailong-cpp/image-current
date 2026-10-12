"""Apply the user's uniform 75 ms run timing without changing any PNG or combat timing."""
from timing_profile import RUN_FRAME_MS
if RUN_FRAME_MS != 75:
    raise SystemExit('历史75ms迁移工具已停用；当前以timing_profile.py为准。')
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat(); ledger=ROOT/'provenance/audit/run_timing_1200_update_20261003.json'
timing=read(ROOT/'runtime_timing.json'); delivery=read(ROOT/'manifest.delivery.json'); review=read(ROOT/'review.json')
records=[];before=[]
for row in delivery['files']:
    assert sha(ROOT/row['path'])==row['sha256']
    j=ROOT/row['record']; assert sha(j)==row['recordSha256'];data=read(j)
    if data['action']=='run':
        before.append({'file':row['path'],'sha256':row['sha256'],'frameDurationMs':data.get('frameDurationMs'),'runTiming':data.get('runTiming'),'sidecarSha256':row['recordSha256']})
        records.append((j,data))
assert len(records)==128
if not ledger.exists():save(ledger,{'requestedAt':now,'reason':'用户最新明确1200ms一圈、16帧均匀75ms，移除旧快档；替代先前800对照和比例权重方案。','beforeRunTiming':timing['run'],'beforeFrames':before,'pngPixelsChanged':False,'combatTimingChanged':False})
for j,data in records:
    data['frameDurationMs']=75
    data['runTiming']={'offlinePreviewDefaultLoopMs':1200,'offlinePreviewFrameMs':75,'offlinePreviewFrameDurationsMs':[75]*16,'clientApprovedLoopMs':None,'status':'user_selected_offline_1200_client_unconfirmed','updatedAt':now,'updateRecord':'provenance/audit/run_timing_1200_update_20261003.json'}
    save(j,data)
timing['run']={k:v for k,v in timing['run'].items() if k in ['directions','framesPerDirection','phaseMarkers']}
timing['run'].update(frameMs=75,offlineDefaultLoopMs=1200,offlineFrameDurationsMs=[75]*16,clientApprovedLoopMs=None,status='user_selected_offline_1200_client_unconfirmed',previewEncoding='APNG',previewFrameDurationsMs=[75]*16,timingRationale='用户指定16帧均匀75ms；完整1200ms循环，首尾不额外停顿，当前预览移除旧快档。')
timing['timingUpdatedAt']=now;save(ROOT/'runtime_timing.json',timing)
review['limits']=[('1200ms/75ms为用户选定的离线节奏；客户端速度未接入验证。' if '720ms' in item else item) for item in review['limits']]
review['timingUpdate']={'record':'provenance/audit/run_timing_1200_update_20261003.json','cycleMs':1200,'frameMs':75,'uniform':True,'clientTested':False}
save(ROOT/'review.json',review)
for row in delivery['files']:row['recordSha256']=sha(ROOT/row['record'])
delivery['timingUpdatedAt']=now;save(ROOT/'manifest.delivery.json',delivery)
print(json.dumps({'runFramesUpdated':len(records),'frameMs':75,'cycleMs':1200,'pngChanged':0,'combatChanged':0}))
