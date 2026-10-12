"""Versioned, tile-owned native production. No shared-state or historical-art writes."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,importlib.util,argparse,re
T=Path(__file__).resolve().parent;Z=T.parent;VERSION='v20261012'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 p=Path(p);assert p.resolve().is_relative_to(T.resolve())
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ev(p,**k):return {'file':str(p),'sha256':sha(p),**k}
def now():return datetime.now(timezone.utc).isoformat()
def selected(tile,patch):
 sf=tile/'selected-native.json';se=read(sf) if sf.exists() else {}
 f=se.get(patch,patch+'.png');assert Path(f).name==f
 p=tile/'native'/f
 assert p.exists(),f'Required real neighbor missing: {p}'
 r=read(str(p)+'.generation.json');assert sha(p)==r['sha256']
 with Image.open(p) as im:assert im.size==(1254,1254)
 return p,r
def neighbors(patch):
 r,c=int(patch[1]),int(patch[2])
 return [('west',T if c>1 else Z/'r08_c14',f'p{r}{c-1}' if c>1 else f'p{r}4',[1024,0,1254,1254],[0,0]),
 ('north',T if r>1 else Z/'r07_c15',f'p{r-1}{c}' if r>1 else f'p4{c}',[0,1024,1254,1254],[0,0])]
def progress(note=None,inflight=None):
 path=T/'tile-progress.json';state=read(path) if path.exists() else {}
 sf=T/'selected-native.json';sel=read(sf) if sf.exists() else {};records=[]
 for patch in sorted(sel):
  p,r=selected(T,patch);records.append({'patch':patch,**ev(p)})
 state.update({'tile':T.name,'updatedAt':now(),'status':'prepared-awaiting-actual-north' if not records else 'versioned-native-production','nativePatchCount':len(records),'selectedCoreCount':len(records),'remainingCoreCount':16-len(records),'nativeSources':records,'completeCandidateCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'candidate':str(T/'candidates'/f'{T.name}.candidate-{VERSION}.png'),'candidateSha256':None,'inflightGeneration':inflight,'actualModel':None,'actualQuality':None,'resumeAuthority':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','nextStep':note or 'Continue only when true north and west pixels are available; no native overwrite.'})
 save(path,state);return state
def context(patch):
 assert re.fullmatch('p[1-4][1-4]',patch)
 stem=f'{patch}-{VERSION}';req=T/'prompts'/(stem+'.request.json')
 out=T/'layout-only'/(stem+'-mixed-context.png')
 assert not req.exists() and not out.exists(),'Context is immutable after preparation'
 plan=read(T/'coordinates.json');coord=next(p for p in plan['patches'] if p['id']==patch)
 guide=Path(coord['guide']);assert sha(guide)==coord['guideSha256']
 im=Image.open(guide).convert('RGB');derived=[ev(guide,role='layout-only geometry guidance; must repaint')]
 neighborfiles=[];outs=[]
 for direction,other,np,box,pos in neighbors(patch):
  src,record=selected(other,np);h=sha(src);native=Image.open(src).convert('RGB')
  im.paste(native.crop(box),tuple(pos))
  derived.append(ev(src,role=f'actual {direction} native context',tile=other.name,patch=np,crop=box,paste=pos))
  neighborfiles.append(str(src))
  if other!=T:outs.append(other)
 for other in dict.fromkeys(outs):
  tp=other/'tile-progress.json';state=read(tp) if tp.exists() else {}
  fallback=other/'candidates'/(other.name+'.candidate.png')
  f=Path(state.get('candidate') or fallback)
  if not f.exists():continue
  h=sha(f)
  if state.get('candidateSha256'):assert h==state['candidateSha256']
  ox=(int(other.name[5:7])-1)*4096;oy=(int(other.name[1:3])-1)*4096
  wx,wy,wr,wb=coord['contextWorldBox'];box=[max(wx,ox),max(wy,oy),min(wr,ox+4096),min(wb,oy+4096)]
  if box[2]<=box[0] or box[3]<=box[1]:continue
  sb=[box[0]-ox,box[1]-oy,box[2]-ox,box[3]-oy];dest=[box[0]-wx,box[1]-wy]
  cim=Image.open(f).convert('RGB');assert cim.size==(4096,4096)
  im.paste(cim.crop(sb),tuple(dest));assert sha(f)==h
  derived.append(ev(f,role='current repaired candidate actual core override',crop=sb,paste=dest))
 im.save(out);save(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'createdAt':now(),'derivedFrom':derived,'neighborNativeReferences':neighborfiles,'coordinates':coord,'assetRole':'mixed guidance; blurry layout area must be freshly painted','operation':{'type':'integer crop paste only','outputPixels':[1254,1254],'requiredDirections':['west','north'],'resized':False}})
 print(json.dumps({'target':str(out),'neighbors':neighborfiles}))
def request(patch,note):
 stem=f'{patch}-{VERSION}';out=T/'layout-only'/(stem+'-mixed-context.png');meta=read(str(out)+'.generation.json')
 assert sha(out)==meta['sha256']
 for d in meta['derivedFrom']:assert sha(d['file'])==d['sha256']
 contract=read(Z.parent/'production-contract.json')
 refs=[str(out),contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference']]
 roles=['exact native-overlap mixed edit target including true north/west pixels','approved full-city layout reference','approved daylight and material close detail','approved Daoist illustration style']
 prompt=f"""Use case: precise-object-edit. Produce the exact native1254x1254 opaque map crop {T.name}/{stem}, same framing.
