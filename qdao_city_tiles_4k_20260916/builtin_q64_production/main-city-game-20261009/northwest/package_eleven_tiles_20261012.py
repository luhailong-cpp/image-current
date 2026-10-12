from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw,ImageFont
Z=Path(__file__).resolve().parent
OLD=Z/'verified-nine-tiles-20261012-v2/9195bae2e10f72ba'
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f):
 with Path(f).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def ref(f):return {'file':str(Path(f).resolve()),'sha256':sha(f)}
def now():return datetime.now(timezone.utc).isoformat()
def write(f,v):
 assert not f.exists();f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert read(f)==v
inputs={};extras={};walked=set()
def check(r):
 f=Path(r['file']).resolve();assert sha(f)==r['sha256'],f;inputs[str(f)]=r['sha256'];return f
def keep(r,entry=None,recurse=False):
 if isinstance(r,(str,Path)):r=ref(r)
 f=check(r)
 if not f.is_relative_to(Z):return f
 if entry is None:entry='evidence/'+f.relative_to(Z).as_posix()
 assert entry not in extras or extras[entry]['sha256']==r['sha256'];extras[entry]={'originalFile':str(f),'zipEntry':entry,'sha256':r['sha256']}
 if recurse and str(f) not in walked and f.suffix.lower()=='.json':
  walked.add(str(f));walk(read(f))
 return f
def walk(v):
 if isinstance(v,dict):
  if isinstance(v.get('file'),str) and isinstance(v.get('sha256'),str):
   f=Path(v['file'])
   if f.is_relative_to(Z) and not any(part.startswith('verified-') for part in f.parts) and f.suffix!='.zip':
    # Submitted generation references preserve historical hashes; original pixels/evidence are validated separately.
    recurse=f.suffix=='.json' and 'receipts' not in f.parts and not f.name.endswith('generation.json')
    keep(v,recurse=recurse)
  for k,x in v.items():
   if k not in ('references','recordedReferences','configSnapshot','configurationSnapshot','guideDerivation','sourceHostFile'):walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
op=read(OLD/'package.json');oldzip=check(op);assert op['sha256']=='7af0f0f710740dbb19be01f861a8ab5e71660a9033f707e2404e402aa072c9b5';oldsummary=read(check(op['summary']));contents=read(check(op['packageContents']));oldfiles=list(contents['files'])+[{'originalFile':op['packageContents']['file'],'zipEntry':'package-contents.json','sha256':op['packageContents']['sha256']}]
assert len(oldfiles)==op['verifiedZipEntries']==1578
with zipfile.ZipFile(oldzip) as archive:
 assert archive.testzip() is None
 for item in oldfiles:
  check({'file':item['originalFile'],'sha256':item['sha256']})
  with archive.open(item['zipEntry']) as h:assert hashlib.file_digest(h,'sha256').hexdigest()==item['sha256']
tiles=[dict(t) for t in oldsummary['tiles']];newdeliveries=[];newsources=[]
for tile in ('r07_c05','r06_c07'):
 f=Z/tile/'delivery-summary-20261012.json';d=read(keep(f,recurse=True));assert d['internalQAPassed'] and not d['unresolvedInternalBlockers'] and d['verifiedPixels']==16777216 and not d['formalAccepted'];newdeliveries.append(ref(f));check(d['candidate']);m=read(check(d['assemblyManifest']))
 check(d['acceptance']);check(d['qaEvidence']);sources=d['nativeSources']
 assert len(sources)==(21 if tile=='r07_c05' else 16)
 for i,s in enumerate(sources):
  native_name=s['id']+'.png' if Path(s['file']).name=='native.png' else Path(s['file']).name
  native_entry='native/'+tile+'/'+native_name
  source=keep(s,native_entry);gref=s.get('generationRecord')
  if isinstance(gref,str):gref=ref(gref)
  if not gref:gref=ref(source.with_suffix('.png.generation.json'))
  g=read(keep(gref));evidence={}
  if i<16:
   selection=read(Z/tile/'selection.json') if (Z/tile/'selection.json').exists() else {};selected=Path(selection.get(s['id'],'native/'+s['id']+'.png'))
   if not selected.is_absolute():selected=Z/tile/selected
   assert sha(selected)==s['sha256']
  host=g.get('sourceHostFile',g.get('hostOutputPath',g.get('evidence',{}).get('hostOutputPath')));assert host and sha(host)==s['sha256']
  for label in ('prompt','request','receipt'):
   e=s.get('evidence',{}).get(label)
   if not e:
    ev=g.get('evidence',{});path=ev.get(label)
    if path:e={'file':path,'sha256':ev.get(label+'Sha256',sha(path))}
   if not e:
    if label=='request':e=g.get('request')
    elif label=='receipt':e=g.get('toolReceipt')
    elif label=='prompt':
     path=source.parent/'prompt.txt'
     if path.exists():e=ref(path)
   if e:
    if isinstance(e,str):e=ref(e)
    keep(e);evidence[label]=e
  with Image.open(source) as im:assert im.format=='PNG' and im.size==(1254,1254)
  newsources.append({'tile':tile,'id':s['id'],'file':str(source),'sha256':s['sha256'],'generationRecord':gref,'evidence':evidence,'hostOutputHashMatches':True,'nativePixels':[1254,1254],'currentFixedSelectionMatches':True if i<16 else None,'kind':'fixed_grid' if i<16 else 'supplemental_same_world_native_source','zipEntry':native_entry})
 row,col=int(tile[1:3]),int(tile[5:7]);tiles.append({'tile':tile,**d['candidate'],'tileWorldBox':[(col-1)*4096,(row-1)*4096,col*4096,row*4096],'zipEntry':'tiles/'+tile+'-4096.png','productionBytesUnmodified':True});keep(d['candidate'],'tiles/'+tile+'-4096.png')
