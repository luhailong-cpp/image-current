from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image, ImageChops

base = Path(__file__).resolve().parent
manifest = json.loads((base / 'delivery/candidate-manifest.json').read_text(encoding='utf-8-sig'))
region_path = Path(manifest['regionCandidate']['file'])
region = Image.open(region_path).convert('RGB')
checks = []
for source in manifest['sources']:
    path = Path(source['file'])
    tile = Image.open(path).convert('RGB')
    x, y = source['regionPasteAt']
    measured_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    exact = ImageChops.difference(tile, region.crop((x, y, x+4096, y+4096))).getbbox() is None
    checks.append({'tile': source['tile'], 'dimensionsCorrect': tile.size == (4096,4096), 'shaMatches': measured_sha == source['sha256'], 'regionPixelsExactlyEqual': exact})
sha = hashlib.sha256(region_path.read_bytes()).hexdigest()
report = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'region': str(region_path), 'dimensions': list(region.size), 'sha256': sha, 'shaMatchesManifest': sha == manifest['regionCandidate']['sha256'], 'tileChecks': checks, 'finalPixelsResized': False, 'verificationScope': 'Region assembly dimensions, hashes and pixel equality; visual seam review is recorded separately.', 'formalAcceptanceGranted': False}
report['pass'] = region.size == (8192,8192) and report['shaMatchesManifest'] and all(all(v for k,v in c.items() if k != 'tile') for c in checks)
review=json.loads((base/'qa/region-seams/findings.json').read_text(encoding='utf-8-sig'))
seams=[]
for item in review['files']:
    path=base/'qa/region-seams'/item['file']
    matches=hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
    crop=Image.open(path).convert('RGB')
    equal=ImageChops.difference(crop,region.crop(tuple(item['candidateCropBox']))).getbbox() is None
    seams.append({'file':item['file'],'unchangedSinceNativeVisualReview':matches,'matchesCurrentRegionCrop':equal})
validity={'verifiedAt':datetime.now(timezone.utc).isoformat(),'currentCandidate':str(region_path),'currentSha256':sha,'priorVisualReview':str(base/'qa/region-seams/findings.json'),'segments':seams,'reviewStillApplicable':len(seams)==17 and all(v['unchangedSinceNativeVisualReview'] and v['matchesCurrentRegionCrop'] for v in seams),'formalAcceptanceGranted':False}
(base/'qa/region-seams/review-validity-v2.json').write_text(json.dumps(validity,indent=2)+'\n',encoding='utf-8')
report['interTileSeamReviewStillApplicable']=validity['reviewStillApplicable']
report['pass']=report['pass'] and validity['reviewStillApplicable']
(base/'qa/region-assembly-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass': report['pass'], 'dimensions':report['dimensions'], 'sha256':sha}))
