import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
OUT=Path(__file__).parent
ROOT=Path('D:/work/image')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def save(name,d):
 p=OUT/name;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
s=read(OUT/'snapshot.json');diag=read(OUT/'extension-diagnostic.json');checked=now()
special={
 'r02_c03_s04_03_a02-south-r03_c03':('failed_retained_strip_geometry','核心拼接线本身附近连贯，但北侧源的保留带在裁片 x≈115、y≈130 处出现明显矩形截断，蓝瓦排和右侧金边被横切；属于当前原生候选内已有问题，不能当作接缝通过。',[10350,8055,11264,8200]),
 'r02_c11_p04_01_v02-south-r03_c11':('geometry_continuous_material_pending','接线两侧石缝、红色圆板轮廓基本连续；南侧铺地与部分叶片明显失焦，与北侧清晰纹理形成水平质感变化，材质检查仍待修。',[40960,8080,41984,8448]),
 'extension-s11-east':('geometry_continuous_material_pending','花枝、石柱与石缝连接未见明显几何错位；道路阴影及局部植被存在偏软区域，本次保留清晰度复核项，不将整块材质验收标为通过。',[17152,8192,17664,9216])
}
reviews=[];issues=[]
for e in s['edges']:
 status,finding,box=special.get(e['id'],('locally_continuous_in_checked_crop','在该100%裁片范围内，跨线物体轮廓和主要纹理方向连续；不代表未查边或整块验收。',e['worldBox']))
 v={**e,'status':status,'finding':finding,'viewedAtUtc':checked,'viewMethod':'view_image original; 100pct indexed contact board; flagged strips also viewed individually','formalAccepted':False};reviews.append(v)
 if e['id'] in special:issues.append({'id':e['id'],'tileId':e['sources'][0].get('tileId','r03_c05'),'status':status,'finding':finding,'worldBox':box,'evidence':e['output'],'sources':e['sources']})
for h in s['holds']:
 issues.append({'id':'producer-hold-'+'_'.join(map(str,h['coordinate'])),'tileId':h['coordinate'][0],'status':'producer_failed_reused','finding':h['reason'],'evidence':h.get('review',h.get('reusedUnchangedQa')),'source':h['path'],'sha256':h['sha256']})
corners=[{**x,'status':'locally_continuous_in_checked_crop','finding':'该交汇512方形裁片内石缝、墙体或植物连接未见明显错位；仅限本交汇。','viewedAtUtc':checked,'formalAccepted':False} for x in diag['corners']]
save('visual-review.json',{'reviewedAtUtc':checked,'nativeScale':True,'newSeamStripCount':len(reviews),'newFourWayCount':len(corners),'edges':reviews,'corners':corners,'reusedPriorSeams':s['reusedChecks'],'unreviewedScope':'其余部分住宅块内部边与空缺外边未在本批宣称通过；扩展整块布局与其北/东/南邻块外边仍未验收。'})
save('repair-queue.json',{'openIssues':issues,'productionSelectionUnchangedByAudit':True,'priorFailedCandidatesRemainFailed':True})

# Verify saved crop and board pixels against frozen image paths.
replay=[]
for e in s['edges']:
 im=Image.open(e['output']['file']).convert('RGB')
 a=Image.open(e['sources'][0]['file']).convert('RGB').crop(e['sourceBoxes'][0]);b=Image.open(e['sources'][1]['file']).convert('RGB').crop(e['sourceBoxes'][1])
 ba=[0,0,1024,256] if e['direction']=='south' else [0,0,256,1024]
 bb=[0,256,1024,512] if e['direction']=='south' else [256,0,512,1024]
 ok=im.crop(ba).tobytes()==a.tobytes() and im.crop(bb).tobytes()==b.tobytes();assert ok
 replay.append({'id':e['id'],'pixelIdentical':ok})
for board in s['boards']:
 im=Image.open(board['file']['file']).convert('RGB')
 for p in board['panels']:
  e=next(x for x in s['edges'] if x['id']==p['id'])
  assert im.crop(p['destination']).tobytes()==Image.open(e['output']['file']).convert('RGB').tobytes()
save('pixel-replay.json',{'allSeamCropsExact':True,'stripCount':len(replay),'all7BoardsExact':True,'cropChecks':replay,'extensionAssembly':{'sourceReplayAll16PixelIdentical':True,'pixelsVerified':diag['pixelCountVerified']}})

# One terminal recheck and one late-file listing: do not chase new production.
records=s['native']+list(s['neighbors'].values())+[x['source'] for x in s['metadata']]+s['rules']
checks=[]
for v in records:
 p=Path(v['file']);h=sha(p) if p.exists() else None
 checks.append({'file':v['file'],'expectedSha256':v['sha256'],'currentSha256':h,'unchanged':h==v['sha256']})
