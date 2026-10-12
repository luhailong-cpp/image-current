"""Record compact observations read from the visible CUA browser-check report."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((R/n).read_text(encoding='utf-8-sig'))
data=read('records/cua_playback_observed_20261005.json')
snapshot=read('records/browser_check_source_snapshot_20261004.json')
assert data['completed'] and data['passed'] and not data['errors']
assert data['manifestGeneratedAt']==snapshot['generatedAt']
assert data['sourceFrameCount']==196 and len(data['runs'])==14
assert all(r['passed'] and r['normalAllFrames'] and r['slowAllFrames'] and r['nonRenderable']==0 and r['skippedTransitions']==0 and r['steppedAllVisible'] and r['pauseAtLastFrame'] and r['nextWrap']==0 and r['previousWrap']==r['frameCount']-1 for r in data['runs'])
assert all(sha(R/f['path'])==f['sha256'] for f in snapshot['frames'])
assert all(min(r.get('actualWrapCounts',[0]))>=3 for r in data['runs'])
out={**data,'verifiedAt':datetime.now(timezone.utc).isoformat(),'sourceFrames':snapshot['frames'],'sourceManifestSha256':snapshot['manifestSha256'],'sourceUnchangedAfterPlayback':True,'sourceSnapshot':'records/browser_check_source_snapshot_20261004.json','observedResultRecord':'records/cua_playback_observed_20261004.json','method':'实际Codex内置浏览器打开本角色browser-check.html，点击检查；真实预览iframe正常/四分之一速度各至少两圈，rAF观测可见图片，暂停、逐帧及首尾；本记录来自CUA读取页面可见JSON结果','clientConnected':False,'visualArtAcceptance':False}
out['method']=data['method']+'; recorded through CUA visible DOM JSON; per-frame decode, pause, step and wrap checked.'
out['observedResultRecord']='records/cua_playback_observed_20261005.json'
(R/'review/current_playback_evidence_20261005.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sequences':14,'sourceFrames':196,'passed':True,'sourceUnchanged':True}))
