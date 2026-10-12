"""Record the user's model constraint without generating or changing existing artwork."""
from pathlib import Path
import hashlib,json
import coast_work as c
B=Path(__file__).resolve().parent
requirement=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')
assert requirement.is_file()
p=c.read(B/'progress.json')
assert p['productionComplete'] is True and p['remainingCoreCount']==0
assert p['complete4096CandidateCount']==4 and p['internallyReviewedWholeTileCount']==4
stamp=c.now()
record_path=B/'image-model-requirement-20261012.json'
assert not record_path.exists(), 'Preserve existing model requirement record; create a later version if needed.'
restriction={
 'requestedExactImageModel':'GPT Image 2.5',
 'imageModelRequirementFile':requirement.as_posix(),
 'imageModelRequirementSha256':hashlib.sha256(requirement.read_bytes()).hexdigest(),
 'imageModelConstraintRecordedAtUtc':stamp,
 'generationAllowed':False,
 'newImageGenerationBlockedUntilVerifiedRequiredRoute':True,
 'newImageRepairGenerationBlockedUntilVerifiedRequiredRoute':True,
 'verifiedRequiredImageModelRouteAvailable':False,
 'currentBuiltinImageRouteUsableForNewImages':False,
 'imageRouteLimitation':'Current built-in entry point cannot explicitly select or independently verify GPT Image 2.5.',
 'paidApiAllowed':False,'paidApiUsageAuthorized':False,
 'modelRequirementPausedMissingCoreCount':0,
 'modelRequirementPausedMissingCoordinates':[],
 'modelRequirementPausedNecessaryRepairCount':0,
 'modelRequirementPausedWork':[],
 'existingImagesPreserved':True,'existingActualImageModel':'unknown',
 'noExistingImageRelabeledAsRequiredModel':True}
record={
 'schemaVersion':1,'recordedAtUtc':stamp,**restriction,
 'scope':'accelerated-northeast-coast',
 'existingProductionStatus':p['status'],
 'existingProductionComplete':True,'candidateTileCount':4,
 'internallyReviewedWholeTileCount':4,'coveredCoreCount':64,
 'remainingCoreCount':0,'pendingNecessaryRepairsCount':0,
 'generationCallsMadeForThisUpdate':0,'paidApiCallsMadeForThisUpdate':0,
 'existingArtOrDeliveryPackageModified':False,
 'pauseMeaning':'No outstanding image generation or repair exists in this completed region. This constraint blocks any future new image call; it is not evidence of completion for other regions.',
 'futureAction':'Read project model requirement on every computer. Resume new generation only through an explicitly selectable verified GPT Image 2.5 route with existing spending authorization respected.'}
c.write(record_path,record)
for name in ['progress.json','production-resume-20261012.json','current-selection-20261012.json']:
    current=c.read(B/name)
    current.update(restriction)
    current['imageModelConstraintRecord']=record_path.as_posix()
    current['updatedAtUtc']=stamp
    c.write(B/name,current)
print(json.dumps({'record':record_path.as_posix(),'newGenerationAllowed':False,
 'requiredModel':'GPT Image 2.5','pausedMissingCores':0,'pausedNecessaryRepairs':0,
 'existingProductionComplete':True,'existingDeliveryPreserved':True},ensure_ascii=False))

