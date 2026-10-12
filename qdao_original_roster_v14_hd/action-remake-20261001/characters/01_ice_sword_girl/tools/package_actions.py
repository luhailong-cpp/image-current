"""Package the actual selected PNGs and review metadata. Refuse missing/failed technical inventory."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,argparse,copy
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
assert m['presentFrameCount']==196 and m['technicalPassCount']==196 and not m['errors'], 'Incomplete technical inventory'
proof=json.loads((R/'review/delivery-provenance.json').read_text(encoding='utf-8'))
assert proof['passed'] and proof['checked']==196,'Final provenance audit incomplete'
playback=json.loads((R/'preview/verification-all.json').read_text(encoding='utf-8'))
assert len(playback['checks'])==14 and not playback['pageErrors'],'Final playback check incomplete'
p=argparse.ArgumentParser();p.add_argument('--require-art',action='store_true');args=p.parse_args()
run=[s for s in m['sequences'] if s['action']=='run']
if args.require_art:
 assert all(s.get('eightConsecutiveSupportVerified') and s.get('positionPairsVerified') for s in run),'Run art review incomplete'
d={'characterId':m['characterId'],'createdAt':datetime.now(timezone.utc).isoformat(),'totalFrames':196,'size':[1024,1024],'format':'PNG RGBA','runTiming':'16 x 60ms = 960ms','clientIntegrated':False,'clientRuntimeVerified':False,'review':{'runDirections':[{k:s.get(k) for k in ['direction','eightConsecutiveSupportVerified','positionPairsVerified','dynamicArtAccepted','remainingIssues']} for s in run]},'sequences':[]}
target=R/'ice_sword_girl_actions_196.zip'
preview_manifest=copy.deepcopy(m)
for s in preview_manifest['sequences']:
 for f in s['frames']:
  f['path']=f"runtime/{s['action']}/{s['direction']}/{f['frame']:02}.png"
  f['generationRecord']=f['path']+'.generation.json'
with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
 for s in m['sequences']:
  q={k:v for k,v in s.items() if k!='frames'};q['frames']=[]
  for f in s['frames']:
   path=R/f['path'];sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==f['sha256']
   rel=f"runtime/{s['action']}/{s['direction']}/{f['frame']:02}.png"
   z.write(path,rel)
   record=json.loads((R/f['generationRecord']).read_text(encoding='utf-8-sig'))
   record.update(file=rel,provenanceImageIncluded=False,provenanceNote='原生和参考图仅保留来源文字与哈希，不在交付包重复收录；本PNG为完整画布1024导出。')
   z.writestr(rel+'.generation.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
   q['frames'].append({'frame':f['frame'],'path':rel,'sha256':sha,'durationMs':f['durationMs']})
  d['sequences'].append(q)
  if s.get('selection'):z.write(R/s['selection'],s['selection'])
 for fn in ['animation-timing.json','MERGE_HANDOFF.md','review/paired-position-contact-requirement.json','review/combat-final-continuity-review.md','preview/verification-all.json','review/final-artwork-review.json','review/delivery-provenance.json','review/NW-final-independent-review.json','review/south-final-independent-review.json','review/south-completion-handoff.json','review/combat-final-independent-review.json','review/retired-image-sources.json']:
  if (R/fn).exists():z.write(R/fn,fn)
 for folder in ['sources','drafts']:
  for evidence in (R/folder).rglob('*'):
   if evidence.is_file() and evidence.suffix.lower() in ['.json','.txt']:
    z.write(evidence,evidence.relative_to(R).as_posix())
 for pattern in ['review/axis-*.json','review/*before-axis-20261004.json','review/video-axis-20261004/*.json','review/full-axis-*.json','review/full-action-audit-*.json','review/*before-full-axis-20261005.json']:
  for evidence in R.glob(pattern):z.write(evidence,evidence.relative_to(R).as_posix())
 for fn in ['preview/all.html','preview/all-player.js']:
  z.write(R/fn,fn)
 z.writestr('preview/all-sequences.js','window.ALL_SEQUENCES='+json.dumps(preview_manifest,ensure_ascii=False)+';\n')
 z.writestr('manifest.json',json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 z.writestr('README.txt','冰剑少女：8方向跑步128帧，E/W受击12、普攻24、施法32，共196张1024透明PNG。跑步统一60ms/帧，0.96秒/圈。\n文件在runtime/。解压后打开preview/all.html可预览所有动作。\n素材检查与客户端接入分开，本包未修改或验证客户端。\n')
with ZipFile(target) as z:
 bad=z.testzip();assert bad is None,bad
 assert len([n for n in z.namelist() if n.endswith('.png')])==196
sha=hashlib.sha256(target.read_bytes()).hexdigest()
(R/'delivery.json').write_text(json.dumps({'file':target.name,'sha256':sha,'bytes':target.stat().st_size,'totalFrames':196,'clientIntegrated':False,'review':d['review']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':str(target),'sha256':sha,'bytes':target.stat().st_size,'frames':196},ensure_ascii=False))
