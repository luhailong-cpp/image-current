"""Remove superseded image files only after final selected exports are independently verified."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,argparse
R=Path(__file__).resolve().parents[1].resolve()
assert R.name=='01_ice_sword_girl' and R.parent.name=='characters'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
m=rd(R/'manifest.json');proof=rd(R/'review/delivery-provenance.json');delivery=rd(R/'delivery.json')
assert m['presentFrameCount']==196 and m['technicalPassCount']==196 and not m['errors']
assert proof['passed'] and proof['checked']==196
assert all(s.get('eightConsecutiveSupportVerified') and s.get('positionPairsVerified') for s in m['sequences'] if s['action']=='run')
assert sha(R/delivery['file'])==delivery['sha256']
keep={f['path'] for s in m['sequences'] for f in s['frames']}
for s in m['sequences']:
 for f in s['frames']:assert sha(R/f['path'])==f['sha256']
 keep.add(f"preview/{s['action']}-{s['direction']}-1x-{s['cycleMs']}ms.webp")
 if s['action']=='run':keep.add(f"preview/run-{s['direction']}-selected-256.png")
 else:keep.add(f"review/combat-{s['action']}-{s['direction']}-contact-sheet.png")
for rel in keep:assert (R/rel).is_file(),f'Missing retained image: {rel}'
remove=[]
for source in R.rglob('*'):
 if source.is_file() and source.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.gif']:
  resolved=source.resolve()
  assert resolved.is_relative_to(R),f'outside scope {source}'
  rel=source.relative_to(R).as_posix()
  if rel not in keep:remove.append({'file':rel,'sha256':sha(source),'bytes':source.stat().st_size})
record_path=R/'review/retired-image-sources.json'
old=rd(record_path) if record_path.exists() else {}
combined={v['file']:v for v in old.get('removedFiles',[])}
for item in remove:combined[item['file']]=item
record={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'applied' if args.apply else 'dry_run','scope':str(R),'policy':'保留最终游戏PNG、最终预览/接地联系图与全部逐图文字证据；删除原生加工图、拒稿、中间预览，无图片回退备份。','archive':delivery['file'],'preCleanupArchiveSha256':delivery['sha256'],'preCleanupProvenance':'review/delivery-provenance.json','previousRetirementProof':'review/retired-image-sources-before-full-axis-20261005.json','removedFiles':list(combined.values()),'removedThisPass':remove,'removedBytes':sum(v['bytes'] for v in remove),'keptImagePaths':sorted(keep)}
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if args.apply:
 for item in remove:
  target=(R/item['file']).resolve()
  assert target.is_relative_to(R) and sha(target)==item['sha256']
  target.unlink()
print(json.dumps({'status':record['status'],'removedImages':len(remove),'removedBytes':record['removedBytes'],'retainedImages':len(keep)},ensure_ascii=False))
