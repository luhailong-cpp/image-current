from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import hashlib,json,re,numpy as np

b=Path(__file__).resolve().parents[1];e=b/'extension-20261011'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
norm=lambda p:str(Path(p).resolve()).replace('\\','/').lower()
textnorm=lambda v:str(v).replace('\r\n','\n').strip()
issues=[];missing=[];cores=[];raw=[];candidates=[];replays=[];notes=[]
def issue(s):
 if s not in issues:issues.append(s)
def check(condition,message):
 if not condition:issue(message)
 return bool(condition)
def img(p):return Image.open(p).convert('RGB')
def exact(a,z):return a.size==z.size and ImageChops.difference(a,z).getbbox() is None
def hashcheck(p,expected,label):
 if not Path(p).is_file():
  missing.append(str(p));issue('Missing '+label+': '+str(p));return False
 return check(sha(p)==expected,'Hash mismatch '+label+': '+str(p))
def objecthash(o,label):
 return hashcheck(o['file'],o['sha256'],label)
def recordpaths(g,gp,kind):
 if kind=='core':
  d=gp.parent.parent/'records';stem=Path(g['file']).stem
  return [d/f'{stem}.prompt.txt',d/f'{stem}.request.json',d/f'{stem}.receipt.json']
 d=gp.parent
 prefix='repair.' if (d/'repair.request.json').exists() else ''
 return [Path(g.get('promptFile',d/(prefix+'prompt.txt'))),Path(g.get('requestFile',d/(prefix+'request.json'))),Path(g.get('receiptFile',d/(prefix+'receipt.json')))]
selected_paths=set()
for t in ['r05_c10','r05_c11']:
 for r in range(1,5):
  for c in range(1,5):
   p=b/t/'records'/f'p{r}{c}.selection.json'
   if not p.exists():missing.append(str(p));issue('Missing selected core '+str(p));continue
   s=read(p);g=read(s['generationRecord']);im=Image.open(s['file']);x=(int(t[5:7])-1)*4096+(c-1)*1024;y=16384+(r-1)*1024
   ok=s['sha256']==sha(s['file'])==g['sha256'] and im.size==(1254,1254) and g['globalCoreBox']==[x,y,x+1024,y+1024] and g['globalNativeBox']==[x-115,y-115,x+1139,y+1139] and g['coreCropNative']==[115,115,1139,1139] and g['actualModel'] is None and g['actualQuality'] is None
   check(ok,'Invalid selected native core '+str(p));selected_paths.add(norm(s['file']))
   cores.append({'tile':t,'core':f'p{r}{c}','file':s['file'],'sha256':sha(s['file']),'checkPassed':ok})

# Generation-record-driven inventory; corroborate with raw filename census so missing records cannot hide a raw.
inventory={}
for t in ['r05_c10','r05_c11']:
 for kind,root in [('core',b/t/'native'),('repair',b/t/'repairs')]:
  for gp in sorted(root.rglob('*.generation.json')):
   g=read(gp)
   if 'file' not in g:issue('Generation record has no file: '+str(gp));continue
   k=norm(g['file'])
   if k in inventory:
    inventory[k]['recordAliases'].append(str(gp));continue
   inventory[k]={'gp':gp,'g':g,'kind':kind,'tile':t,'recordAliases':[]}
 for p in sorted((b/t/'native').glob('p*-v*.png')):
  if norm(p) not in inventory:issue('Raw core has no generation record: '+str(p))
 for p in sorted((b/t/'repairs').rglob('*.png')):
  if p.name in ['native-result.png','repair-native.png'] and norm(p) not in inventory:
   issue('Raw repair has no generation record: '+str(p))
   inventory[norm(p)]={'gp':None,'g':{'file':str(p)},'kind':'repair','tile':t,'recordAliases':[]}
