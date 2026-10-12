from pathlib import Path
from datetime import datetime,timezone
from PIL import Image, ImageChops
import json,hashlib,io,contextlib,importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base_audit',HERE/'audit_provenance.py')
A=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(A)
R=A.R;Q=A.Q;sha=A.sha;read=A.read;fileinfo=A.fileinfo;norm=A.norm;issues=A.issues
def issue(scope,kind,description):A.msg(scope,kind,description)
def truth(v,scope,kind,desc):
 if not v:issue(scope,kind,desc)
 return v
def imageeq(a,b):return a.mode==b.mode and a.size==b.size and a.tobytes()==b.tobytes()
repairs=[]
# Builtin color repair: its generation evidence is recorded in versioned composite manifest.
cm_path=R/'r03_c10/candidate/r03_c10-4096-candidate-v2.manifest.json';cm=read(cm_path);cr=cm['repairNative']
cp=Path(cr['file']);cd=list(Image.open(cp).size);request=read(cm['request']['file']);receipt=read(cm['receipt']['file'])
ce={'kind':'builtin_parasol_color_repair','image':fileinfo(cp),'nativeDimensions':cd,'recordedDimensions':cr['measuredDimensions'],'record':fileinfo(cm_path),'prompt':fileinfo(cm['prompt']['file']),'request':fileinfo(cm['request']['file']),'receipt':fileinfo(cm['receipt']['file']),'actualModel':cr.get('actualModel'),'actualQuality':cr.get('actualQuality'),'unknownReason':cr.get('unknownReason'),'references':[],'checks':{}}
cc=ce['checks'];scope='color-repair'
cc['dimension1254']=truth(cd==[1254,1254] and cd==cr['measuredDimensions'],scope,'dimensions','Native color repair size mismatch.')
cc['shaMatches']=truth(sha(cp)==cr['sha256'],scope,'sha','Native color repair SHA mismatch.')
cc['modelQualityUnknown']=truth(cr.get('actualModel','missing') is None and cr.get('actualQuality','missing') is None and bool(cr.get('unknownReason')),scope,'unknown_metadata','Color repair model/quality unknown evidence missing.')
cc['builtinRoute']=truth(cr.get('tool')=='image_gen__imagegen' and cr.get('route')=='builtin',scope,'route','Color repair builtin evidence missing.')
cc['promptExact']=truth(A.promptnorm(Path(cm['prompt']['file']).read_text(encoding='utf-8-sig'))==A.promptnorm(request['prompt']),scope,'prompt','Prompt and request differ.')
cc['receiptUnknown']=truth(receipt.get('actualModel','missing') is None and receipt.get('actualQuality','missing') is None,scope,'receipt_metadata','Receipt metadata unexpectedly disclosed/absent.')
for p in request.get('referenced_image_paths',[]):
 fi=fileinfo(p);ce['references'].append(fi);truth(fi['exists'],scope,'reference_missing',p)