tiles.sort(key=lambda t:t['tile']);assert len(tiles)==11 and len(newsources)==37
identity=hashlib.sha256(json.dumps([(t['tile'],t['sha256']) for t in tiles]).encode()).hexdigest()[:16];D=Z/'verified-eleven-tiles-20261012'/identity;D.mkdir(parents=True);assert not list(D.iterdir())
preview=Image.new('RGB',(2560,1624),'#20252b');draw=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);draw.text((18,8),'PREVIEW ONLY | 11 reviewed tiles | originals: 4096 x 4096',font=font,fill='white');bytile={t['tile']:t for t in tiles}
for row in range(5,8):
 for col in range(3,8):
  tile=f'r{row:02}_c{col:02}';xy=((col-3)*512,48+(row-5)*512)
  if tile in bytile:
   with Image.open(check(bytile[tile])) as im:assert im.size==(4096,4096);preview.paste(im.resize((512,512),Image.Resampling.LANCZOS),xy)
   draw.rectangle((xy[0],xy[1]+476,xy[0]+155,xy[1]+511),fill='#20252b');draw.text((xy[0]+10,xy[1]+478),tile,font=font,fill='white')
  else:
   draw.rectangle((xy[0],xy[1],xy[0]+511,xy[1]+511),fill='#30373f',outline='#59616b');label=tile+(' | REPAIR PENDING' if tile=='r07_c06' else ' | PENDING');draw.text((xy[0]+18,xy[1]+240),label,font=font,fill='#a9b1ba')
