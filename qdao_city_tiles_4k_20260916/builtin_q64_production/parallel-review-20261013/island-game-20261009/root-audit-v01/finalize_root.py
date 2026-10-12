from pathlib import Path
from PIL import Image,ImageChops
from collections import defaultdict
from datetime import datetime,timezone
import json,hashlib,gc
O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
now=datetime.now(timezone.utc).isoformat()
inventory=read(O/'inventory.json'); tiles={t['tileId']:t for t in inventory['tiles']}
issues=[];groups=[]
for d in sorted(O.glob('g0*')):
 p=d/'manifest.json'
 if not p.exists():continue
 q=read(p)
 if len(q['seams'])==4:
  for e in q['seams']:e.update(status='passed_shared_edge_geometry_and_material_visual100pct',actuallyViewed=True,reviewedAtUtc=now)
  q['scope']='only NW/SW r07_c03-r08_c03 boundary; tile internals and missing r07_c04 cross remain open'
  q['status']='local_shared_edge_passed_missing_fourth_cross_neighbor'
 else:
  for e in q['seams']:
   e.update(status='passed_shared_edge_visual100pct',actuallyViewed=not d.name.startswith('g01'),reviewedAtUtc=now)
   if d.name.startswith('g01'):e['reviewMethod']='reuse four current candidate exact-source QA reports; see inventory source hashes; subject to explicit material exception below'
  q['cross'].update(status='passed_geometry_visual100pct',actuallyViewed=not d.name.startswith('g01'))
  q['status']='four_tile_local_shared_edges_passed_perimeter_unreviewed'
  badname='v-2-segment-4-100pct.png' if d.name.startswith('g01') else 'v-1-segment-4-100pct.png' if d.name.startswith('g02') else None
  if badname:
   for e in q['seams']:
    if Path(e['file']).name==badname:
     e.update(status='material_repair_required',finding='At world x53248 near y7900-8050 the sea caustic/blue field has a straight rectangular change. Geometry is continuous, but texture is not accepted.',actuallyViewed=True)
     issues.append({'id':'coast-c13-c14-blue-material-band','pair':['r02_c13','r02_c14'],'worldApproxBox':[53120,7870,53376,8120],'status':'needs_AI_material_repair_by_production_owner','evidence':e,'sourceFiles':[t for t in q['inputs'] if t['tileId'] in ['r02_c13','r02_c14']]})
   q['status']='geometry_local_passed_material_repair_required'
   q['cross']['status']='geometry_passed_material_issue_continues_north'
  # Each native output is verified by exact coordinate recrop against its current input snapshot.
  q['pixelReplay']=[]
  x0,y0=q['worldBox'][:2]
  with Image.open(q['output']['file']) as joined:
   for src in q['inputs']:
    sx,sy=src['worldBox'][:2]
    with Image.open(src['file']) as im:
     cr=joined.crop((sx-x0,sy-y0,sx-x0+4096,sy-y0+4096));ok=ImageChops.difference(cr.convert('RGB'),im.convert('RGB')).getbbox() is None;cr.close()
    assert ok,src
    q['pixelReplay'].append({'tileId':src['tileId'],'sameCoordinatePixelsIdentical':True})
 q['reviewedAtUtc']=now;q['formalAccepted']=False
 write(p,q);groups.append({'group':d.name,'status':q['status'],'manifest':p.as_posix()});gc.collect()

refs=defaultdict(lambda:{'recordedHashes':set(),'sourceCount':0,'roles':set()})
for t in inventory['tiles']:
 for src in t['sources']:
  for r in src.get('references') or []:
   if not isinstance(r,dict):continue
   p=r.get('file',r.get('path'))
   if not p:continue
   if any(s in p.lower() for s in ['penglai-natural-stone','mail-daoist','mail-event','team-ui']):
    refs[p]['recordedHashes'].add(r.get('sha256'));refs[p]['sourceCount']+=1;refs[p]['roles'].add(r.get('role',''))