cc['referencePathsMatch']=truth([norm(p) for p in request['referenced_image_paths']]==[norm(cm['referenceEditTarget']['file'])],scope,'refs','Color reference mismatch.')
dep=[];A.check_manifest_hash_objects(cm,scope,dep);ce['dependencyHashes']=dep
repairs.append(ce)
# Builtin gold repair standalone generation record.
gold=R/'r04_c10/repairs/north-gold-v1'
gp=gold/'repair-native.generation.json';g=read(gp);src=Path(g['file']);dims=list(Image.open(src).size)
pp=Path(g['promptFile']);qp=Path(g['requestFile']);rp=gold/'repair.receipt.json';req=read(qp);rc=read(rp)
ge={'kind':'builtin_gold_boundary_repair','image':fileinfo(src),'nativeDimensions':dims,'recordedDimensions':g.get('nativeDimensions'),'record':fileinfo(gp),'prompt':fileinfo(pp),'request':fileinfo(qp),'receipt':fileinfo(rp),'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'unknownReason':g.get('unknownReason'),'references':[],'checks':{}}
ck=ge['checks'];scope='gold-repair'
ck['dimension1254']=truth(dims==[1254,1254] and dims==g.get('nativeDimensions'),scope,'dimensions','Gold native dimensions mismatch.')
ck['shaMatches']=truth(sha(src)==g.get('sha256'),scope,'sha','Gold native SHA mismatch.')
ck['noNativeResizing']=truth(g.get('nativePixelsResized') is False,scope,'resizing','Gold native resize flag missing/true.')
ck['modelQualityUnknown']=truth(g.get('actualModel','missing') is None and g.get('actualQuality','missing') is None and bool(g.get('unknownReason')),scope,'metadata','Gold model/quality unknown evidence missing.')
ck['builtinRoute']=truth(g.get('tool')=='image_gen__imagegen' and g.get('route')=='builtin',scope,'route','Gold route mismatch.')
ck['promptExact']=truth(A.promptnorm(pp.read_text(encoding='utf-8-sig'))==A.promptnorm(req.get('prompt',''))==A.promptnorm(g.get('prompt','')),scope,'prompt','Gold prompt/request/record mismatch.')
ck['receiptExact']=truth(rc==g.get('receipt'),scope,'receipt','Gold receipt mismatch.')
ck['referencePathsExact']=truth([norm(p) for p in req.get('referenced_image_paths',[])]==[norm(r['file']) for r in g.get('references',[])],scope,'refs','Gold reference paths mismatch.')
for ref in g.get('references',[]):
 fi=fileinfo(ref['file']);fi['shaMatches']=fi.get('sha256')==ref.get('sha256');ge['references'].append(fi)
 truth(fi['exists'] and fi['shaMatches'],scope,'reference','Gold reference missing/SHA mismatch.')
repairs.append(ge)
proposal_path=gold/'proposal.json';proposal=read(proposal_path)
rgba=Image.open(proposal['rgbaFile']);mask=Image.open(proposal['maskFile'])
gold_image=Image.open(src).convert('RGB')
proposal_checks={'proposal':fileinfo(proposal_path),'rgba':fileinfo(proposal['rgbaFile']),'mask':fileinfo(proposal['maskFile']),'native':fileinfo(proposal['nativeFile']),'nativeDimensions':list(gold_image.size),'checks':{}}
pc=proposal_checks['checks']
pc['nativeSha']=truth(sha(src)==proposal['nativeSha256'],scope,'proposal_native_sha','Proposal native SHA mismatch.')
pc['rgbaSha']=truth(sha(proposal['rgbaFile'])==proposal['rgbaSha256'],scope,'rgba_sha','RGBA SHA mismatch.')
pc['maskSha']=truth(sha(proposal['maskFile'])==proposal['maskSha256'],scope,'mask_sha','Mask SHA mismatch.')
pc['rgbaDimensions']=truth(list(rgba.size)==proposal['roiDimensions']==[280,180] and rgba.mode=='RGBA',scope,'rgba_dimensions','RGBA dimensions/mode mismatch.')
pc['maskEqualsRgbaAlpha']=truth(imageeq(mask.convert('L'),rgba.getchannel('A')),scope,'mask_pixels','Mask differs from RGBA alpha.')
pc['roiPixelsEqualNativeUnscaledCrop']=truth(imageeq(rgba.convert('RGB'),gold_image.crop(proposal['roiContextBox'])),scope,'roi_resampling','RGBA RGB differs from exact native crop.')
checks_contributions=[]
for c in proposal['tileContributions']:
 t=c['tile'];r=int(t[1:3]);col=int(t[5:7]);d=c['destinationLocalBox'];s=c['sourceRoiCrop'];globaldest=[(col-1)*4096+d[0],(r-1)*4096+d[1],(col-1)*4096+d[2],(r-1)*4096+d[3]]
 expected=[proposal['roiGlobalBox'][0]+s[0],proposal['roiGlobalBox'][1]+s[1],proposal['roiGlobalBox'][0]+s[2],proposal['roiGlobalBox'][1]+s[3]]
 ok=globaldest==expected and d[2]-d[0]==s[2]-s[0] and d[3]-d[1]==s[3]-s[1]
 truth(ok,scope,'contribution_coordinates','Gold contribution global coordinate or size mismatch: '+t)
 checks_contributions.append({'tile':t,'globalDestinationBox':globaldest,'expected':expected,'matches':ok})
proposal_checks['tileCoordinates']=checks_contributions
proposal_checks['snapshotNote']='Proposal status/notAppliedToCandidates fields are retained as the pre-integration proposal snapshot. New final candidate manifests are the records of integration.'
finals=[]
picks={'r03_c10':'r03_c10-4096-candidate-v4.png','r03_c11':'r03_c11-4096-candidate-v2.png','r04_c10':'r04_c10-4096-candidate-v2.png','r04_c11':'r04_c11-4096-candidate-v1.png'}
base_results={x['tile']:x for x in A.candidate_results}
for tile,name in picks.items():
 p=R/tile/'candidate'/name;mp=p.with_suffix('.manifest.json');m=read(mp);im=Image.open(p).convert('RGB');entry={'tile':tile,'candidate':fileinfo(p),'manifest':fileinfo(mp),'nativeDimensionsOfContributingGeneration':[1254,1254],'compositeDimensions':list(im.size),'manifestDimensions':m.get('dimensions'),'actualModel':m.get('actualModel',None),'actualQuality':m.get('actualQuality',None),'formalAccepted':m.get('formalAccepted'),'checks':{},'dependencyHashes':[]}
 scope=tile+':final';c=entry['checks']
 c['shaMatches']=truth(sha(p)==m.get('sha256'),scope,'candidate_sha','Final candidate SHA mismatch.')
 c['dimensions4096']=truth(list(im.size)==m.get('dimensions')==[4096,4096],scope,'dimensions','Final candidate dimensions mismatch.')
 A.check_manifest_hash_objects(m,scope,entry['dependencyHashes'])
 if tile in ['r03_c10','r04_c10']:
  b=Path(m['baseCandidate']['file']);bm=b.with_suffix('.manifest.json');base=Image.open(b).convert('RGB');replay=base.copy()
  truth(sha(proposal_path)==m['repairProposal']['sha256'],scope,'proposal_sha','Final proposal SHA mismatch.')
  contribution=m['roiContribution'];repair=rgba.crop(contribution['sourceRoiCrop']);d=contribution['destinationLocalBox']
  replay.paste(repair,d[:2],repair.getchannel('A'))
  c['pixelExactGoldReplay']=truth(imageeq(replay,im),scope,'pixel_replay','Final differs from exact recorded unscaled gold composite.')
  c['recordedNoResampling']=truth(m.get('nativePixelsResized') is False,scope,'resampling','No-resampling declaration missing/false.')
  c['baseChainPreviouslyPixelVerified']=base_results[tile].get('pixelExactDocumentedCompositeVerified',base_results[tile].get('pixelExactCoreAssemblyVerified',False))
  truth(c['baseChainPreviouslyPixelVerified'],scope,'base_chain','Base chain was not independently verified.')
  c['nativeRepairRecordMatches']=truth(norm(m['nativeRepair']['file'])==norm(src) and m['nativeRepair']['sha256']==sha(src) and m['nativeRepair']['dimensions']==dims,scope,'native_record','Final native repair record mismatch.')
  c['rgbaAndMaskHashesMatch']=truth(m['rgbaSha256']==sha(proposal['rgbaFile']) and m['maskSha256']==sha(proposal['maskFile']),scope,'mask_hash','Final mask/RGBA hash mismatch.')
  # Difference bounding box must be confined to declared ROI. Uses image comparison only, no output editing.
  diff=ImageChops.difference(base,im);bbox=diff.getbbox();entry['changedBoundingBox']=list(bbox) if bbox else None
  c['changesConfinedToDeclaredRoi']=truth(bbox is None or (bbox[0]>=d[0] and bbox[1]>=d[1] and bbox[2]<=d[2] and bbox[3]<=d[3]),scope,'outside_roi_change','Pixels changed outside recorded gold contribution.')
  entry['noResamplingEvidence']='Final independently reconstructed byte-for-byte from verified base plus exact native RGBA crop and recorded alpha; original base chain independently verified at scale1.'
 else:
  c['pixelExactCoreAssemblyVerified']=truth(base_results[tile].get('pixelExactCoreAssemblyVerified') is True,scope,'core_assembly','Final core assembly not pixel-exact.')
  entry['noResamplingEvidence']='Exact RGB equality to 16 native 1024 center crops.'
 finals.append(entry)
raw_inventory=[]
for n in A.all_generations:
 raw_inventory.append({'file':n['image']['file'],'sha256':n['image'].get('sha256'),'nativeDimensions':n['checks']['measuredDimensions'],'actualModel':n['metadata'].get('actualModel'),'actualQuality':n['metadata'].get('actualQuality'),'unknownReason':n['metadata'].get('unknownReason'),'kind':'core_native_version','selected':n['selected'],'record':n['generationRecord']['file'],'prompt':n['promptFile']['file'],'request':n['requestFile']['file'],'receipt':n['receiptFile']['file']})
for n in repairs:
 raw_inventory.append({'file':n['image']['file'],'sha256':n['image']['sha256'],'nativeDimensions':n['nativeDimensions'],'actualModel':n['actualModel'],'actualQuality':n['actualQuality'],'unknownReason':n['unknownReason'],'kind':n['kind'],'selected':True,'record':n['record']['file'],'prompt':n['prompt']['file'],'request':n['request']['file'],'receipt':n['receipt']['file']})
unique_paths={norm(x['file']) for x in raw_inventory}
unique_shas={x['sha256'] for x in raw_inventory}
raw_counts={'selectedCoreCount':len(A.selected),'coreNativeVersionCount':len(A.all_generations),'unselectedCoreVersionCount':sum(not x['selected'] for x in A.all_generations),'additionalBuiltinRepairCount':len(repairs),'rawGeneratedImageCount':len(raw_inventory),'uniqueRawGeneratedFiles':len(unique_paths),'uniqueRawImageSha256Count':len(unique_shas),'allRawNativeDimensions1254':all(x['nativeDimensions']==[1254,1254] for x in raw_inventory),'allActualModelQualityUnknown':all(x['actualModel'] is None and x['actualQuality'] is None and bool(x['unknownReason']) for x in raw_inventory)}
now=datetime.now(timezone.utc)
summary={'auditedAt':now.isoformat(),'status':'PASS' if not issues and A.coverage['complete'] and len(finals)==4 else 'FAIL','scope':A.TILES,'readOnlyOutsideAuditFolder':True,'coverage':A.coverage,'rawCounts':raw_counts,'finalCandidatePicks':[{k:v for k,v in x.items() if k in ['tile','candidate','compositeDimensions']} for x in finals],'errors':sum(x['severity']=='error' for x in issues),'warnings':sum(x['severity']=='warning' for x in issues),'pending':A.pending,'issues':issues,'noResizingConclusion':'Four final candidates independently verified from 1254 native generations, 1024 crops, true native overlaps and recorded alpha composites without resampling. Composite4096 is not claimed as single-generation native4K.','actualModelQualityConclusion':'All 68 raw generation records keep actual model and quality null, with evidence explaining non-disclosure.' if len(raw_inventory)==68 else 'Every raw generation checked for null actual model/quality and unknown reason.','formalAcceptanceGranted':False,'referenceAuditScope':A.summary['referenceAuditScope'],'auditType':'production records, coordinates, SHA, and exact pixel-operation provenance; no new visual acceptance'}
report={**summary,'selectedCores':A.selected,'allCoreNativeGenerations':A.all_generations,'additionalBuiltinRepairs':repairs,'rawGenerationInventory':raw_inventory,'goldProposalVerification':proposal_checks,'finalCandidates':finals,'verifiedBaseCandidates':A.candidate_results,'integrationScript':fileinfo(R/'integrate-gold.py')}
stamp=now.strftime('%Y%m%dT%H%M%SZ')
(Q/f'audit-final-{stamp}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'audit-current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'audit-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'summary-current.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'raw-generation-inventory.json').write_text(json.dumps(raw_inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))

