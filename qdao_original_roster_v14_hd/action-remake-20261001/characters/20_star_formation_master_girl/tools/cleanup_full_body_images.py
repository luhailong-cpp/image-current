"""Delete reviewed intermediates only after current final files pass verification."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert rd(R/'provenance/final-verification.json')['passed']
assert rd(R/'STATUS.json')['fullBodyReviewed']
out=R/'provenance/full-body-image-cleanup.json';assert not out.exists()
for f in rd(R/'selection.json')['frames']:assert sha(R/f['source'])==f['sourceSha256']
scope=(R/'hand-review-20261005').resolve();assert scope.is_relative_to(R)
files=[p.resolve() for p in scope.rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.mp4'}]
for name in ['run-eight-directions-1200ms.png','run-eight-directions-1200ms-slow.png']:
 p=(R/'preview'/name).resolve()
 if p.exists():files.append(p)
assert all(p.is_relative_to(R) for p in files)
rows=[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'最终runtime与60ms预览已验证；删除过程稿、审核局部图与过时75ms总览，保留来源文字。'} for p in files]
data={'time':datetime.now(timezone.utc).isoformat(),'scope':scope.as_posix(),'removed':rows,'count':len(rows),'bytes':sum(x['bytes'] for x in rows),'finalRuntimeVerified':196,'textEvidenceRetained':True}
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in files:p.unlink()
for name in ['MERGE_HANDOFF.md','STATUS.md']:
 with (R/name).open('a',encoding='utf-8') as f:f.write('\n本轮过程图片及过时75ms总览已清理；逐图来源、提示词、回执与SHA保留。清理索引：provenance/full-body-image-cleanup.json。当前素材以runtime及60ms preview为准。\n')
vr=rd(R/'provenance/final-verification.json');vr['fullBodyImageCleanup']='provenance/full-body-image-cleanup.json';(R/'provenance/final-verification.json').write_text(json.dumps(vr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'removed':len(rows),'bytes':data['bytes'],'finalRuntime':196}))

