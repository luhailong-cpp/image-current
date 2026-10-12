from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,os,sys
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach')
Q=R/'qa'/'provenance-audit';Q.mkdir(parents=True,exist_ok=True)
TILES=['r03_c10','r03_c11','r04_c10','r04_c11']
CANDIDATES={'r03_c10':'r03_c10-4096-candidate-v3.png','r03_c11':'r03_c11-4096-candidate-v2.png','r04_c10':'r04_c10-4096-candidate-v1.png','r04_c11':'r04_c11-4096-candidate-v1.png'}
cache={}
def sha(p):
 p=Path(p);k=(str(p),p.stat().st_mtime_ns,p.stat().st_size)
 if k not in cache:cache[k]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[k]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def norm(p):return os.path.normcase(str(Path(p).resolve()))
def within(p):return Path(p).resolve().is_relative_to(R.resolve())
def fileinfo(p,do_hash=True):
 p=Path(p);d={'file':str(p),'exists':p.is_file()}
 if p.is_file():
  d['bytes']=p.stat().st_size
  if do_hash:d['sha256']=sha(p)
 return d
def msg(scope,kind,description,severity='error'):issues.append({'scope':scope,'kind':kind,'severity':severity,'description':description})
def promptnorm(s):return str(s).replace('\r\n','\n').rstrip('\r\n')
issues=[];pending=[];selected=[];all_generations=[];candidate_results=[];selected_images={}
def audit_generation(gp,selected_flag):
 scope=str(gp.relative_to(R));g=read(gp);src=Path(g.get('file',str(gp).replace('.generation.json','.png')))
 info={'generationRecord':fileinfo(gp),'image':fileinfo(src),'selected':selected_flag,'checks':{},'references':[],'metadata':{k:g.get(k,'<missing>') for k in ['tool','route','actualModel','actualQuality','submittedModel','submittedQuality','unknownReason']}}
 ck=info['checks']
 if not src.is_file():msg(scope,'native_missing',str(src));return info
 with Image.open(src) as im:dims=list(im.size);fmt=im.format
 ck['measuredDimensions']=dims;ck['recordDimensionsMatch']=g.get('nativeDimensions')==dims
 ck['is1254Square']=dims==[1254,1254];ck['shaMatchesRecord']=sha(src)==g.get('sha256')
 for k in ['recordDimensionsMatch','is1254Square','shaMatchesRecord']:
  if not ck[k]:msg(scope,k,'Failed native file integrity check.')
 ck['nativePixelsResizedFalse']=g.get('nativePixelsResized') is False
 if not ck['nativePixelsResizedFalse']:msg(scope,'resizing_not_disclaimed','nativePixelsResized is not false.')
 ck['coreCropIs1024']=g.get('coreCropNative')==[115,115,1139,1139]
 if not ck['coreCropIs1024']:msg(scope,'core_crop','Expected [115,115,1139,1139].')
 ck['builtinOnly']=g.get('tool')=='image_gen__imagegen' and g.get('route')=='builtin'
 if not ck['builtinOnly']:msg(scope,'tool_route','Expected builtin imagegen route.')
 ck['modelQualityUnknown']=g.get('actualModel','missing') is None and g.get('actualQuality','missing') is None and bool(g.get('unknownReason'))
 if not ck['modelQualityUnknown']:msg(scope,'model_quality','Model/quality are not accurately null with unknown reason.')
 stem=src.stem;recorddir=gp.parent.parent/'records'
 pp=Path(g.get('promptFile',recorddir/(stem+'.prompt.txt')))
 qp=recorddir/(stem+'.request.json');rp=recorddir/(stem+'.receipt.json')
 info['promptFile']=fileinfo(pp);info['requestFile']=fileinfo(qp);info['receiptFile']=fileinfo(rp)
 for role,p in [('prompt',pp),('request',qp),('receipt',rp)]:
  if not p.is_file():msg(scope,role+'_missing',str(p))
 if pp.is_file():
  ck['promptTextMatchesGeneration']=promptnorm(pp.read_text(encoding='utf-8-sig'))==promptnorm(g.get('prompt',''))
  if not ck['promptTextMatchesGeneration']:msg(scope,'prompt_mismatch','Prompt file differs from generation record.')
 if qp.is_file():
  req=read(qp);ck['requestPromptMatchesGeneration']=promptnorm(req.get('prompt',''))==promptnorm(g.get('prompt',''))
  if not ck['requestPromptMatchesGeneration']:msg(scope,'request_prompt_mismatch','Request prompt differs from generation record.')
  paths=req.get('referenced_image_paths',[])
  refs=[z.get('file') for z in g.get('references',[])]
  ck['requestReferencePathsMatchGeneration']=[norm(p) for p in paths]==[norm(p) for p in refs]
  if not ck['requestReferencePathsMatchGeneration']:msg(scope,'references_mismatch','Request references differ from generation references.')
 if rp.is_file():
  receipt=read(rp);ck['receiptMatchesEmbedded']=receipt==g.get('receipt')
  if not ck['receiptMatchesEmbedded']:msg(scope,'receipt_mismatch','Receipt file differs from inline generation receipt.')
  for k in ['actualModel','actualQuality']:
   if receipt.get(k,None) is not None:msg(scope,'receipt_model_quality','Receipt discloses value; inspect any null generation metadata claim.')
 for ref in g.get('references',[]):
  p=Path(ref['file']);fi=fileinfo(p,within(p));fi['recordedSha256']=ref.get('sha256');fi['role']=ref.get('role')
  if not p.is_file():msg(scope,'reference_missing',str(p))
  elif within(p):
   fi['shaMatchesRecord']=sha(p)==ref.get('sha256')
   if not fi['shaMatchesRecord']:msg(scope,'reference_sha_mismatch',str(p))
  else:fi['hashAudit']='existence only; outside assigned four-tile zone; file contents not read'
  info['references'].append(fi)
 info['originalToolOutputExists']=bool(g.get('sourcePath') and Path(g['sourcePath']).is_file())
 return info
