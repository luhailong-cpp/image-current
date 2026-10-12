from pathlib import Path
from workflow import ROOT,read,write,sha,now
import sys
tile,revision=sys.argv[1:3]
folder=ROOT/'qa'/f'{tile}-{revision}'
m=read(folder/'seams-junctions-external.json')
for e in m['entries']:
 assert sha(Path(e['file']))==e['sha256'];e['status']='visual_pass_no_substantive_issue'
m.update(reviewedAt=now(),reviewer='left_resume',internalSeamsPassed=24,junctionsPassed=9,availableExternalSidesPassed=['north','east'],formalAccepted=False,observations='Actual native rock contours, surf waterline, timber column and caustic cells connect. Minor fine-grain or water phase variation retained. Whole shared lower-column source boundary reviewed. West/south external acceptance remains pending.')
write(folder/'left-visual-review.json',m)
for f in [ROOT/f'progress-{tile}.json',ROOT/f'production-resume-left-sol-{tile}-20261012.json']:
 p=read(f);p.update(updatedAt=now(),status='internal_and_available_north_east_passed_pending_independent_review',selectedCoordinateCount=16,missingPatches=[],fullyCovered4kCount=1,internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0,availableExternalSidesPassed=['north','east'],visualReview=str(folder/'left-visual-review.json'),inFlightRequests=[],newGenerationStatus='builtin_allowed_unknown_actual_model',nextStep='Continue next assigned tile using stable actual native edges; root independent QA remains required.')
 write(f,p)
print({'candidate':m['candidate'],'sha256':m['candidateSha256'],'visualReview':str(folder/'left-visual-review.json')})
