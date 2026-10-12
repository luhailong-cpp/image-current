from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,importlib.util,contextlib,io,sys
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prior_final',HERE/'audit_final.py');M=importlib.util.module_from_spec(s)
with contextlib.redirect_stdout(io.StringIO()):s.loader.exec_module(M)
A=M.A;R=M.R;Q=M.Q;sha=M.sha;read=M.read;fi=M.fileinfo;issues=M.issues
def check(value,scope,kind):
 if not value:A.msg(scope,kind,'Native repair or candidate check failed.')
 return value
new=[]
for name in ['net-rope-v1','net-joint-v2']:
 d=R/'r04_c11/repairs'/name;gp=d/'native-result.generation.json';g=read(gp);p=Path(g['file']);scope=name
 pp=Path(g['promptFile']);qp=Path(g['requestFile']);rp=Path(g['receiptFile']);req=read(qp);rc=read(rp)
 dims=list(Image.open(p).size)
 e={'kind':name,'image':fi(p),'nativeDimensions':dims,'record':fi(gp),'prompt':fi(pp),'request':fi(qp),'receipt':fi(rp),'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'unknownReason':g.get('unknownReason'),'contributesFinalPixels':g.get('contributesFinalPixels'),'status':g.get('status'),'checks':{},'references':[]}
 c=e['checks'];c['dimensions']=check(dims==g.get('nativeDimensions')==[1254,1254],scope,'dimensions');c['sha']=check(sha(p)==g['sha256'],scope,'sha');c['noResizing']=check(g.get('nativePixelsResized') is False,scope,'resizing')
 c['builtinRoute']=check(g.get('tool')=='image_gen__imagegen' and g.get('route')=='builtin',scope,'route')
 c['unknownMetadata']=check(g.get('actualModel','missing') is None and g.get('actualQuality','missing') is None and bool(g.get('unknownReason')),scope,'metadata')
 c['promptExact']=check(A.promptnorm(pp.read_text(encoding='utf-8-sig'))==A.promptnorm(req['prompt'])==A.promptnorm(g['prompt']),scope,'prompt')
 c['receiptExact']=check(rc==g['receipt'],scope,'receipt')
 c['referencePaths']=check([A.norm(x) for x in req['referenced_image_paths']]==[A.norm(x['file']) for x in g['references']],scope,'reference_paths')
 for ref in g['references']:
  f=fi(ref['file']);f['shaMatches']=check(f.get('sha256')==ref['sha256'],scope,'reference_sha');e['references'].append(f)
 if name=='net-rope-v1':c['explicitRejection']=check(g.get('contributesFinalPixels') is False and bool(g.get('rejectionReason')),scope,'rejection_record')
 new.append(e)
tile='r04_c11';p=R/tile/'candidate/r04_c11-4096-candidate-v2.png';mp=p.with_suffix('.manifest.json');m=read(mp)
base=Image.open(m['baseCandidate']['file']).convert('RGB');native=Image.open(m['nativeRepair']['file']).convert('RGB');mask=Image.open(m['compositing']['mask']['file']).convert('L');box=m['compositing']['cropBoxTileXYXY'];target=Image.open(m['target']['file']).convert('RGB')
replay=base.copy();replay.paste(Image.composite(native,target,mask),box[:2]);actual=Image.open(p).convert('RGB')
c={'tile':tile,'candidate':fi(p),'manifest':fi(mp),'compositeDimensions':list(actual.size),'nativeDimensionsOfContributingGeneration':list(native.size),'formalAccepted':m.get('formalAccepted'),'checks':{},'dependencyHashes':[]}
ck=c['checks'];ck['candidateSha']=check(sha(p)==m['sha256'],tile,'candidate_sha');ck['dimensions4096']=check(list(actual.size)==m['dimensions']==[4096,4096],tile,'dimensions4096')
ck['baseSha']=check(sha(m['baseCandidate']['file'])==m['baseCandidate']['sha256'],tile,'base_sha')
ck['targetExactBaseCrop']=check(base.crop(box).tobytes()==target.tobytes(),tile,'target_crop')
ck['maskDimension']=check(mask.size==native.size==(1254,1254),tile,'mask_dimensions')
ck['pixelExactRecordedComposite']=check(replay.tobytes()==actual.tobytes(),tile,'pixel_replay')
ck['noResizing']=check(m['compositing']['nativePixelsResized'] is False,tile,'resizing')
ck['rejectedVersionContributesNoPixels']=check(m['rejectedAlternative']['contributesFinalPixels'] is False and A.norm(m['nativeRepair']['file'])!=A.norm(m['rejectedAlternative']['file']),tile,'rejected_pixel_source')
A.check_manifest_hash_objects(m,tile,c['dependencyHashes'])
c['noResamplingEvidence']='Independent RGB-exact replay of builtin native result + 1254 alpha mask over exact target crop; verified v1 core assembly is the base. Rejected net-rope-v1 is not a compositing source.'
c['visualAcceptance']='Upper rope passes local continuity review; lower vertical mesh defect remains for subsequent builtin repair. This provenance audit grants no formal visual acceptance.'
finals=[c if x['tile']==tile else x for x in M.finals]
inventory=M.raw_inventory.copy()
for n in new:
 inventory.append({'file':n['image']['file'],'sha256':n['image']['sha256'],'nativeDimensions':n['nativeDimensions'],'actualModel':n['actualModel'],'actualQuality':n['actualQuality'],'unknownReason':n['unknownReason'],'kind':n['kind'],'selected':n['contributesFinalPixels'],'contributesFinalPixels':n['contributesFinalPixels'],'record':n['record']['file'],'prompt':n['prompt']['file'],'request':n['request']['file'],'receipt':n['receipt']['file']})
counts=dict(M.raw_counts);counts.update({'additionalBuiltinRepairCount':4,'additionalBuiltinRepairsUsed':3,'additionalBuiltinRepairsRejected':1,'rawGeneratedImageCount':len(inventory),'uniqueRawGeneratedFiles':len({A.norm(x['file']) for x in inventory}),'uniqueRawImageSha256Count':len({x['sha256'] for x in inventory}),'allRawNativeDimensions1254':all(x['nativeDimensions']==[1254,1254] for x in inventory),'allActualModelQualityUnknown':all(x['actualModel'] is None and x['actualQuality'] is None and bool(x['unknownReason']) for x in inventory)})
now=datetime.now(timezone.utc)
summary={**M.summary,'auditedAt':now.isoformat(),'status':'PASS_PROVENANCE' if not issues else 'FAIL','rawCounts':counts,'errors':sum(x['severity']=='error' for x in issues),'warnings':sum(x['severity']=='warning' for x in issues),'issues':issues,'finalCandidatePicks':[{k:v for k,v in x.items() if k in ['tile','candidate','compositeDimensions']} for x in finals],'actualModelQualityConclusion':f'All {len(inventory)} raw native generation records have actual model and quality null, with unknown explanations.','visualStatus':'Lower net defect at r04_c11 x1139 remains; upper rope candidate-v2 is an intermediate composite. Formal acceptance false.','formalAcceptanceGranted':False}
report={**M.report,**summary,'rawGenerationInventory':inventory,'additionalBuiltinRepairs':M.repairs+new,'finalCandidates':finals}
for name in ['audit-current.json','audit-final.json','audit-70-native.json']:(Q/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'summary-current.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'raw-generation-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':summary['status'],'coverage':A.coverage,'rawCounts':counts,'errors':summary['errors'],'warnings':summary['warnings'],'candidate':str(p),'sha256':sha(p),'report':str(Q/'audit-70-native.json'),'visualStatus':summary['visualStatus']},ensure_ascii=False,indent=2))