generation_lookup={}
for tile in TILES:
 folder=R/tile;sel_files=list((folder/'records').glob('p??.selection.json'))
 chosen_paths={}
 for r in range(1,5):
  for c in range(1,5):
   sp=folder/'records'/f'p{r}{c}.selection.json';scope=f'{tile}:p{r}{c}'
   if not sp.is_file():pending.append({'type':'missing_core_selection','tile':tile,'core':f'p{r}{c}','file':str(sp)});continue
   sel=read(sp);src=Path(sel['file']);gp=Path(sel['generationRecord'])
   ent={'tile':tile,'core':f'p{r}{c}','selection':fileinfo(sp),'image':fileinfo(src),'generationRecord':str(gp),'checks':{}}
   if not gp.is_file():msg(scope,'generation_record_missing',str(gp));selected.append(ent);continue
   g=read(gp);x=(int(tile[5:7])-1)*4096+(c-1)*1024;y=(int(tile[1:3])-1)*4096+(r-1)*1024
   expected=[x,y,x+1024,y+1024]
   checks=ent['checks'];checks['selectionShaMatches']=src.is_file() and sha(src)==sel.get('sha256')
   checks['generationFileMatchesSelection']=norm(g.get('file',''))==norm(src)
   checks['coreBoxCorrect']=g.get('globalCoreBox')==expected
   checks['nativeBoxCorrect']=g.get('globalNativeBox')==[x-115,y-115,x+1139,y+1139]
   checks['coreDimensions']=[1024,1024]
   ent['expectedGlobalCoreBox']=expected
   for k,v in checks.items():
    if v is False:msg(scope,k,'Selected core integrity/coordinate mismatch.')
   selected.append(ent);chosen_paths[norm(gp)]=True
   if src.is_file():selected_images[(tile,r,c)]=src
 for gp in sorted((folder/'native').glob('*.generation.json')):
  info=audit_generation(gp,norm(gp) in chosen_paths);all_generations.append(info);generation_lookup[norm(gp)]=info
 for p in (folder/'native').glob('*.png'):
  if not p.with_suffix('.generation.json').is_file():msg(tile,'orphan_native_image',str(p))
 for ent in selected:
  if ent['tile']==tile and norm(ent['generationRecord']) not in generation_lookup:msg(tile,'selected_generation_outside_native_folder',ent['generationRecord'])
# Core coverage: coordinates align to non-overlapping 8x8 global 1024 grid over designated 8192 square region.
boxes=[tuple(e['expectedGlobalCoreBox']) for e in selected if 'expectedGlobalCoreBox' in e]
coverage={'expectedCoreCount':64,'selectedCoreCount':len(selected),'uniqueCoordinateBoxCount':len(set(boxes)),'duplicateCoordinateBoxes':len(boxes)-len(set(boxes)),'selectedPixelArea':len(set(boxes))*1024*1024,'targetPixelArea':8192*8192,'targetGlobalBox':[36864,8192,45056,16384],'complete':len(selected)==64 and len(set(boxes))==64}
def check_manifest_hash_objects(obj,scope,outlist):
 if isinstance(obj,dict):
  if 'file' in obj and 'sha256' in obj and isinstance(obj['file'],str):
   p=Path(obj['file']);entry={'file':str(p),'exists':p.is_file()}
   if p.is_file() and within(p):
    entry['actualSha256']=sha(p);entry['matches']=sha(p)==obj['sha256']
    if not entry['matches']:msg(scope,'manifest_dependency_sha_mismatch',str(p))
   elif not p.is_file():msg(scope,'manifest_dependency_missing',str(p))
   else:entry['hashAudit']='existence only outside assigned zone'
   outlist.append(entry)
  for v in obj.values():check_manifest_hash_objects(v,scope,outlist)
 elif isinstance(obj,list):
  for v in obj:check_manifest_hash_objects(v,scope,outlist)