save('source-recheck.json',{'checkedAtUtc':now(),'checks':checks,'unchangedCount':sum(x['unchanged'] for x in checks),'changed':[x for x in checks if not x['unchanged']]})
added=[]
for key,files in s['nativeListing'].items():
 folder=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013'/key/'native'
 for p in sorted(folder.glob('*.png')):
  if p.as_posix() not in files:added.append({'file':p.as_posix(),'sha256':sha(p),'notIncludedInFrozenCounts':True})
late_meta=[]
base=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013'
known={x['source']['file'] for x in s['metadata']}
for p in sorted((base/'island-east-residences/selections').glob('*/*.json'))+sorted((base/'island-west-residences').glob('c03-progress-v*.json')):
 if p.as_posix() not in known and p.stat().st_mtime_ns>max(x['source']['mtimeNs'] for x in s['metadata']):late_meta.append({'file':p.as_posix(),'sha256':sha(p),'notIncludedInFrozenCounts':True})
delta={'baseline':s['baseline'],'frozenAtUtc':s['frozenAtUtc'],'endCheckedAtUtc':now(),'newNativeIdsSinceBaseline':s['newNativeIdsSinceBaseline'],'newVersionCountSinceBaseline':len(s['newNativeIdsSinceBaseline']),'lateNativeFiles':added,'lateSelectionMetadata':late_meta,'changedFrozenInputs':[x for x in checks if not x['unchanged']],'policy':'Frozen counts retained; late files need their own review, no automatic adoption.'}
save('late-delta.json',delta)

for t in s['tiles']:
 t['evidence'].append({'file':(OUT/'snapshot.json').as_posix(),'sha256':sha(OUT/'snapshot.json')})
 t['visualReviewEvidence']=(OUT/'visual-review.json').as_posix()
 if t['tileId']=='r03_c05':
  t['diagnosticCandidate']={'file':diag['file'],'sha256':diag['sha256'],'nativeCoreCoverage':16,'adopted':False,'formalAccepted':False,'internalGeometry':'24 edge segments and 9 crossings locally continuous in inspected crops','materialStatus':'pending softness review','outerEdges':'west inspected; north/east/south pending'}
  t['coverageReason']='16 saved unique native cores have no production selection or adopted tile record; kept separate from effective selected coverage.'
summary={'schemaVersion':1,'status':'frozen_batch_audit_complete','createdAtUtc':now(),'frozenAtUtc':s['frozenAtUtc'],'baseline':s['baseline'],'counts':s['counts'],'tiles':s['tiles'],'unselectedNativeSources':[n for n in s['native'] if n['id'] not in s['selectionMap'].values()],'newNativeIdsSinceBaseline':s['newNativeIdsSinceBaseline'],'lateDelta':delta,'sourceImagesUnchanged':all(x['unchanged'] for x in checks if x['file'].endswith('.png')),'sourceMetadataChangedCount':sum(not x['unchanged'] for x in checks if not x['file'].endswith('.png')),'reviewedNewSeamCount':len(reviews),'reviewedNewCrossingCount':len(corners),'priorHashUnchangedSeamsReused':sum(x['reused'] for x in s['reusedChecks']),'openIssueCount':len(issues),'outputs':{k:(OUT/k).as_posix() for k in ['snapshot.json','visual-review.json','repair-queue.json','pixel-replay.json','source-recheck.json','late-delta.json','extension-diagnostic.json']},'scopeNotes':['coreCount counts explicit effective production selections with source SHA verified; each coordinate counted once.','adopted means a complete4096 production tile adopted, never a quick selected core.','All file/sha256 pairs at tile level remain null because no production4096 adopted tile exists in these14 coordinates. Diagnostic candidate is separate.','Held c02_s04_02 and s04_03 excluded despite early provisional continuation on older source.','93 saved versions and71 saved unique cores are not44 selected cores and not formal acceptance.','No production writes, no image generation or AI edits, no shared Git mutation.'],'generationPerformed':False,'productionWrites':False,'sharedGitTouched':False,'formalAcceptedCount':0}
save('summary.json',summary)
print(json.dumps({'counts':summary['counts'],'sourceImagesUnchanged':summary['sourceImagesUnchanged'],'openIssueCount':len(issues),'lateNativeFiles':len(added),'lateSelectionMetadata':len(late_meta),'summary':str(OUT/'summary.json')},ensure_ascii=False,indent=2))
