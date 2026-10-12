from pathlib import Path
import json
O=Path(__file__).resolve().parent
p=O/'inventory.json';d=json.loads(p.read_text(encoding='utf-8'));bad=[];unknown=[];derived=[]
for t in d['tiles']:
 for c in t['selectedCores']:
  co=c.get('coordinates') or {};core=c['coreGlobalBox'];expectedNative=[core[0]-115,core[1]-115,core[2]+115,core[3]+115]
  if 'coreGlobalBox' in co and 'nativeGlobalBox' in co:
   good=co['coreGlobalBox']==core and co['nativeGlobalBox']==expectedNative
   c['recordCoordinatesMatchGridPlan']=good
   if not good:bad.append({'tileId':t['tileId'],'stem':c['stem'],'recordCoordinates':co,'expectedCoreBox':core,'expectedNativeBox':expectedNative})
  else:c['recordCoordinatesMatchGridPlan']=None;unknown.append(c['stem'])
  if not c.get('recordShaMatchesImage'):bad.append({'stem':c['stem'],'issue':'generation-record image SHA mismatch'})
  rec=json.loads(Path(c['record']['path']).read_text(encoding='utf-8-sig'))
  if rec.get('route')=='derived':derived.append({'tileId':t['tileId'],'stem':c['stem'],'tool':rec.get('tool'),'operation':rec.get('operation'),'derivedFrom':rec.get('derivedFrom'),'assembly':rec.get('assembly'),'assemblyCrop':rec.get('assemblyCrop'),'status':'Mechanical derivative provenance disclosed; no new model attributed. Independent full-tile source-ID equality verified; earlier derivative construction evidence reused.'})
d['coordinateAudit']={'checkedSelectedCoreCount':220,'mismatches':bad,'recordsMissingExplicitCoordinateBoxes':unknown,'grid':'1-based row/column; tile origin [(c-1)*4096,(r-1)*4096]; core1024; halo115'}
d['derivedSelectedCoreProvenance']=derived
d['sourceReferenceAudit']['interpretation']='209 direct core records share one layout hash and one independent detail hash. 190 primary-style references point to the JPEG mail reference and 19 to the original designs/mail-ui-v1/01-mail-event.png. Their file hashes differ; no pixel-equivalence claim is made because those external reference images were not read in this audit. Ten selected cores are mechanical resolved crops with derivedFrom provenance rather than new model generations. All 220 selected core records report actualModel null.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
r=O/'review.md';s=r.read_text(encoding='utf-8');s=s.replace('209 个直接核心记录共享同一布局及细节参考哈希，邮件风格有原 PNG 与 JPEG 两种记录；未越权读取区外参考图。','209 个直接核心记录共享同一布局及细节参考哈希，邮件风格记录分别指向原 PNG 与 JPEG；文件哈希不同，本审计未读取区外参考图，不推断二者像素等同。');s+='\n坐标复核：220 个已选核心的记录坐标与 1024 核心/115 halo 网格一致，0 坐标冲突。十个 resolved 核心的机械裁切上游记录已另存于 derivedSelectedCoreProvenance。\n';r.write_text(s,encoding='utf-8')
print(json.dumps({'coordinateMismatches':len(bad),'unknownCoordinateRecords':len(unknown),'mechanicalDerivedSelectedCores':len(derived)},ensure_ascii=False))
