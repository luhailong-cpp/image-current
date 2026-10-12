from pathlib import Path
from PIL import Image
import json,sys,hashlib,datetime
T=Path(__file__).resolve().parent;version=sys.argv[1];patch=version.split('-')[0]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=T/'native'/(version+'.png');record=json.loads(Path(str(src)+'.generation.json').read_text());assert sha(src)==record['sha256'];assert Image.open(src).size==(1254,1254)
sp=T/'selected-native.json';sel=json.loads(sp.read_text(encoding='utf-8-sig'));sel[patch]=src.name;sp.write_text(json.dumps(sel,indent=2)+'\n')
valid=[p for p,f in sel.items() if (T/'native'/f).exists()];missing=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in valid]
out=T/'qa/resume3-20261013';out.mkdir(exist_ok=True)
native=Image.open(src).convert('RGB');joins=[]
req=json.loads((T/'prompts'/(version+'.request.json')).read_text());context=Path(req['referenced_image_paths'][3]);guide=json.loads(Path(str(context)+'.generation.json').read_text())
for direction in ['west','north']:
 sources=[d for d in guide['derivedFrom'] if d.get('role')=='actual '+direction+' native context']
 if not sources:continue
 n=Path(sources[0]['file']);old=Image.open(n).convert('RGB');assert sha(n)==sources[0]['sha256']
 if direction=='west':
  j=Image.new('RGB',(512,1024));j.paste(old.crop((883,115,1139,1139)),(0,0));j.paste(native.crop((115,115,371,1139)),(256,0))
 else:
  j=Image.new('RGB',(1024,512));j.paste(old.crop((115,883,1139,1139)),(0,0));j.paste(native.crop((115,115,1139,371)),(0,256))
 f=out/(version+'-'+direction+'-join.png');assert not f.exists();j.save(f);joins.append({'direction':direction,'file':str(f),'sha256':sha(f),'source':str(n),'sourceSha256':sha(n)})
report={'tile':T.name,'patch':patch,'native':str(src),'nativeSha256':sha(src),'joins':joins,'status':'native-return-layout-quick-checked; join-window-review-pending','actualModel':None,'formalAccepted':False}
(out/(version+'-quick-review.json')).write_text(json.dumps(report,indent=2)+'\n')
pf=T/'tile-progress.json';p=json.loads(pf.read_text(encoding='utf-8-sig'));p.update(status='native-production-resumed',selectedCoreCount=len(valid),remainingCoreCount=len(missing),missingSelectedIds=missing,generatedNativeCount=len(list((T/'native').glob('p*.png'))),owner='/root/east_resume3',lastCompletedPatch=patch,lastCompletedNative=str(src),lastCompletedSha256=sha(src),inflightRequests=[],unsavedSuccessfulOutputs=[],generationStopped=False,newGenerationAllowed=True,requestedFutureImageModel='free/included2.5 preferred; builtin2.0 allowed; actual model undisclosed',nextStep='Continue missing native cores with current AGENTS and split; full seam review after16.',updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());pf.write_text(json.dumps(p,indent=2)+'\n')
print(json.dumps({'tile':T.name,'selectedCoreCount':len(valid),'joins':joins}))
