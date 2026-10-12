"""Bind the two original-scale visual reviews to the proven hard candidate."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
QA = HERE / 'qa/final-candidate-20261012'
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data):
    p = Path(p)
    if p.exists():
        raise FileExistsError(p)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

review = read(QA / 'crops.json')
primary = read(QA / 'primary-verdicts.json')
independent_path = HERE / 'qa/independent-transition-review-20261012/final-independent-review-20261012.json'
independent = read(independent_path)
second = {entry['name']:entry for entry in independent['entries']}
proof_path = QA / 'candidate-pixel-proof.json'
proof = read(proof_path)
assert len(primary) == len(second) == len(review['entries']) == 41
for entry in review['entries']:
    name = entry['name']
    assert sha(entry['file']) == entry['sha256'] == second[name]['sha256']
    assert second[name]['actuallyViewed'] is True
    entry.update(actuallyViewed=True,primaryReviewerVerdict=primary[name][0],
                 independentReviewerVerdict=second[name]['verdict'],findings=[primary[name][1]])
    entry['verdict'] = 'needs_repair' if 'needs_repair' in [primary[name][0],second[name]['verdict']] else 'passed'
    entry['independentFindings'] = second[name]['findings']
    entry['reviewersDiffer'] = primary[name][0] != second[name]['verdict']
    entry['blockerGroups'] = second[name].get('blockerGroups',[])
review.update(reviewedAt=datetime.now(timezone.utc).isoformat(),status='needs_repair',
              actuallyViewedCropCount=41,internalViewedCropCount=33,externalViewedCropCount=8,
              passedCropCount=sum(e['verdict']=='passed' for e in review['entries']),
              needsRepairCropCount=sum(e['verdict']=='needs_repair' for e in review['entries']),
              candidate=proof['candidate'],pixelProof=dict(file=str(proof_path),sha256=sha(proof_path)),
              independentReview=dict(file=str(independent_path),sha256=sha(independent_path),
                                     all41ActuallyViewed=True,reportedNeedsRepairCropCount=independent['blockingCropCount']),
              coverageComplete=True,sourceCount=16,formalAccepted=False,pendingExternalSides=['east','south'],
              priorReviewsPreserved=True,
              verdictMeaning='Passed means a local crop only. Any outstanding blocker prevents tile acceptance. '
                             'All anchor transitions in the crops were inspected. Differing reviewer judgments '
                             'are conservatively retained for repair. No zone or global progress is changed.',
              deduplicatedBlockerGroups=independent['blockers'])
out = QA / 'review.json'
write(out,review)
native_files = list((HERE / 'native').glob('*.png'))
checkpoint = dict(tile=HERE.name,createdAt=review['reviewedAt'],status='coverage-complete-needs-seam-repair',
                  selectedNativeSourceCount=16,preservedNativePngCount=len(native_files),
                  selectedSources=proof['selectedSources'],candidate=proof['candidate'],
                  assemblyManifest=proof['assemblyManifest'],
                  pixelProof=dict(file=str(proof_path),sha256=sha(proof_path)),
                  visualReview=dict(file=str(out),sha256=sha(out),actuallyViewedCropCount=41,
                                    passedCropCount=review['passedCropCount'],needsRepairCropCount=review['needsRepairCropCount']),
                  independentReview=review['independentReview'],neighbors=review['neighbors'],
                  allSelectedNativeOriginals1254Opaque=True,originalHostCopiesByteIdentical=True,
                  sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,
                  coverageComplete=True,formalAccepted=False,progressUpdated=False,
                  actualModel=None,actualQuality=None,
                  notes=['All originals, rejected repairs, unsubmitted requests and prior freezes preserved.',
                         'Candidate is 4096x4096 exact core translation of selected sources.',
                         'Current north and west neighbors inspected; east and south await later neighbors.',
                         'Configuration wishes are preserved as metadata; built-in backend model and quality are unknown.'])
checkpoint_path = HERE / 'continuation-complete-candidate-20261012.json'
write(checkpoint_path,checkpoint)
print(json.dumps(dict(review=str(out),reviewSha256=sha(out),checkpoint=str(checkpoint_path),checkpointSha256=sha(checkpoint_path),
                      selectedSources=16,preservedNativePngCount=len(native_files),viewed=41,
                      passed=review['passedCropCount'],needsRepair=review['needsRepairCropCount'],formalAccepted=False),indent=2))