for k,item in sorted(inventory.items()):
 g=item['g'];gp=item['gp'];p=Path(g['file']);before=len(issues)
 if not p.exists():missing.append(str(p));issue('Generation file missing '+str(p));continue
 with Image.open(p) as im:dimensions=list(im.size);mode=im.mode
 check(dimensions==[1254,1254],'Wrong native dimensions '+str(p))
 entry={'file':str(p),'sha256':sha(p),'dimensions':dimensions,'mode':mode,'kind':item['kind'],'tile':item['tile'],'selectedCore':k in selected_paths,'generationRecord':str(gp) if gp else None,'recordAliases':item['recordAliases']}
 if gp:
  check(g.get('sha256')==sha(p),'Raw hash differs from generation record '+str(p))
  check(g.get('nativeDimensions',g.get('dimensions'))==dimensions,'Recorded dimensions differ '+str(p))
  check('actualModel' in g and g['actualModel'] is None and 'actualQuality' in g and g['actualQuality'] is None,'Actual model/quality must be explicit null '+str(gp))
  check(g.get('nativePixelsResized') is False,'Native resize metadata invalid '+str(gp))
  check(g.get('tool') in ['image_gen__imagegen','image_gen.imagegen'],'Tool is not builtin imagegen '+str(gp))
  check(g.get('route','builtin')=='builtin' and g.get('paidApiUsed',False) is False,'Unexpected paid/non-builtin route '+str(gp))
  for key in ['submittedModel','submittedQuality','requestedModel','requestedQuality']:
   check(g.get(key) is None,'Unexpected model/quality selector '+str(gp)+' '+key)
  prompt,request,receipt=recordpaths(g,gp,item['kind'])
  entry['promptFile']=str(prompt);entry['requestFile']=str(request);entry['receiptFile']=str(receipt)
  for q in [prompt,request,receipt]:
   if not q.exists():missing.append(str(q));issue('Missing provenance file '+str(q))
  if all(q.exists() for q in [prompt,request,receipt]):
   req=read(request);rec=read(receipt)
   check(textnorm(req.get('prompt'))==textnorm(prompt.read_text(encoding='utf-8-sig'))==textnorm(g.get('prompt')),'Prompt mismatch '+str(gp))
   check(bool(rec.get('output_hint')),'Receipt lacks actual output_hint '+str(receipt))
   check(rec.get('tool','image_gen__imagegen') in ['image_gen__imagegen','image_gen.imagegen'],'Receipt tool mismatch '+str(receipt))
   for obj,label in [(req,'request'),(rec,'receipt')]:
    for key in ['actualModel','actualQuality','submittedModel','submittedQuality','requestedModel','requestedQuality']:
     check(obj.get(key) is None,'Unsupported model/quality metadata '+label+' '+str(gp))
   entry['recordFileHashes']={q.name:sha(q) for q in [prompt,request,receipt]}
   for key,q in [('promptSha256',prompt),('requestSha256',request),('receiptSha256',receipt)]:
    if key in g:hashcheck(q,g[key],key)
   refs=g.get('references',[g['reference']] if 'reference' in g else [])
   requested_refs=req.get('referenced_image_paths',[])
   check([norm(x) for x in requested_refs]==[norm(x['file']) for x in refs],'Request/reference list mismatch '+str(gp))
   entry['references']=[]
   for ref in refs:
    rp=Path(ref['file']);matched=hashcheck(rp,ref['sha256'],'reference')
    dims=list(Image.open(rp).size) if rp.is_file() else None
    entry['references'].append({'file':str(rp),'sha256':ref['sha256'],'shaMatches':matched,'dimensions':dims})
   original=g.get('sourcePath',rec.get('originalFile'))
   if not original:
    match=re.search(r' as (.*?) by default',rec.get('output_hint',''),re.S)
    if match:original=match.group(1).strip()
   if original:
    op=Path(original);entry['originalToolOutput']=str(op)
    if op.exists():
     matched=check(sha(op)==sha(p),'Tool output copy differs '+str(p));entry['originalToolOutputShaMatches']=matched
    else:entry['originalToolOutputShaMatches']=None;notes.append('Tool cache output unavailable; stored raw and receipt verified: '+str(p))
   else:issue('Cannot resolve actual output source from receipt '+str(receipt))
  if 'sourceSha256' in g and 'sourcePath' in g and Path(g['sourcePath']).exists():hashcheck(g['sourcePath'],g['sourceSha256'],'original source')
  if 'targetDerivationFile' in g:hashcheck(g['targetDerivationFile'],g['targetDerivationSha256'],'target derivation')
 entry['checkPassed']=gp is not None and len(issues)==before;raw.append(entry)