refout=[{'file':p,'recordedHashes':sorted(s for s in d['recordedHashes'] if s),'sourceCount':d['sourceCount'],'roles':sorted(d['roles'])} for p,d in refs.items()]
write(O/'reference-selection-audit.json',{'scope':'historical submitted reference records; does not claim current required refs were retroactively attached','records':refout,'layoutAuthorityExpectedSha256':'e7a06f547274a29a01cc4e20223637e99c0fab534d4982361e824147c800b34f','detailAuthorityExpectedSha256':'40ca8d6b5b062511ebd18dc0e278399644097ee10608000658f691796884c133','existingActualImageModel':'unconfirmed','newImageCalls':0,'currentPolicy':'free/existing GPT Image2.5 preferred; builtin2.0 fallback allowed; independent review only'})

snapshot=read(O/'input-snapshot.json');changes=[]
for i,e in enumerate(snapshot['files']):
 p=Path(e['file']);current=sha(p) if p.exists() else None
 if current!=e['sha256']:changes.append({'file':e['file'],'snapshotSha256':e['sha256'],'currentSha256':current})
print('root_rehash',len(snapshot['files']),len(changes),flush=True)
changedpaths={c['file'] for c in changes}
for t in inventory['tiles']:
 relevant={t.get('file'),t.get('selectionFile')}
 relevant.update(s['file'] for s in t['sources']);relevant.update(s['generationRecord'] for s in t['sources'])
 relevant.update(o['record'] for o in t['overlays']);relevant.update(o['source'] for o in t['overlays'])
 t['snapshotStale']=bool(relevant & changedpaths)
inventory.update(completedAtUtc=datetime.now(timezone.utc).isoformat(),sourceChangeAudit={'inputCount':len(snapshot['files']),'changed':changes,'snapshotStale':bool(changes)},reviewGroups=groups)
write(O/'inventory.json',inventory)
dedup={}
for issue in issues:dedup[issue['id']]=issue
issues=list(dedup.values())
issues.append({'id':'r03c10-stone-face-straight-band','tileId':'r03_c10','status':'needs_AI_material_repair_by_production_owner','worldApproxBox':[39750,9216,39900,10240],'finding':'Existing current root review requires material repair at native x1024 in selected r03_c10_p02_03_v2; core origin + crop offset places its vertical band near global x39821.','reviewRecord':'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/qa/r03_c10-native-v1-20261012-review.json','source':{'file':tiles['r03_c10']['file'],'sha256':tiles['r03_c10']['sha256']}})
write(O/'repair-queue.json',issues)
text='''# 八仙岛东北及跨区接缝检查

东北主区选择矩阵核实为12张完整候选和3张部分候选，215个1024核心；海岸加速区独占4坐标、64核心。共279核心，16张完整覆盖。16张现行成图均与当前核心及采用覆盖片的逐像素回放相等。完整覆盖不等于内部或全图验收，正式验收仍为0。

四组8192平方图均为4张4096候选按世界坐标硬拼，导出后再逐块回裁验证像素相等。g03与g04的共享接边和交叉点本次100%查看通过，外围仍待邻块验收，可作局部原生交付。g01及g02保留海水材质待修，不列作无缺陷局部交付。

海岸 r02_c13、r02_c14 对主区 r03_c13、r03_c14 的8张旧南北接边裁片，与当前重新裁出的RGB像素完全相等，可以复用通过证据。但海岸 c13/c14 竖边在世界x53248、y约7900至8050仍有直线蓝色材质带；本次原尺寸复看保留待修。东北 r03_c10 的石面直带按现行来源评语继续开放。

西北 r07_c03 对西南 r08_c03 的4096共享横边分4段实际查看，轮廓、石缝与颜色连续。此结论只覆盖共享边，两块的内部遗留问题继续开放。右侧 r07_c04 缺失，世界12288、28672四交叉点不能验收。

原生产目录、progress、AGENTS及Git均未由本窗口改写。审核零生图；当前规则允许免费现有入口2.5优先，不可用时内置2.0继续。已有图实际型号未确认。每个结论只适用于JSON列明hash的版本，来源变更后按sourceChangeAudit或snapshotStale失效。
'''
(O/'review.md').write_text(text,encoding='utf-8')
print('complete',inventory['sourceChangeAudit'],flush=True)
