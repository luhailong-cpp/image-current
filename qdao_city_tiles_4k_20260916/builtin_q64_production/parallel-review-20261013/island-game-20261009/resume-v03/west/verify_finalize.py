import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
import numpy as np
O=Path(__file__).parent;A=O.parents[1];P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009')
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
j=read(O/'source-delta.json');tm={t['tileId']:t for z in j['zones'].values() for t in z['tiles']};es={e['id'][:3]:e for e in j['edges']};old=read(A/'resume-v02/west/summary.json')
# Verify adopted min-error candidate pixels against its explicit source-ID mask.
t=tm['r12_c03'];ca=t['adopted4kCandidate']['statusRecord'];rp=Path(ca['sourceReport']);rdata=rp.read_bytes();(O/'snapshots/r12c03-candidate-report.json').write_bytes(rdata);r=json.loads(rdata.decode('utf-8-sig'))
maskpath=ca['sourceIdMask'];cand=np.array(Image.open(t['file']).convert('RGB'));mask=np.array(Image.open(maskpath));validation=[];totalbad=0;totalcovered=0
for s in r['inputs']:
 sid=s['sourceId'];box=s['nativeGlobalBox'];tx=box[0]-8192;ty=box[1]-45056;x0=max(tx,0);y0=max(ty,0);x1=min(tx+1254,4096);y1=min(ty+1254,4096)
 src=np.array(Image.open(s['path']).convert('RGB'));cut=src[y0-ty:y1-ty,x0-tx:x1-tx];sel=mask[y0:y1,x0:x1]==sid;bad=int(np.count_nonzero(np.any(cand[y0:y1,x0:x1]!=cut,axis=2)&sel));count=int(sel.sum());totalbad+=bad;totalcovered+=count
 validation.append({'sourceId':sid,'path':s['path'],'recordedSha256':s['sha256'],'actualSha256':sha(s['path']),'selectedPixelCount':count,'mismatchCount':bad})
save(O/'r12c03-pixel-verification.json',{'candidate':t['file'],'sha256':t['sha256'],'sourceIdMask':maskpath,'sourceIdMaskSha256':sha(maskpath),'sourceReport':str(rp),'sourceReportSha256':hashlib.sha256(rdata).hexdigest(),'sourceCount':16,'coveredPixelCount':totalcovered,'mismatchedPixelCount':totalbad,'allSourceHashesMatch':all(s['actualSha256']==s['recordedSha256'] for s in validation),'inputs':validation,'comparisonWithPriorDiagnostic':j['candidatePixelComparisons'][0],'interpretation':'Native-coordinate provenance only; does not imply visual acceptance.'})
# Persist actual original-pixel reviews. No unviewed board is marked as passed.
for e in j['edges']:
 e.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,reviewer='west_v03_delta',status='local_shared_edge_visual_passed',finding='No obvious geometry break or material step at this inspected seam segment.')
for id in ['001']:
 es[id].update(status='geometry_and_material_repair_required',finding='A horizontal hard cut changes yellow flower/leaf shapes and sharpness across the r06/r07 shared edge.')
for id in ['002','003']:
 es[id].update(status='geometry_continuous_material_review_required',finding='Paving outlines continue; tonal/grain difference around the old/new boundary remains open for paired material review.')
for id in ['023','024','031','032','033','034']:
 es[id].update(status='retained_rectangular_material_band_requires_repair',finding='Visible rectangular bamboo/foliage texture step within seam crop, including retained strips about 115 px before a horizontal core/tile boundary. Do not count the tile material as passed.')
es['013'].update(status='geometry_pass_material_review_required',finding='The prior straight red-column texture change about 115 px west of the tile edge persists.')
prior=read(A/'resume-v02/west/partial-edges-reviewed.json')['edges'];reuse=[]
for eid,pi in [('013',0),('014',1)]:
 a=Image.open(es[eid]['path']).convert('RGB');b=Image.open(prior[pi]['path']).convert('RGB');eq=a.size==b.size and not ImageChops.difference(a,b).getbbox()
 reuse.append({'newEdgeId':es[eid]['id'],'priorEvidence':prior[pi]['path'],'identicalDecodedCropPixels':eq,'priorStatus':prior[pi]['status']})
 es[eid]['priorEvidenceReusable']=eq
