"""Package six reviewed tiles, retaining exact PNG bytes and generation evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile,shutil
from PIL import Image
import production_v2 as p
Z=Path(__file__).resolve().parent
D=Z/'joint-six-tile-review/ac2031be4f9bb37b'
J=Z/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70'
def sha(f): return p.sha(f)
def read(f): return p.read(f)
def ref(f): return {'file':str(f),'sha256':sha(f)}
def write(f,v): p.write_json(f,v,replace=True)
idx=read(D/'index.json');ext=read(D/'external-review.json')
assert ext['blockingCount']==0 and len(ext['entries'])==22
for e in ext['entries']:
 assert e['actuallyViewed'] and e['verdict']=='passed' and sha(e['file'])==e['sha256']
hard=Z/'r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.assembly.json'
a=read(hard)
reports=[Z/'r06_c06/qa/root-vertical-review-077556c4fb59.json',Z/'r06_c06/qa/horizontal-junction-review-hard-077556c4fb59.json']
seen={}
for f in reports:
 r=read(f); assert r['candidate']['sha256']==a['output']['sha256'] and r['blockingCount']==0
 for e in r['entries']:
  v=e.get('reference',e)
  assert e['actuallyViewed'] and e['verdict'].startswith('passed') and sha(v['file'])==v['sha256']
  seen[v['file']]=v['sha256']
assert len(seen)==33
for q in a['qa']: assert seen[q['file']]==q['sha256']
internal={'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'evidence':[ref(f) for f in reports]}
acceptance={'schemaVersion':1,'tile':'r06_c06','candidate':a['output'],'internalQA':internal,'externalQA':{'status':'pending','actuallyViewed':True,'reviewedSides':['north','west'],'worldBoundarySides':[],'evidence':ref(D/'external-review.json'),'pending':['east neighbor absent','south neighbor absent']},'formalAccepted':False,'actualModel':None,'actualQuality':None,'runtimeIntegration':False,'capacity5000Validated':False,'updatedAt':p.now()}
write(Z/'r06_c06/qa/acceptance.json',acceptance)
east=read(Z/'r05_c06/qa/acceptance.json')
assert east['internalQA']['status']=='passed'
east['externalQA'].update({'reviewedSides':['west','south'],'candidateBoundaryEvidence':ref(D/'external-review.json'),'pending':['north neighbor absent','east neighbor absent']})
east['updatedAt']=p.now();write(Z/'r05_c06/qa/acceptance.json',east)
prior=read(J/'delivery-summary.json')
assert prior['blockingCount']==0 and prior['status']=='joint_milestone_internal_visual_qa_passed'
manifests=[Path(prior['assemblyManifest']['file']),Z/'r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.assembly.json',hard]
source_refs=[];evidence=[];historical_reference_diagnostics=[]
for mf in manifests:
 m=read(mf)
 for s in m['nativeSources']:
  path=Path(s['file']); tile=s.get('tile',m.get('tile'))
  if tile is None: tile=path.parent.parent.name
  assert sha(path)==s['sha256'] and sha(p.selected_path(Z/tile,s['id']))==s['sha256']
  recpath=path.with_suffix('.png.generation.json');r=read(recpath)
  host=Path(r['evidence']['hostOutputPath'])
  assert sha(host)==sha(path)==r['sha256']
  assert r['route'] in ['builtin','builtin_image_gen'] and not r.get('resizedAfterGeneration',False)
  assert [r['width'],r['height']]==[1254,1254]
  for role in ['request','receipt','prompt']:
   v=s[role]
   assert sha(v['file'])==v['sha256']
  for v in r['references']:
   exists=Path(v['file']).is_file()
   matches=exists and sha(v['file'])==v['sha256']
   if not matches:
    assert tile in ['r05_c04','r05_c05','r06_c04','r06_c05']
    historical_reference_diagnostics.append({'tile':tile,'id':s['id'],'reference':v,'available':exists,'currentHashMatches':matches,'note':'Historical generation reference remains recorded exactly; it was not replaced or re-described. Host generated PNG hash matches native source exactly.'})
  source_refs.append({'tile':tile,'id':s['id'],'file':str(path),'sha256':sha(path),'hostMatchesExactly':True,'generationRecord':ref(recpath)})
  evidence.extend([(recpath,f'evidence/{tile}/{path.stem}.generation.json'),(Path(r['prompt']),f'prompts/{tile}/{path.stem}.txt')])
assert len(source_refs)==96
audit={'createdAtUtc':p.now(),'nativeSourceCount':96,'allHostOutputsExact':True,'nativePixelIssues':[],'historicalReferenceDiagnostics':historical_reference_diagnostics,'sources':source_refs}
write(D/'source-audit.json',audit)
for s in idx['sources']:
 assert sha(s['file'])==s['sha256']
 with Image.open(s['file']) as im: assert im.size==(4096,4096)
proofs=[J/'delivery-summary.json',Z/'r05_c06/qa/source-pixel-verification-03d4dd9f7332.json',Z/'r06_c06/qa/native-pixel-proof-077556c4fb59.json']
summary={'createdAtUtc':p.now(),'status':'six_contiguous_tiles_internal_and_shared_boundaries_passed','tiles':idx['sources'],'tilePixels':[4096,4096],'tileGrid':[3,2],'artWorldBox':[12288,16384,24576,24576],'tileCount':6,'ownedZoneTileCount':60,'wholeZoneComplete':False,'formalAccepted':False,'nativeSourceCount':96,'verifiedNativeOutputPixels':6*4096*4096,'sourceAudit':ref(D/'source-audit.json'),'firstFourReview':ref(J/'delivery-summary.json'),'newInternalReviews':[ref(Z/'r05_c06/qa/internal-review-03d4dd9f7332.json')]+[ref(f) for f in reports],'newBoundaryReview':ref(D/'external-review.json'),'pixelEvidence':[ref(f) for f in proofs],'blockingCount':0,'outerPerimeterStatus':'Real neighboring tiles remain unfinished/unreviewed.','actualModel':None,'actualQuality':None,'generationRoute':'builtin image_gen only','productionResampled':False,'runtimeIntegration':False}
write(D/'delivery-summary.json',summary)
readme='西北分区阶段成品：连续 3×2、共 6 张 4096×4096 PNG。\n排列：第一行 r05_c04、r05_c05、r05_c06；第二行 r06_c04、r06_c05、r06_c06。\n每张保留原始像素；无放大、变形、调色、羽化。96 张内置生成原稿的来源和提示词已记录。\n六块内部和相互边界检查通过。缩略预览仅供浏览，不是原图。\n整个西北60块尚未完成，外圈邻块仍在制作，尚未完成全区正式验收。\n'
(D/'DELIVERY.txt').write_text(readme,encoding='utf-8')
files=[(Path(s['file']),f'tiles/{s["tile"]}-4096.png') for s in idx['sources']]
files += [(D/'preview-only-1536.png','preview-only-1536.png'),(D/'DELIVERY.txt','DELIVERY.txt'),(D/'delivery-summary.json','delivery-summary.json'),(D/'source-audit.json','source-audit.json'),(D/'external-review.json','qa/external-review.json')]
files += [(f,'qa/'+f.name) for f in reports]
files += [(Z/'r05_c06/qa/internal-review-03d4dd9f7332.json','qa/r05_c06-internal-review.json')]
files += evidence
out=D/'northwest-six-4k-tiles.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as zip:
 for f,name in files: zip.write(f,name)
with zipfile.ZipFile(out) as zip:
 assert zip.testzip() is None
 for s in idx['sources']: assert hashlib.sha256(zip.read(f'tiles/{s["tile"]}-4096.png')).hexdigest()==s['sha256']
package={'createdAtUtc':p.now(),'file':str(out),'sha256':sha(out),'sizeBytes':out.stat().st_size,'verifiedZipEntries':len(files),'tileCount':6,'formalAccepted':False,'wholeZoneComplete':False,'summary':ref(D/'delivery-summary.json')}
write(D/'package.json',package)
print(json.dumps(package,ensure_ascii=False,indent=2))
