"""Private west_sol production helper. Authorized c11 then c10 rows6/7; no shared state writes."""
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
import argparse,datetime,json,hashlib,re,shutil,uuid
Z=Path(__file__).resolve().parent
R=Z/'records/west_sol';R.mkdir(exist_ok=True)
C=json.loads((Z.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
ALLOWED={'r06_c11','r07_c11','r06_c10','r07_c10'}
A=Z.parent/'accelerated-jewelry-approach'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role=None):
 d={'path':str(Path(p).resolve()).replace('\\','/'),'sha256':sha(p)}
 if role:d['role']=role
 return d
def write(p,d,replace=False):
 p=Path(p);assert replace or not p.exists(),('Refuse overwrite',str(p))
 temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(p)
def coords(p):
 m=re.fullmatch(r'(r(\d{2})_c(\d{2}))_p([1-4])([1-4])',p);assert m and m[1] in ALLOWED,p
 tr,tc,sr,sc=map(int,[m[2],m[3],m[4],m[5]])
 x=(tc-1)*4096+(sc-1)*1024;y=(tr-1)*4096+(sr-1)*1024
 return dict(id=p,tile=m[1],patchRow=sr,patchColumn=sc,coreGlobalBox=[x,y,x+1024,y+1024],nativeGlobalBox=[x-115,y-115,x+1139,y+1139],nativeCoreBox=[115,115,1139,1139],expectedSize=[1254,1254],overviewBox=[v*1254/57344 for v in [x-115,y-115,x+1139,y+1139]])
def mandatory():
 return [ref(C[k],role) for k,role in [('layoutReference','authoritative whole village layout only'),('detailStyleReference','daylight material detail only, not coordinate crop'),('primaryStyleReference','approved Q Daoist painterly style only; ignore UI/text/night')]]
def own_selection(tile):
 p=R/f'{tile}.selected.json';return read(p) if p.exists() else {}
def evidence(path):
 for suffix in ['.generation.json','.derived.json']:
  p=Path(str(path)+suffix)
  if p.exists():return ref(p)
 p=Path(path).with_suffix('.generation.json')
 if p.exists():return ref(p)
 return None
def get_neighbor(p,side):
 co=coords(p);tile=co['tile'];sr=co['patchRow'];sc=co['patchColumn']
 item=None;key=None;selection=None
 if side=='right':
  if sc==4:
   rightTile=tile[:4]+f'c{int(tile[5:])+1:02d}';key=rightTile+f'_p{sr}1'
   if rightTile.endswith('c12'):
    selection=Z/f'records/{rightTile}.selection-closure-v5.json';item=read(selection)['patches'][key]
   else:
    selection=R/f'{rightTile}.selected.json';item=own_selection(rightTile).get(key)
  else:
   key=tile+f'_p{sr}{sc+1}';selection=R/f'{tile}.selected.json';item=own_selection(tile).get(key)
 elif side=='top':
  if sr>1:
   key=tile+f'_p{sr-1}{sc}';selection=R/f'{tile}.selected.json';item=own_selection(tile).get(key)
  elif tile.startswith('r07_'):
   topTile=tile.replace('r07_','r06_');key=topTile+f'_p4{sc}';selection=R/f'{topTile}.selected.json';item=own_selection(topTile).get(key)
  else:
   topTile=tile.replace('r06_','r05_');key=topTile+f'_p4{sc}';selection=A/f'{topTile}/records/p4{sc}.selection.json'
   if selection.exists():
    d=read(selection);item={'path':d['file'],'sha256':d['sha256']}
 if not item:return None
 path=Path(item['path']);assert path.exists() and sha(path)==item['sha256'],('Neighbor hash mismatch',path)
 ev=evidence(path);assert ev,('Missing native coordinate evidence',path)
 data=read(ev['path']);ngb=data.get('nativeGlobalBox',data.get('globalNativeBox',data.get('coordinates',data.get('coordinate',{})).get('nativeGlobalBox')))
 assert ngb and ngb[:2]==[co['nativeGlobalBox'][0]+(1024 if side=='right' else 0),co['nativeGlobalBox'][1]+(-1024 if side=='top' else 0)],('Wrong native neighbor geometry',path,ngb,co)
 return dict(**ref(path,f'sharp native {side}230 edge anchor'),patchId=key,selection=ref(selection),provenance=ev,nativeGlobalBox=ngb,side=side,
 sourceCropBox=[0,0,230,1254] if side=='right' else [0,1024,1254,1254],targetPasteAt=[1024,0] if side=='right' else [0,0])
def init():
 plan=read(Z/'records/zone-tile-plan.json');owned={t['id']:t for t in plan['tiles']};forbidden=plan['handedOffTiles']
 assert all(owned[t]['ownedByThisZone'] for t in ALLOWED)
 assert not(ALLOWED & set(forbidden))
 for t in sorted(ALLOWED):
  p=R/f'{t}.coordinates.json'
  if not p.exists():write(p,dict(tile=t,patches=[coords(t+f'_p{r}{c}') for c in range(4,0,-1) for r in range(1,5)],references=mandatory(),traversal='columns4 to1, each column rows1 to4',finalResizeAllowed=False))
 layout=Image.open(C['layoutReference']).convert('RGB')
 gp=Z/'guides/west_sol-context-layout-only.png'
 if not gp.exists():
  box=[int(v*1254/57344) for v in [39706,19226,47560,29926]]
  layout.crop(box).resize((900,1226),Image.Resampling.NEAREST).save(gp)
  write(Path(str(gp)+'.derived.json'),dict(**ref(gp),source=ref(C['layoutReference']),sourceBox=box,purpose='Wider coordinate layout-only guide, never final pixels',operation='nearest resize for guide readability only'))
 audit=R/'ownership-audit-20261012-v2-c10-extension.json'
 if not audit.exists():write(audit,dict(schemaVersion=1,checkedAtUtc=now(),zonePlan=ref(Z/'records/zone-tile-plan.json'),ownedTargets=sorted(ALLOWED),forbiddenHandedOff=forbidden,rightSelectionRecords=[ref(Z/f'records/{t.replace("c11","c12")}.selection-closure-v5.json') for t in sorted(ALLOWED) if t.endswith('c11')],c10RightSource='Private c11 selected natives with coordinate and hash checks',authorizedOrder=['r06_c11','r07_c11','r06_c10','r07_c10'],writesAllowed='Private west_sol helper, guides, generated natives, private QA and records; no shared progress/index or other-zone writes'))
 print(json.dumps(dict(targets=sorted(ALLOWED),forbidden=forbidden,contextGuide=str(gp))))
def prepare(p,v,subject,contextSide=None):
 co=coords(p);plan=read(Z/'records/zone-tile-plan.json');assert next(t for t in plan['tiles'] if t['id']==co['tile'])['ownedByThisZone']
 gp=Z/f'guides/{p}-{v}-west_sol.layout-native-anchors.png';assert not gp.exists()
 im=Image.open(C['layoutReference']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
 neighbors=[]
 for side in ['right','top']:
  item=get_neighbor(p,side)
  if item:
   q=Image.open(item['path']).convert('RGB');assert q.size==(1254,1254)
   im.paste(q.crop(item['sourceCropBox']),tuple(item['targetPasteAt']));neighbors.append(item)
 assert any(e['side']=='right' for e in neighbors),('Right native anchor required',p)
 im.save(gp)
 neighborContext=next((e for e in neighbors if e['side']==contextSide),neighbors[0]) if contextSide else next((e for e in neighbors if e['side']=='top'),neighbors[0])
 refs=mandatory()+[ref(gp,'coordinate layout-only interior plus 1:1 sharp native edge anchors')]
 if contextSide!='guide':refs.append(ref(neighborContext['path'],f'actual {neighborContext["side"]} neighbor native scale and cropped geometry context only'))
 contextText=f'Attachment5 is the actual {neighborContext["side"]} neighboring native patch for its existing scale and object continuation only; it is OUTSIDE this frame, do not copy its full scene into this patch.' if contextSide!='guide' else 'All adjoining native artwork is shown within attachment4 as copied native1:1 edge bands at its exact coordinate position; there is no outside neighboring whole scene to recompose into this frame.'
 pp=R/f'{p}-{v}.prompt.txt';args=R/f'{p}-{v}.actual-arguments.json';planpath=R/f'{p}-{v}.plan.json'
 anchors=' '.join('RIGHT x1024..1254 is existing native230 anchor; meet its original contours, scale and color.' if e['side']=='right' else 'TOP y0..230 is existing native230 anchor; continue its original objects below without horizontal splice.' for e in neighbors)
 prompt=f'''Use case: stylized-concept. Asset: one native1254 by1254 square patch of a continuous painterly Q Daoist village game map. Attachment4 is the EXACT fixed coordinate frame with sharp native anchors and a low-detail blurred positional interior; preserve camera, scale, object placement and natural crop. Rebuild the blurred interior in fresh crisp native art; never enlarge or copy its blurred pixels. {anchors} The sharp strips are real adjoining artwork, not separate inset panels. Maintain the same continuous surfaces across their inner boundaries, with no shifted contour, duplicated geometry, exposure stripe or blur. {contextText} Sharp native anchors take precedence over blurred guide details at the join. Never zoom out or fit a whole object into the patch. Attachment1 is the authoritative full-map layout only; attachment2 is the daylight material reference only; attachment3 is the approved rounded detailed painterly Q Daoist style only, ignore its UI, text, people and nighttime. Exact square frame,1024 core at[115,115,1139,1139] plus115halo. World native box{co['nativeGlobalBox']}. Bright daylight, warm upper-left illumination, fine hand-painted facets, rounded clean outlines and natural blue-grey/light-grey stone slab joints, rich warm timber. No photorealism, pixelation, blur, grid, labels, text, people, UI, border or watermark. Do not invent objects or move architecture, close a passage, add free-standing street trees or use red paving. Keep only festival details that belong to existing architecture: red trim and modest spent firecracker scraps do not block routes.\nPATCH {p}: {subject}'''
 assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
 write(args,dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
 configpath=Path('D:/work/image/config/image-generation.json')
 write(planpath,dict(schemaVersion=1,patchId=p,version=v,preparedAtUtc=now(),coordinates=co,references=refs,nativeEdgeSources=neighbors,guide=ref(gp),guidePurpose='Resampled low-res layout interior plus exact opaque native anchors; non-final guide only; TOP owns shared corner',contract=ref(Z.parent/'production-contract.json'),configSnapshot=read(configpath) if configpath.exists() else None,configSource=dict(path=str(configpath),available=configpath.exists(),purpose='read-only snapshot; not builtin parameter interface'),actualModel=None,actualQuality=None,submittedSelectors=dict(model=None,quality=None),formalAccepted=False))
 write(Path(str(gp)+'.derived.json'),dict(**ref(gp),coordinates=co,sourceLayout=mandatory()[0],nativeEdgeSources=neighbors,operation='Overview EXTENT bicubic layout-only crop then integer native right230 and top230; top owns corner',finalPixels=False))
 print(json.dumps(dict(arguments=str(args),guide=str(gp),nativeEdgeSources=neighbors)))
def ingest(p,v,host):
 plan=read(R/f'{p}-{v}.plan.json');dst=Z/f'native/{p}-{v}-west_sol.png'
 if dst.exists():assert sha(dst)==sha(host),('Existing native differs from returned host output',dst)
 else:shutil.copyfile(host,dst)
 im=Image.open(dst);pp=R/f'{p}-{v}.prompt.txt';rp=R/f'{p}-{v}.receipt.json';rr=read(rp)
 request=rr.get('request',rr.get('actualRequest'));assert request['prompt']==pp.read_text(encoding='utf-8');assert request['referenced_image_paths']==[e['path'] for e in plan['references']]
 gen=dict(plan)
 gen.update(file=str(dst),sha256=sha(dst),nativeSize=list(im.size),width=im.width,height=im.height,tool='image_gen.imagegen',route='builtin',submittedParameters=dict(transparent_background=False,model=None,quality=None),
 actualModel=None,actualQuality=None,actualModelReason='No selector or actual model/quality identification exposed by built-in tool',source=ref(host,'byte-for-byte host output copy'),prompt=ref(pp),receipt=ref(rp),pngMetadataKeys=list(im.info),nativeResizePerformed=False,observedAtUtc=rr['observedAtUtc'],status='native_candidate_pending_review',formalAccepted=False)
 write(Path(str(dst)+'.generation.json'),gen)
 assert im.size==(1254,1254),('Native size mismatch preserved; never resize',im.size)
 qa=Z/f'qa/west_sol/{p}-{v}';qa.mkdir(parents=True,exist_ok=False);striprecords=[]
 for e in plan['nativeEdgeSources']:
  q=Image.open(e['path']).convert('RGB');out=Image.new('RGB',(256,1254) if e['side']=='right' else (1254,256))
  if e['side']=='right':out.paste(im.crop((1011,0,1139,1254)),(0,0));out.paste(q.crop((115,0,243,1254)),(128,0))
  else:out.paste(q.crop((0,1011,1254,1139)),(0,0));out.paste(im.crop((0,115,1254,243)),(0,128))
  qp=qa/f'{e["side"]}.native-1to1.png';out.save(qp)
  striprecords.append(dict(**ref(qp),nativeSize=list(out.size),sources=[ref(dst),e],operation='exact native integer crop/paste; no resizing',seamLocalCoordinate=128))
 write(qa/'construction.json',dict(patch=p,native=ref(dst),coordinates=plan['coordinates'],nativeEdgeSources=plan['nativeEdgeSources'],strips=striprecords,formalAccepted=False,visualReview='pending'))
 print(json.dumps(dict(native=str(dst),nativeSize=list(im.size),sha256=sha(dst),qa=str(qa),strips=striprecords)))
def select(p,v,review):
 co=coords(p);np=Z/f'native/{p}-{v}-west_sol.png';assert np.exists();sel=own_selection(co['tile']);sel[p]=ref(np)
 write(R/f'{co["tile"]}.selected.json',sel,True)
 write(R/f'{p}-{v}.review.json',dict(schemaVersion=1,reviewer='west_sol',reviewedAtUtc=now(),patch=p,native=ref(np),review=review,selectedLocallyForProposal=True,formalAccepted=False))
 print(json.dumps(dict(selected=p,coveredCores=len(sel))))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('op');a.add_argument('patch',nargs='?');a.add_argument('--version',default='v1');a.add_argument('--subject');a.add_argument('--source');a.add_argument('--review');a.add_argument('--context-side',choices=['right','top','guide'],default='guide');args=a.parse_args()
 if args.op=='init':init()
 elif args.op=='prepare':prepare(args.patch,args.version,args.subject,args.context_side)
 elif args.op=='ingest':ingest(args.patch,args.version,args.source)
 elif args.op=='select':select(args.patch,args.version,args.review)