j['reusedPartialEdges']=reuse
extra=read(O/'extra-checks.json')
for x in extra:
 x['actuallyViewed']=True;x['viewedAtOriginalPixelScale']=True
 x['status']='geometry_initial_review_material_repairs_open' if x['tileId']=='r08_c02' else 'localized_internal_geometry_repairs_and_north_material_issue_open'
 for b in x['boards']:
  b['actuallyViewed']=True;b['status']='local_seam_review_passed_except_reported_localized_repairs'
  if b['axis']=='vertical' and b['boundary']==3:b['status']='row4_wood_groove_repair_required'
  if b['axis']=='horizontal' and b['boundary']==3:b['status']='column3_wood_highlight_repair_required'
 if x.get('northBoard'):x['northBoard']['actuallyViewed']=True;x['northBoard']['status']='north_segment1_retained_material_band_repair_required'
 x['crossings']['actuallyViewed']=True;x['crossings']['status']='no_additional_junction_geometry_break_found; listed material/wood issues remain open'
save(O/'extra-checks.json',extra)
issues=[dict(v,reuseBasis='Prior source/candidate inputs unchanged unless explicitly rechecked in v03.') for v in old['issues']]
issues[0].update(evidence=str(O/'extra-crops/r12_c03-north-segment-1.png'),reuseBasis='New adopted candidate explicitly rechecked; the same horizontal band remains visible at local y115.')
issues.extend([
 {'id':'r07c04-north-flower-cut','tileId':'r07_c04','pair':['r06_c04','r07_c04'],'status':'geometry_and_material_repair_required','worldApproxBox':[13312,24550,14336,24610],'finding':es['001']['finding'],'evidence':es['001']['path']},
 {'id':'r07c04-north-paving-material','tileId':'r07_c04','pair':['r06_c04','r07_c04'],'status':'material_review_required','worldApproxBox':[14336,24520,16384,24680],'finding':'Paving outline continuity is present; keep grain/tone transition pending paired review.','evidence':[es['002']['path'],es['003']['path']]},
 {'id':'r08c02-internal-bamboo-retained-band','tileId':'r08_c02','status':'material_repair_required','worldApproxBox':[4860,31600,6170,31670],'finding':'A rectangular retained strip cuts bamboo/foliage texture near local y2957 (115 px north of the row3/row4 core boundary).','evidence':[es['023']['path'],es['024']['path'],str(O/'extra-crops/r08_c02-nine-crossings.png')]},
 {'id':'r08c02-south-bamboo-retained-band','tileId':'r08_c02','pair':['r08_c02','r09_c02'],'status':'material_repair_required','worldApproxBox':[4096,32620,6144,32690],'finding':'Straight rectangular texture changes cross multiple bamboo trunks about 115 px north of the shared tile edge.','evidence':[es['032']['path'],es['034']['path']]},
 {'id':'r12c03-wood-v3-row4','tileId':'r12_c03','status':'localized_geometry_repair_required','worldApproxBox':[11230,48120,11310,48200],'finding':'Small horizontal wood-board groove/highlight discontinuity persists near vertical core boundary x3072. Current production also lists it as pending.','evidence':str(O/'extra-crops/r12_c03-vertical-3-segment-4.png')},
 {'id':'r12c03-wood-h3-column3','tileId':'r12_c03','status':'localized_geometry_repair_required','worldApproxBox':[10540,48070,10690,48160],'finding':'A jagged bright wooden groove remains near horizontal core boundary y3072. Current production also lists it as pending.','evidence':str(O/'extra-crops/r12_c03-horizontal-3-segment-3.png')}
])
save(O/'repair-queue.json',issues)
newcontract=[]
for s in j['newCoreEvidence']:
 rec=s['record'];r=int(s['tileId'][1:3]);c=int(s['tileId'][5:7]);x=(c-1)*4096+(s['subcolumn']-1)*1024;y=(r-1)*4096+(s['subrow']-1)*1024;coords=rec.get('coordinates');expected=[x,y,x+1024,y+1024]
 newcontract.append({'tileId':s['tileId'],'subrow':s['subrow'],'subcolumn':s['subcolumn'],'path':s['image']['path'],'sha256':s['image']['sha256'],'nativeDimensions':s['image']['dimensions'],'sizeValid':s['image']['dimensions']==[1254,1254],'expectedCoreGlobalBox':expected,'recordedCoreGlobalBox':coords.get('coreGlobalBox') if coords else None,'recordedCoordinatesMatch':coords.get('coreGlobalBox')==expected if coords else None,'recordedImageHashMatches':rec.get('sha256')==s['image']['sha256'],'actualModel':rec.get('actualModel'),'modelEvidence':'actual model not returned' if rec.get('actualModel') is None else rec['actualModel']})