draw.text((18,1586),'Reduced presentation mosaic. Northwest target: 60 tiles. 48 lack native sources; 1 complete-source tile needs repairs.',font=font,fill='white');preview.save(D/'preview-only-mosaic-2560.png')
validation={'createdAtUtc':now(),'status':'passed','nativeSourceCount':184,'inheritedValidatedSources':147,'newSourceCount':37,'newFixedGridSources':32,'newSupplementalNativeSources':5,'newSources':newsources,'inheritedNineSourceAudit':op['sourceValidation'],'newDeliveries':newdeliveries,'newNativeOutputPixelsProven':33554432,'allNativeOutputPixelsProven':184549376,'newSourcesHostByteIdentical':True,'sourceResampled':False,'actualImageBackendModel':None,'actualImageBackendQuality':None};write(D/'source-validation.json',validation)
summary={'schemaVersion':1,'createdAtUtc':now(),'status':'eleven_tiles_internal_and_available_shared_boundaries_passed','tileCount':11,'tiles':tiles,'ownedZoneTileCount':60,'tilesWithAll16NativePatches':12,'internallyPassedTiles':11,'tilesStillMissingNativePatches':48,'missingNativePatches':768,'fullSourceTilesPendingRepairOrReview':1,'nativeSourceCount':184,'blockingCountWithinDeliveredTiles':0,'wholeZoneComplete':False,'formalAccepted':False,'formalAcceptedCount':0,'productionResampled':False,'productionPNGBytesUnmodified':True,'sourceValidation':ref(D/'source-validation.json'),'newDeliveries':newdeliveries,'preservedNinePackage':ref(OLD/'package.json'),'preservedNineArchive':op,'preview':{**ref(D/'preview-only-mosaic-2560.png'),'previewOnly':True,'productionArt':False},'pendingTile':'r07_c06','outerPerimeterStatus':'Unfinished neighboring tiles are pending external review; internal source coverage and review counts are reported separately.','newGenerationPaused':True,'exactFutureModelRequired':'GPT Image 2.5','generationHold':ref(Z/'generation-hold-current-model-requirement-20261012.json')};write(D/'delivery-summary.json',summary)
(D/'README.txt').write_text('11 reviewed 4096 x 4096 production PNGs. All production image bytes are unchanged.\nAll inherited nine-package files and original sources are preserved. Two new tiles add37 unchanged native1254 sources, exact same-world pixel proofs, and native seam/boundary review evidence.\nThe reduced mosaic is PREVIEW ONLY. Gray cells are pending. Northwest target60 remains incomplete:48 tiles lack native sources (768 patches), and1 complete-source tile awaits repair/review.\nNew generation is paused pending a route explicitly selecting verified GPT Image2.5; paid API is not authorized. Existing unspecified-backend images are preserved without inventing model metadata.\n',encoding='utf-8')
keep(Z/'generation-hold-current-model-requirement-20261012.json');keep(Z/'saved-successful-output-audit-20261012-v2.json')
files=[]
for item in oldfiles:
 item=dict(item);item['inheritedFromArchiveEntry']=item['zipEntry']
 if '/' not in item['zipEntry']:item['zipEntry']='historical-nine/'+item['zipEntry']
 files.append(item)
for item in extras.values():
 if item['zipEntry'] not in {x['zipEntry'] for x in files}:files.append(item)
 else:assert next(x['sha256'] for x in files if x['zipEntry']==item['zipEntry'])==item['sha256']
for f in (D/'source-validation.json',D/'delivery-summary.json',D/'preview-only-mosaic-2560.png',D/'README.txt'):files.append({'originalFile':str(f),'zipEntry':f.name,'sha256':sha(f)})
assert len({x['zipEntry'] for x in files})==len(files)
write(D/'package-contents.json',{'schemaVersion':1,'files':files,'manifestSelfHashInPackageJson':True});files.append({'originalFile':str(D/'package-contents.json'),'zipEntry':'package-contents.json','sha256':sha(D/'package-contents.json')})
archive_path=D/'northwest-eleven-4k-tiles.zip'
with zipfile.ZipFile(oldzip) as srczip,zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as dstzip:
 for item in files:
  assert sha(item['originalFile'])==item['sha256']
  if 'inheritedFromArchiveEntry' in item:
   with srczip.open(item['inheritedFromArchiveEntry']) as src,dstzip.open(item['zipEntry'],'w',force_zip64=True) as dst:shutil.copyfileobj(src,dst,1048576)
  else:dstzip.write(item['originalFile'],item['zipEntry'])
with zipfile.ZipFile(archive_path) as archive:
 assert archive.testzip() is None;assert set(archive.namelist())=={x['zipEntry'] for x in files}
 for item in files:
  with archive.open(item['zipEntry']) as h:assert hashlib.file_digest(h,'sha256').hexdigest()==item['sha256']==sha(item['originalFile'])
  if item['zipEntry'].endswith('.json'):json.loads(archive.read(item['zipEntry']).decode('utf-8-sig'))
assert all(sha(f)==digest for f,digest in inputs.items())
verification={'createdAtUtc':now(),'status':'passed','archive':ref(archive_path),'verifiedEntries':len(files),'zipCRCVerified':True,'allEntrySHA256Verified':True,'allOriginalFileBytesVerified':True,'allArchivedJsonStrictlyParsed':True,'allProtectedInputsUnchanged':True,'oldNineArchiveUnchanged':ref(oldzip)};write(D/'archive-verification.json',verification)
package={**ref(archive_path),'createdAtUtc':now(),'sizeBytes':archive_path.stat().st_size,'verifiedEntries':len(files),'tileCount':11,'nativeSourceCount':184,'summary':ref(D/'delivery-summary.json'),'sourceValidation':ref(D/'source-validation.json'),'preview':ref(D/'preview-only-mosaic-2560.png'),'packageContents':ref(D/'package-contents.json'),'verification':ref(D/'archive-verification.json'),'wholeZoneComplete':False,'formalAccepted':False};write(D/'package.json',package);print(json.dumps(package,indent=2))