Image1 is the ONLY composition and edit target. Replace only its blurry rectangle x230..1254,y230..1254 with newly painted detail. Sharp top230 and left230 are true neighboring artwork: lock their positions and continue their actual objects exactly without a cut at x230 or y230. Preserve topmost115 and leftmost115 unchanged. Images2/3/4 are supporting style/material references ONLY: do not import their architecture, road shapes, props, landscape or composition. Full west/north neighboring crops were inspected and their exact source pixels are attached inside Image1 with recorded source hashes.
{note}
Lock viewpoint, scale, geographic positions, masonry course endpoints and inherited object silhouettes. Complete partly inherited objects once, do not duplicate or invent architecture. Natural varied pale grey/cyan stone ground; no overall red ground. Crisp rounded hand-painted Daoist Q detail, soft upper-left daylight, moderate broad material variation, fine clean construction. Red/gold only on indicated festive architecture/props and sparse spent paper remnants. Preserve walkable lanes. No new isolated tree or pot, new lantern, character, lettering, UI, framing, watermark or transparency. No blurry enlarged-guide pixels, blur, defocus, smear, texture stretch, rescaling, warp, zoom or camera shift. Output exactly1254x1254."""
 pf=T/'prompts'/(stem+'.prompt.txt');rf=T/'prompts'/(stem+'.request.json')
 assert not pf.exists() and not rf.exists()
 pf.write_text(prompt,encoding='utf8')
 save(rf,{'prompt':prompt,'referenced_image_paths':refs,'referenceRoles':roles,'transparent_background':False})
 progress(f'Complete {stem} once from saved built-in request; persist actual success immediately.',{'patch':stem,'request':str(rf),'requestSha256':sha(rf),'status':'request-saved-awaiting-builtin-result'})
 print(str(rf))
def ingest(patch,source):
 stem=f'{patch}-{VERSION}';rec=T/'receipts'/(stem+'.receipt.json')
 assert rec.exists() and Path(source).exists()
 with Image.open(source) as im:assert im.size==(1254,1254) and im.format=='PNG'
 spec=importlib.util.spec_from_file_location('tile_wrapper',Z/'tile_worker.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.setup(T.name);m.p.ingest(stem,source)
 selp=T/'selected-native.json';sel=read(selp) if selp.exists() else {}
 assert patch not in sel
 sel[patch]=stem+'.png';save(selp,sel)
 progress('Continue available patches using recorded selected north and west natives.')
 print(json.dumps({'canonical':patch,'selected':sel[patch],'sha256':sha(T/'native'/sel[patch])}))
def audit():
 plan=read(T/'coordinates.json');assert plan['coreWorldBox']==[57344,28672,61440,32768]
 for p in plan['patches']:
  assert sha(p['guide'])==p['guideSha256']
  with Image.open(p['guide']) as im:assert im.size==(1254,1254)
 contract=read(Z.parent/'production-contract.json');refs=[ev(contract[k],role=k) for k in ['layoutReference','detailStyleReference','primaryStyleReference']]
 west=Z/'r08_c14';state=read(west/'tile-progress.json');candidate=Path(state['candidate']);assert sha(candidate)==state['candidateSha256']
 westsrc=[];im=Image.open(candidate).convert('RGB')
 for r,y in enumerate([0,1024,2048,2842],1):
  src,record=selected(west,f'p{r}4');dest=T/'qa'/f'west-current-row{r}-v20261012.png'
  im.crop((3584,y,4096,y+1254)).save(dest)
  westsrc.append({'native':ev(src),'candidateCrop':ev(dest),'candidateCropBox':[3584,y,4096,y+1254]})
 save(T/'qa/preparation-v20261012.json',{'tile':T.name,'preparedGuideCount':16,'coordinates':ev(T/'coordinates.json'),'worldBox':plan['coreWorldBox'],'approvedReferences':refs,'resumeAuthority':ev('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json'),'historicalFreeze':ev(Z/'migration-freeze-20261011.json'),'deliveryIndex':ev(Z/'delivery-index-20261011.json'),'westCandidate':ev(candidate),'westSources':westsrc,'actualModel':None,'actualQuality':None,'formalAcceptedCount':0,'note':'Historical freeze read as preserved baseline evidence. Resume authorization permits new versioned art only. No other tile written.'})
 progress('Await r07_c15 selected p41; west r08_c14 selected p14 and current candidate ready. No generation in flight.')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','context','request','ingest','progress']);ap.add_argument('patch',nargs='?',default='');ap.add_argument('value',nargs='?',default='');a=ap.parse_args()
 if a.mode=='audit':audit()
 elif a.mode=='context':context(a.patch)
 elif a.mode=='request':request(a.patch,a.value)
 elif a.mode=='ingest':ingest(a.patch,a.value)
 else:progress(a.value or a.patch)