save(O/'new-core-contract-check.json',newcontract)
# One end check of frozen current inputs only; later metadata changes are a separate delta.
endmeta=[]
for m in j['metadata']:
 h=sha(m['path'])
 if h!=m['sha256']:endmeta.append({'path':m['path'],'snapshotSha256':m['sha256'],'endSha256':h,'snapshotReadAtUtc':m['readAtUtc']})
allims={}
for z in j['zones'].values():
 for t in z['tiles']:
  for s in t['selectedSources']:allims[s['path']]=s['sha256']
  if t['adopted4kCandidate']:allims[t['file']]=t['sha256']
changes=[{'path':p,'snapshotSha256':h,'endSha256':a} for p,h in allims.items() if (a:=sha(p))!=h]
j.update(status='frozen_incremental_review_complete',completedAtUtc=now(),laterMetadataChanges=endmeta,endImageChanges=changes,endInputImageCount=len(allims),extraChecks=str(O/'extra-checks.json'),issues=issues)
save(O/'source-delta.json',j)
summary={k:v for k,v in j.items() if k not in ['newCoreEvidence','edges','boards','metadata']};summary['zones']={z:{**d,'tiles':[{k:v for k,v in t.items() if k not in ['selectedSources','adopted4kCandidate']} for t in d['tiles']]} for z,d in j['zones'].items()};summary['tiles']=[{'zone':z,**t} for z,d in summary['zones'].items() for t in d['tiles']];summary['unchangedAdoptedCandidateCount']=23;summary['reviewedNativeEdgeSegments']=len(j['edges'])+28;summary['reviewedNativeCrossings']=18;summary['priorWholeZoneFindingsRemainApplicable']=True;summary['priorWholeZoneReports']=[str(A/'northwest-audit-v01/review.md'),str(A/'southwest-audit-v01/review.md'),str(A/'resume-v02/west/review.md')];summary['limitations']=['FullCoverage means 16 selected native cores; it is not formal acceptance.','r05_c02 and r08_c02 files are independent audit diagnostic assemblies, not production adopted outputs.','All unfilled coordinates/edges remain pending.','Reserved parallel-production coordinates are audited by the root or its dedicated parallel worker, outside this NW/SW production selection scope.'];save(O/'summary.json',summary)
print(json.dumps({'completedAtUtc':j['completedAtUtc'],'sourceImages':len(allims),'changedImages':changes,'laterMetadataChanges':endmeta,'r12PixelMismatch':totalbad,'r12CoveredPixels':totalcovered,'newCoreContractErrors':[c for c in newcontract if not c['sizeValid'] or c['recordedCoordinatesMatch'] is False or not c['recordedImageHashMatches']],'issues':len(issues)},ensure_ascii=False))
