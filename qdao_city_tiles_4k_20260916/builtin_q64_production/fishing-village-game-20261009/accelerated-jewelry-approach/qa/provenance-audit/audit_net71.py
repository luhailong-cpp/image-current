from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,io,contextlib,importlib.util
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('audit70',HERE/'audit_net70.py');M=importlib.util.module_from_spec(s)
with contextlib.redirect_stdout(io.StringIO()):s.loader.exec_module(M)
A=M.A;R=M.R;Q=M.Q;sha=M.sha;read=M.read;fi=M.fi;issues=M.issues
def ck(value,scope,kind):
 if not value:A.msg(scope,kind,'Final lower-net provenance verification failed.')
 return value
D=R/'r04_c11/repairs/net-lower-v1';gp=D/'native-result.generation.json';g=read(gp);p=Path(g['file']);scope='net-lower-v1'
pp=Path(g['promptFile']);qp=Path(g['requestFile']);rp=Path(g['receiptFile']);req=read(qp);rc=read(rp);native=Image.open(p).convert('RGB')
e={'kind':scope,'image':fi(p),'nativeDimensions':list(native.size),'record':fi(gp),'prompt':fi(pp),'request':fi(qp),'receipt':fi(rp),'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'unknownReason':g.get('unknownReason'),'contributesFinalPixels':g.get('contributesFinalPixels'),'references':[],'checks':{}}
c=e['checks']
c['nativeDimensions']=ck(list(native.size)==g['nativeDimensions']==[1254,1254],scope,'dimensions')
c['sha']=ck(sha(p)==g['sha256'],scope,'sha')
c['unknownMetadata']=ck(g.get('actualModel','missing') is None and g.get('actualQuality','missing') is None and bool(g.get('unknownReason')),scope,'metadata')
c['nativeNotResized']=ck(g.get('nativePixelsResized') is False,scope,'resizing')
c['builtinRoute']=ck(g.get('route')=='builtin' and g.get('tool')=='image_gen__imagegen',scope,'route')
c['promptExact']=ck(A.promptnorm(pp.read_text(encoding='utf-8-sig'))==A.promptnorm(req['prompt'])==A.promptnorm(g['prompt']),scope,'prompt')
c['receiptExact']=ck(rc==g['receipt'],scope,'receipt')
c['referencesExact']=ck([A.norm(x) for x in req['referenced_image_paths']]==[A.norm(x['file']) for x in g['references']],scope,'references')
for ref in g['references']:
 f=fi(ref['file']);f['shaMatches']=ck(f.get('sha256')==ref['sha256'],scope,'reference_sha');e['references'].append(f)
cand=R/'r04_c11/candidate/r04_c11-4096-candidate-v3.png';mp=cand.with_suffix('.manifest.json');m=read(mp);plan=m['compositing']
base=Image.open(m['baseCandidate']['file']).convert('RGB');target=Image.open(m['target']['file']).convert('RGB');mask=Image.open(plan['mask']['file']).convert('L');actual=Image.open(cand).convert('RGB')
deriv=read(m['targetDerivation']['file']);derived=Image.new('RGB',(1254,1254));derived.paste(base.crop((512,2957,1766,4096)),(0,0))
for h in deriv['haloPlacements']:derived.paste(Image.open(h['source']).convert('RGB').crop(h['crop']),h['paste'])
replay=base.copy();local=Image.composite(native,target,mask);replay.paste(local.crop(plan['nativeCropContributingToTile']),tuple(plan['pasteXY']))
candidate={'tile':'r04_c11','candidate':fi(cand),'manifest':fi(mp),'compositeDimensions':list(actual.size),'nativeDimensionsOfContributingGeneration':list(native.size),'formalAccepted':m.get('formalAccepted'),'checks':{},'dependencyHashes':[]}
cc=candidate['checks']
cc['shaMatches']=ck(sha(cand)==m['sha256'],'r04_c11v3','sha')
cc['dimensions4096']=ck(list(actual.size)==m['dimensions']==[4096,4096],'r04_c11v3','dimensions')
cc['baseShaMatches']=ck(sha(m['baseCandidate']['file'])==m['baseCandidate']['sha256'],'r04_c11v3','base_sha')
cc['nativeTargetExactCorePlusHalo']=ck(derived.tobytes()==target.tobytes(),'r04_c11v3','target_derivation')
cc['pixelExactRecordedComposite']=ck(replay.tobytes()==actual.tobytes(),'r04_c11v3','pixel_replay')
cc['noResamplingDeclared']=ck(m.get('nativePixelsResized') is False and plan.get('nativePixelsResized') is False,'r04_c11v3','resizing')
cc['referenceHaloNotWritten']=ck(plan['nativeCropContributingToTile']==[0,0,1254,1139] and plan['pasteXY']==[512,2957],'r04_c11v3','halo_crop')
cc['externalBottomChangeRecorded']=ck(m.get('externalBottomBoundaryChanged') is True and m.get('externalSeamsChecked') is False and m.get('formalAccepted') is False,'r04_c11v3','boundary_status')
cc['preservedUpperAndPostPixels']=ck(base.crop((0,0,4096,3287)).tobytes()==actual.crop((0,0,4096,3287)).tobytes() and base.crop((1594,0,4096,4096)).tobytes()==actual.crop((1594,0,4096,4096)).tobytes(),'r04_c11v3','preserved_regions')
A.check_manifest_hash_objects(m,'r04_c11v3',candidate['dependencyHashes'])
A.check_manifest_hash_objects(deriv,'r04_c11v3:derivation',candidate['dependencyHashes'])
candidate['noResamplingEvidence']='Independent pixel-exact replay: recorded source-plus-halo native target, 1254 native repair, exact alpha mask, crop [0,0,1254,1139] and unscaled paste. Extra 115 native halo rows excluded from final tile.'
candidate['visualAcceptance']='Local upper/lower net repair QA passed. Changed bottom tile edge remains externally unchecked; formalAccepted false.'
inventory=M.inventory.copy();inventory.append({'file':e['image']['file'],'sha256':e['image']['sha256'],'nativeDimensions':e['nativeDimensions'],'actualModel':e['actualModel'],'actualQuality':e['actualQuality'],'unknownReason':e['unknownReason'],'kind':scope,'selected':True,'contributesFinalPixels':True,'record':e['record']['file'],'prompt':e['prompt']['file'],'request':e['request']['file'],'receipt':e['receipt']['file']})
finals=[candidate if x['tile']=='r04_c11' else x for x in M.finals]
counts=dict(M.counts);counts.update({'additionalBuiltinRepairCount':5,'additionalBuiltinRepairsUsed':4,'additionalBuiltinRepairsRejected':1,'rawGeneratedImageCount':len(inventory),'uniqueRawGeneratedFiles':len({A.norm(x['file']) for x in inventory}),'uniqueRawImageSha256Count':len({x['sha256'] for x in inventory}),'allRawNativeDimensions1254':all(x['nativeDimensions']==[1254,1254] for x in inventory),'allActualModelQualityUnknown':all(x['actualModel'] is None and x['actualQuality'] is None and bool(x['unknownReason']) for x in inventory)})
now=datetime.now(timezone.utc)
summary={**M.summary,'auditedAt':now.isoformat(),'status':'PASS_PROVENANCE' if not issues else 'FAIL','rawCounts':counts,'finalCandidatePicks':[{k:v for k,v in x.items() if k in ['tile','candidate','compositeDimensions']} for x in finals],'errors':sum(i['severity']=='error' for i in issues),'warnings':sum(i['severity']=='warning' for i in issues),'issues':issues,'actualModelQualityConclusion':f'All {len(inventory)} raw native generations have measured1254x1254, actual model and quality null, with unknown explanations.','visualStatus':'Upper/lower net local QA passed; updated bottom edge x958..1591 requires external neighbor review. Formal acceptance false.','formalAcceptanceGranted':False}
report={**M.report,**summary,'rawGenerationInventory':inventory,'additionalBuiltinRepairs':M.report['additionalBuiltinRepairs']+[e],'finalCandidates':finals,'latestLocalQA':fi(R/'r04_c11/qa/net-lower-v1/findings.json')}
for name in ['audit-current.json','audit-final.json','audit-71-native.json']:(Q/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'summary-current.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'raw-generation-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':summary['status'],'rawCounts':counts,'coverage':A.coverage,'errors':summary['errors'],'warnings':summary['warnings'],'candidate':str(cand),'sha256':sha(cand),'report':str(Q/'audit-71-native.json'),'visualStatus':summary['visualStatus']},ensure_ascii=False,indent=2))


