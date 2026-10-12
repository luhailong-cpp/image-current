from pathlib import Path
from PIL import Image, ImageChops
from workflow import ROOT,read,write,sha,now,progress
import json
tile='r10_c11'
items=[];errors=[];historical=[]
for f in sorted((ROOT/'native').glob(tile+'*.png')):
    rec=read(Path(str(f)+'.generation.json')); im=Image.open(f)
    refchecks=[]
    for r in rec['references']:
        p=Path(r['file']); exists=p.exists()
        ok=sha(p)==r['sha256'] if exists else None
        refchecks.append({'file':r['file'],'exists':exists,'hashMatches':ok})
        if not exists:historical.append({'native':f.name,'reference':r['file'],'recordedSha256':r['sha256'],'note':'Historical input now unavailable; old record preserved unchanged. No claim of replaying missing bytes.'})
    checks={'hash':sha(f)==rec['sha256'],'native1254':im.size==(1254,1254),'prompt':sha(Path(rec['prompt']))==rec['promptSha256'],'availableReferenceHashes':all(r['hashMatches'] is not False for r in refchecks),'actualUnknown':rec['actualModel'] is None and rec['actualQuality'] is None,'submittedUnknown':rec['submittedParameters']=={'model':None,'quality':None},'sourceByteIdentical':sha(Path(rec['sourceOutputPath']))==sha(f),'receiptExists':(ROOT/rec['evidence']['toolReceipt']).exists()}
    items.append({'file':f.as_posix(),'checks':checks,'references':refchecks,'availableEvidencePassed':all(checks.values()),'fullReferenceReplayPossible':all(r['exists'] for r in refchecks)})
    if not all(checks.values()):errors.append(f.name)
selected=read(ROOT/f'selected-native-{tile}.json')
candidate=Path(selected.get('candidateFile',ROOT/'tiles'/f'{tile}.candidate.png'));im=Image.open(candidate).convert('RGB')
base=Image.open(ROOT/'tiles/r10_c11.candidate.png').convert('RGB')
replay=Image.new('RGB',(4096,4096))
corechecks=[]
for s in selected['entries']:
    x,y=s['destination']; box=[x,y,x+1024,y+1024]
    nativecore=Image.open(s['file']).convert('RGB').crop(tuple(s['sourceCrop']))
    same=ImageChops.difference(base.crop(tuple(box)),nativecore).getbbox() is None
    replay.paste(nativecore,(x,y))
    corechecks.append({'file':s['file'],'sha256':s['sha256'],'destinationBox':box,'pixelIdentical':same})
for overlay in selected.get('overlays',[]):
    replay.paste(Image.open(overlay['file']).convert('RGB').crop(tuple(overlay['sourceCrop'])),tuple(overlay['destination']))
finalReplayIdentical=ImageChops.difference(replay,im).getbbox() is None
index=read(ROOT/'qa/r10_c11-neighborhood-v01/index.json')
edges=[]
for e in index['entries']:
    old=Image.open(e['file']).convert('RGB'); rebuilt=Image.new('RGB',old.size)
    parts=e['parts'] if 'parts' in e else zip(e['sources'],e['sourceCrops'],e['destinations'])
    for source,crop,dest in parts:
        path=candidate if source=='sw' else Path(index['sources'][source]['file'])
        rebuilt.paste(Image.open(path).convert('RGB').crop(tuple(crop)),tuple(dest))
    edges.append({'id':e['id'],'reviewedSourceImage':e['file'],'unchangedPixels':ImageChops.difference(old,rebuilt).getbbox() is None,'priorReviewer':e.get('reviewer'),'priorStatus':e.get('status')})
result={'tile':tile,'auditedAt':now(),'nativeCount':len(items),'items':items,'errors':errors,'historicalMissingReferences':historical,'candidateDimensions':list(im.size),'candidateSha256':sha(candidate),'all16BaseCoreContributionsPixelIdentical':all(s['pixelIdentical'] for s in corechecks),'finalContributionReplayPixelIdentical':finalReplayIdentical,'coreContributions':corechecks,'overlays':selected.get('overlays',[]),'nativeResampling':False,'externalReviewPixelReplay':edges,'allReviewedExternalPixelsUnchanged':all(e['unchangedPixels'] for e in edges),'formalAccepted':False}
write(ROOT/'qa/r10_c11-source-audit.json',result)
print(json.dumps({k:result[k] for k in ['nativeCount','errors','candidateSha256','all16BaseCoreContributionsPixelIdentical','finalContributionReplayPixelIdentical','allReviewedExternalPixelsUnchanged']}) )