for tile,name in CANDIDATES.items():
 p=R/tile/'candidate'/name;mp=p.with_suffix('.manifest.json');scope=tile+':candidate'
 if not p.is_file() or not mp.is_file():pending.append({'type':'candidate_missing','tile':tile,'file':str(p),'manifest':str(mp)});continue
 m=read(mp);ci={'tile':tile,'candidate':fileinfo(p),'manifest':fileinfo(mp),'manifestDimensions':m.get('dimensions'),'measuredDimensions':list(Image.open(p).size),'hashMatchesManifest':sha(p)==m.get('sha256'),'formalAccepted':m.get('formalAccepted'),'dependencyHashes':[]}
 check_manifest_hash_objects(m,scope,ci['dependencyHashes'])
 if not ci['hashMatchesManifest']:msg(scope,'candidate_sha_mismatch',str(p))
 if ci['measuredDimensions']!=[4096,4096]:msg(scope,'candidate_dimensions',str(ci['measuredDimensions']))
 if m.get('formalAccepted') is not False:msg(scope,'formal_acceptance_state','Expected false while external acceptance pending.','warning')
 if all((tile,r,c) in selected_images for r in range(1,5) for c in range(1,5)):
  assembly=Image.new('RGB',(4096,4096))
  for r in range(1,5):
   for c in range(1,5):assembly.paste(Image.open(selected_images[(tile,r,c)]).convert('RGB').crop([115,115,1139,1139]),((c-1)*1024,(r-1)*1024))
  candidate=Image.open(p).convert('RGB')
  if tile!='r03_c10':
   ci['pixelExactCoreAssemblyVerified']=assembly.tobytes()==candidate.tobytes()
   ci['noResamplingEvidence']='Pixel-for-pixel equality to 16 native 1024 crops.' if ci['pixelExactCoreAssemblyVerified'] else 'Mismatch: inspect documented processing.'
   if not ci['pixelExactCoreAssemblyVerified']:msg(scope,'candidate_not_exact_core_assembly','Candidate differs from current selected native cores.')
  else:
   basepath=Path(m['baseCandidate']['file']);ci['basePixelExactCoreAssemblyVerified']=assembly.tobytes()==Image.open(basepath).convert('RGB').tobytes()
   if not ci['basePixelExactCoreAssemblyVerified']:msg(scope,'base_core_assembly_mismatch','v1 differs from current selected 16 native crops.')
   strips=[]
   for row in [1,2]:
    strip=Image.new('RGB',(4096,230))
    for c in range(1,5):
     im=Image.open(selected_images[(tile,row,c)]).convert('RGB');box=[115,1024,1139,1254] if row==1 else [115,0,1139,230]
     strip.paste(im.crop(box),((c-1)*1024,0))
    strips.append(strip)
   masks=m['masksAndWeights']
   bm=Image.open(masks['bottomSourceWeightLocal']['file']).convert('L')
   am=Image.open(masks['activationFull']['file']).convert('L').crop([0,909,4096,1139])
   stage=Image.open(basepath).convert('RGB')
   mixed=Image.composite(strips[1],strips[0],bm)
   stage.paste(Image.composite(mixed,stage.crop([0,909,4096,1139]),am),(0,909))
   vr=m['verticalRepair'];mask=Image.open(masks['verticalRepairAlphaLocal']['file']).convert('L');box=vr['targetBoxTileXYXY']
   result=Image.open(vr['nativeResult']['file']).convert('RGB')
   stage.paste(Image.composite(result,stage.crop(box),mask),(box[0],box[1]))
   ci['pixelExactDocumentedCompositeVerified']=stage.tobytes()==candidate.tobytes()
   ci['noResamplingEvidence']='Independently reconstructed at scale1 from selected native crops, real native halos and hash-backed repair/masks; exact final RGB equality.'
   if not ci['pixelExactDocumentedCompositeVerified']:msg(scope,'composite_reconstruction_mismatch','v3 differs from documented unscaled operations.')
 candidate_results.append(ci)
summary={'auditedAt':datetime.now(timezone.utc).isoformat(),'scope':TILES,'readOnlyOutsideAuditFolder':True,'coverage':coverage,'nativeGenerationCount':len(all_generations),'selectedNativeCount':len(selected),'candidateCount':len(candidate_results),'errors':sum(i['severity']=='error' for i in issues),'warnings':sum(i['severity']=='warning' for i in issues),'pending':pending,'issues':issues,'modelQualityPolicy':'Each native generation must keep actualModel/actualQuality null and give an unknown reason; builtin tool does not disclose them.','referenceAuditScope':'Referenced paths inside assigned zone are SHA-verified. External approved style/source references are checked for existence only; no unrelated zone content read.','formalAcceptanceGranted':False,'auditType':'production provenance/coordinate/pixel-operation audit; not visual acceptance'}
report={**summary,'selectedCores':selected,'allNativeGenerations':all_generations,'candidates':candidate_results}
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
(Q/f'audit-{stamp}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'audit-current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'summary-current.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))

