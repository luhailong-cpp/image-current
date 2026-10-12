from pathlib import Path
import json
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl')
p=root/'audit/video-axis-root-repair-review.json'
d=json.loads(p.read_text(encoding='utf-8'))
b={r['file']:r['sha256'] for r in json.loads((root/'audit/video-axis-revision-before.json').read_text(encoding='utf-8'))['beforeFrames']}
for row in d['frames']:
 old=b['runtime/'+row['slot']+'.png']
 if 'beforeSha256' in row:assert row['beforeSha256']==old
 row['beforeSha256']=old
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
