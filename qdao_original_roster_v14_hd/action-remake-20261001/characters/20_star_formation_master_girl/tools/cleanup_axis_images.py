"""Remove this revision's intermediate media after verified final runtime exists."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert rd(R/'provenance/final-verification.json')['passed']
assert rd(R/'STATUS.json')['axisReviewed']
out=R/'provenance/axis-image-cleanup.json';assert not out.exists()
for f in rd(R/'selection.json')['frames']:assert sha(R/f['source'])==f['sourceSha256']
scope=(R/'axis-review-20261004').resolve();assert scope.is_relative_to(R)
files=[p.resolve() for p in scope.rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.mp4'}]
assert all(p.is_relative_to(scope) for p in files)
rows=[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'最终runtime与预览完整，删除本轮过程图片/临时视频副本，保留来源文字'} for p in files]
data={'time':datetime.now(timezone.utc).isoformat(),'scope':scope.as_posix(),'removed':rows,'count':len(rows),'bytes':sum(x['bytes'] for x in rows),'finalRuntimeVerified':196,'textEvidenceRetained':True}
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in files:p.unlink()
(scope/'reference.html').write_text('<!doctype html><meta charset="utf-8"><p>视频对照已完成，临时视频副本已清理。<a href="../preview/run-E-grounding.html">打开星阵少女八向成品</a></p>',encoding='utf-8')
for name in ['MERGE_HANDOFF.md','STATUS.md']:
 with (R/name).open('a',encoding='utf-8') as f:f.write('\n本轮过程图片及临时视频副本已清理；逐图来源、实际提示词、回执与SHA保留。清理索引：provenance/axis-image-cleanup.json。当前图片以runtime与preview为准。\n')
vr=rd(R/'provenance/final-verification.json');vr['axisImageCleanup']='provenance/axis-image-cleanup.json';(R/'provenance/final-verification.json').write_text(json.dumps(vr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'removed':len(rows),'bytes':data['bytes'],'finalRuntime':196}))