# Independent replay of all selected original 1024 cores, no output image mutations.
for t in ['r05_c10','r05_c11']:
 cp=b/t/'candidate'/f'{t}-4096-candidate-v1.png'
 if not cp.exists():missing.append(str(cp));issue('Missing base candidate '+str(cp));continue
 composite=Image.new('RGB',(4096,4096))
 for r in range(1,5):
  for c in range(1,5):
   s=read(b/t/'records'/f'p{r}{c}.selection.json');composite.paste(img(s['file']).crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
 native_exact=exact(img(cp),composite);check(native_exact,'Base candidate differs from selected unscaled cores '+str(cp))
 candidates.append({'tile':t,'candidate':str(cp),'sha256':sha(cp),'dimensions':list(img(cp).size),'nativeCoreAssemblyPixelExact':native_exact})

# c10: exact original-size alpha from original candidate crop and generated repair.
t=b/'r05_c10';rd=t/'repairs/post-net-connection-v1';gp=rd/'repair-native.generation.json';g=read(gp)
base=t/'candidate/r05_c10-4096-candidate-v1.png';dest=t/'candidate/r05_c10-4096-candidate-v2.png';m=read(dest.with_suffix('.manifest.json'))
before=len(issues);hashcheck(base,m['baseCandidateSha256'],'c10 base');hashcheck(dest,m['sha256'],'c10 final')
box=g['targetTileBox'];replay=img(base);target=img(g['reference']['file'])
check(exact(target,replay.crop(box)),'c10 repair target not exact candidate crop')
objecthash(g['reference'],'c10 repair target');objecthash(g['mask'],'c10 alpha mask')
mask=Image.open(g['mask']['file']).convert('L');local=Image.composite(img(g['file']),target,mask)
check(exact(local,img(rd/'after-local-composite-native.png')),'c10 local composite replay differs')
replay.paste(local,(box[0],box[1]));matched=exact(replay,img(dest));check(matched,'c10 final repair replay differs')
app=read(rd/'repair-application.json');hashcheck(dest,app['candidateSha256'],'c10 application final')
replays.append({'tile':'r05_c10','candidate':str(dest),'sha256':sha(dest),'dimensions':list(img(dest).size),'repairSteps':1,'fullNativePixelReplayExact':matched,'checkPassed':len(issues)==before})

# c11: independently reconstruct p11 proposal, then replay manifest-ordered native masks.
t=b/'r05_c11';dest=t/'candidate/r05_c11-4096-candidate-v2.png'
if not dest.exists():missing.append(str(dest));issue('Missing c11 repaired final')
else:
 before=len(issues);m=read(dest.with_suffix('.manifest.json'));base=Path(m['base']);hashcheck(base,m['baseSha256'],'c11 base');hashcheck(dest,m['sha256'],'c11 final')
 if 'baseManifest' in m:hashcheck(m['baseManifest'],m['baseManifestSha256'],'c11 base manifest')
 replay=img(base);stepchecks=[]
 for step in m['steps']:
  st_before=len(issues);source=Path(step['source']);hashcheck(source,step['sourceSha256'],'c11 step source')
  if 'proposal' in step and 'mask' not in step:
   hashcheck(step['proposal'],step['proposalSha256'],'c11 step proposal');pr=read(step['proposal'])
   for key in ['outputNative','outputCore','baseNative','restoredGuide','compositeBase','repairRaw','mask']:objecthash(pr[key],'p11 '+key)
   reconstructed=img(pr['baseNative']['file']);guide=img(pr['restoredGuide']['file'])
   reconstructed.paste(guide.crop(pr['restoredGuide']['crop']),tuple(pr['restoredGuide']['pasteAt']))
   check(exact(reconstructed,img(pr['compositeBase']['file'])),'p11 composite base replay differs')
   reconstructed=Image.composite(img(pr['repairRaw']['file']),reconstructed,Image.open(pr['mask']['file']).convert('L'))
   check(exact(reconstructed,img(pr['outputNative']['file'])),'p11 native proposal replay differs')
   core=reconstructed.crop(pr['coreCrop']);check(exact(core,img(source)),'p11 proposal crop replay differs')
   replay.paste(core,tuple(pr['tileDestination']))
  else:
   if 'proposal' in step and 'proposalSha256' in step:hashcheck(step['proposal'],step['proposalSha256'],'c11 repair proposal')
   hashcheck(step['mask'],step['maskSha256'],'c11 step mask')
   if 'generationRecord' in step:hashcheck(step['generationRecord'],step['generationRecordSha256'],'c11 step generation')
   box=step['tileBox'];mask=Image.open(step['mask']).convert('L');source_image=img(source)
   check(source_image.size==mask.size==(box[2]-box[0],box[3]-box[1])==(1254,1254),'c11 step dimensions invalid '+str(source))
   local=Image.composite(source_image,replay.crop(box),mask);replay.paste(local,(box[0],box[1]))
  stepchecks.append({'name':step.get('name','p11-north-net-v2'),'source':str(source),'mask':step.get('mask'),'checkPassed':len(issues)==st_before})
 matched=exact(replay,img(dest));check(matched,'c11 final native repair replay differs')
 replays.append({'tile':'r05_c11','candidate':str(dest),'sha256':sha(dest),'dimensions':list(img(dest).size),'repairSteps':len(stepchecks),'steps':stepchecks,'fullNativePixelReplayExact':matched,'checkPassed':len(issues)==before})
 if 'sand_repair' in m.get('status',''):issue('c11 manifest is still marked pending sand repair; rerun after final composition before delivery.')

# Exact requested schema plus explicit inventory and replay scope.
check(len(cores)==32,'Selected core total is not32')
receipt_census=[]
for t in ['r05_c10','r05_c11']:
 receipt_census.extend((b/t/'records').glob('*.receipt.json'))
 receipt_census.extend((b/t/'repairs').rglob('*receipt.json'))
recorded_receipts={norm(x['receiptFile']) for x in raw if 'receiptFile' in x}
for p in receipt_census:
 if norm(p) not in recorded_receipts:issue('Receipt not represented by raw inventory '+str(p))
raw_core_count=sum(x['kind']=='core' for x in raw);repair_count=sum(x['kind']=='repair' for x in raw)
report={'auditedAt':datetime.now(timezone.utc).isoformat(),'status':'PASS' if not issues and not missing else 'ISSUES','selectedCoreCount':len(cores),'requiredCoreCount':32,'newRawCount':len(raw),'newCoreRawCount':raw_core_count,'newRepairRawCount':repair_count,'priorRawCount':71,'totalRawCount':71+len(raw),'selectedCores':cores,'rawGenerations':raw,'candidateChecks':candidates,'finalCandidateChecks':replays,'issues':issues,'missing':missing,'notes':notes,'actualModel':None,'actualQuality':None,'formalAcceptedCount':0,'scope':'All new selected32 cores and every raw core/repair version including rejected versions, real prompts/requests/receipts/reference hashes/native dimensions and explicit unknown model/quality. Independent full native pixel replay of both base and repaired final candidates. Prior71 raw outputs already independently passed and were not re-audited. Visual seam checks are separate.'}
report['receiptInventoryCount']=len(receipt_census)
report['receiptInventoryMatchedToRaw']=len(receipt_census)==len(recorded_receipts)==len(raw)
report['uniqueNewRawShaCount']=len({x['sha256'] for x in raw})
(e/'provenance-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','selectedCoreCount','newRawCount','newCoreRawCount','newRepairRawCount','totalRawCount','issues','notes']}))

