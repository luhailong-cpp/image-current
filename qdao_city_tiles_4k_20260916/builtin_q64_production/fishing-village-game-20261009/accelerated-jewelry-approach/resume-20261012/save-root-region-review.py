from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1];e=b/'resume-20261012'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(e/'candidate-manifest.json');region=Image.open(m['regionCandidate']['file']).convert('RGB')
oldreview=b/'qa/region-seams/findings.json';oldvalid=b/'qa/region-seams/review-validity-v2.json';old=read(oldreview);valid=read(oldvalid)
assert all(s['unchangedSinceNativeVisualReview'] and s['matchesCurrentRegionCrop'] for s in valid['segments'])
inherited=[]
for s in old['files']:
 p=b/'qa/region-seams'/s['file'];im=Image.open(p).convert('RGB');box=s['candidateCropBox'];actual=region.crop(box)
 assert sha(p)==s['sha256'] and ImageChops.difference(im,actual).getbbox() is None
 if s['file'].startswith('horizontal-'):new=e/'qa'/s['file'].replace('horizontal-','horizontal-y4096-')
 elif s['file'].startswith('vertical-'):new=e/'qa'/s['file']
 else:new=e/'qa/four-way-y4096.png'
 assert new.exists() and ImageChops.difference(Image.open(new).convert('RGB'),actual).getbbox() is None
 inherited.append({'file':str(new),'sha256':sha(new),'dimensions':list(im.size),'candidateCropBox':box,'status':'PASS','reviewMethod':'Exact native pixel match to prior visual PASS','priorReviewedFile':str(p),'priorReviewedSha256':sha(p),'currentCandidateCropMatches':True})
assert len(inherited)==17
new=[]
for y in [8192,9216,10240,11264]:
 p=e/'qa'/f'vertical-y{y}.png';box=[3968,y,4224,y+1024];assert ImageChops.difference(Image.open(p).convert('RGB'),region.crop(box)).getbbox() is None
 new.append({'file':str(p),'sha256':sha(p),'dimensions':[256,1024],'candidateCropBox':box,'status':'PASS','reviewMethod':'Root viewed original1:1 native pixels','finding':'Stone geometry, sand texture, lantern ornament, post and mesh continue without an actionable seam discontinuity.'})
p=e/'qa/four-way-y8192.png';box=[3584,7680,4608,8704];assert ImageChops.difference(Image.open(p).convert('RGB'),region.crop(box)).getbbox() is None
new.append({'file':str(p),'sha256':sha(p),'dimensions':[1024,1024],'candidateCropBox':box,'status':'PASS','reviewMethod':'Root viewed original1:1 native pixels','finding':'Mesh, beige rim ropes and post align across four-way intersection; no doubled outline or hard tonal cut.'})
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'candidate':m['regionCandidate']['file'],'candidateSha256':sha(m['regionCandidate']['file']),'status':'PASS_ROOT_SUBSET','freshNativeReviewCount':5,'inheritedExactNativeReviewCount':17,'freshReviews':new,'inheritedReviews':inherited,'priorVisualReview':{'file':str(oldreview),'sha256':sha(oldreview)},'priorReviewValidity':{'file':str(oldvalid),'sha256':sha(oldvalid)},'compositionPreview':{'file':m['preview'],'sha256':sha(m['preview']),'review':'PASS for overall scene composition and consistent palette; preview was not used for native pixel acceptance.'},'blockingFindings':[],'remainingRegionReview':'Eight horizontal crops at region y8192 reviewed independently by resume_audit.'}
write(e/'root-region-subset-review.json',out);print(json.dumps({'status':out['status'],'fresh':len(new),'inherited':len(inherited)}))
