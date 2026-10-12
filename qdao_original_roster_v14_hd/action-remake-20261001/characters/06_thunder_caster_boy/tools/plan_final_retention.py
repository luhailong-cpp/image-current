"""Plan explicit file-only cleanup after all reviewed exports are verified. No deletion."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from current_review_state import current_review
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=current_review()
assert review and review.get('localWorkComplete'),'Final SHA-bound review required'
native=json.loads((R/'review/native_export_verification_20261004.json').read_text(encoding='utf-8-sig'))
assert native['passed'] and len(native['records'])==196
assert all(sha(R/f['file'])==f['sha256'] for f in native['records'])
current_native={f['nativeFile'] for f in native['records']}
keep={f'{a}_{d}_contact.png' for a,dirs in [('run',['N','NE','E','SE','S','SW','W','NW']),('hit',['E','W']),('attack',['E','W']),('cast',['E','W'])] for d in dirs}
keep.update(f'run_{d}_contactpairs_positions.png' for d in ['N','NE','E','SE','S','SW','W','NW'])
keep.update(f'run_{d}_contactpairs_{cycle}.webp' for d in ['N','NE','E','SE','S','SW','W','NW'] for cycle in [1200,4800])
files=[]
for p in (R/'work').glob('*.png'):
    rec=p.with_name(p.name+'.generation.json')
    if not rec.is_file():rec=p.with_suffix('.generation.json')
    if not rec.is_file():raise ValueError('Unrecorded source: '+str(p))
    rel=p.relative_to(R).as_posix()
    files.append({'file':rel,'sha256':sha(p),'bytes':p.stat().st_size,'textRecord':rec.relative_to(R).as_posix(),'reason':'已核验正式导出的原生重复图' if rel in current_native else '已淘汰的生成/加工过程图'})
for p in (R/'review').iterdir():
    if not p.is_file() or p.suffix.lower() not in {'.png','.jpg','.jpeg','.gif','.webp'} or p.name in keep:continue
    files.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'历史复核图，已由当前SHA联系表和动态预览替代'})
for f in files:
    p=(R/f['file']).resolve()
    assert p.is_relative_to(R.resolve()) and p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.webp'}
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'authorizedBy':'用户AGENTS素材保留规则：最终资源落盘并引用完整后删除原图/回退/拒稿/中间图，保留逐图来源文字','scope':str(R),'files':files,'totalBytes':sum(f['bytes'] for f in files),'executed':False,'excluded':'不访问或删除临时Edge配置、缓存或其子目录；这些此前被自动审批拒绝'}
(R/'records/final_retention_plan_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(files),'bytes':out['totalBytes'],'plan':'records/final_retention_plan_20261004.json'}))
