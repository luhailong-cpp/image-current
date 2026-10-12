"""Apply clarified model preference to current zone state; preserve artwork and historical policy snapshots."""
from pathlib import Path
import json
import coast_work as c
B=Path(__file__).resolve().parent
rules=Path('D:/work/image/AGENTS.md')
preference=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')
assert '允许继续使用现有内置绘图工具' in rules.read_text(encoding='utf-8-sig')
assert 'explicitly allows GPT Image 2.0' in preference.read_text(encoding='utf-8-sig')
progress=c.read(B/'progress.json')
assert progress['productionComplete'] and progress['coveredCoreCount']==64 and progress['remainingCoreCount']==0
stamp=c.now()
record=B/'image-model-preference-correction-20261013.json'
assert not record.exists(), 'Preserve existing clarification; create a new version for another update.'
updates={
 'imageModelPolicy':'Prefer GPT Image 2.5 through a free or existing included route; otherwise existing built-in GPT Image 2.0 is allowed.',
 'requestedExactImageModel':None,
 'preferredImageModel':'GPT Image 2.5',
 'allowedFallbackImageModel':'GPT Image 2.0',
 'generationAllowed':True,
 'newImageGenerationBlockedUntilVerifiedRequiredRoute':False,
 'newImageRepairGenerationBlockedUntilVerifiedRequiredRoute':False,
 'verifiedRequiredImageModelRouteAvailable':False,
 'currentBuiltinImageRouteUsableForNewImages':True,
 'imageRouteLimitation':'Actual built-in image model is not returned; this no longer pauses production.',
 'imageModelMetadataPolicy':'Record actual returned model metadata honestly; if not returned, unknown. Do not relabel images as 2.5 or 2.0.',
 'paidApiAllowed':False,'paidApiUsageAuthorized':False,
 'modelRequirementPausedMissingCoreCount':0,'modelRequirementPausedMissingCoordinates':[],
 'modelRequirementPausedNecessaryRepairCount':0,'modelRequirementPausedWork':[],
 'imageModelConstraintRecord':record.as_posix(),
 'imageModelConstraintRecordedAtUtc':stamp,
 'imageModelRequirementFile':preference.as_posix(),'imageModelRequirementSha256':c.sha(preference),
 'projectRulesFile':rules.as_posix(),'projectRulesSha256':c.sha(rules),
 'previousMandatory25PauseRevoked':True,
 'previousModelConstraintRecordsHistoricalOnly':True,
 'existingActualImageModel':'unknown',
 'updatedAtUtc':stamp}
clarification={
 'schemaVersion':1,'scope':'accelerated-northeast-coast','recordedAtUtc':stamp,
 'userClarification':'2.5免费就用2.5，不行就用回2.0',
 'supersedes':(B/'image-model-requirement-20261012.json').as_posix(),
 'historicalPolicyRecordPreserved':True,
 **updates,
 'productionComplete':True,'candidateTileCount':4,'internallyReviewedWholeTileCount':4,
 'coveredCoreCount':64,'remainingCoreCount':0,'pendingNecessaryRepairsCount':0,
 'artRegeneratedForPolicyChange':False,'generationCallsMadeForPolicyChange':0,
 'existingDeliveryPackageModified':False,'gitOperationsPerformed':False}
c.write(record,clarification)
for name in ['progress.json','production-resume-20261012.json','current-selection-20261012.json']:
    p=c.read(B/name);p.update(updates);c.write(B/name,p)
print(json.dumps({'record':record.as_posix(),'generationAllowed':True,'mandatory25PauseRevoked':True,
 'candidateTiles':4,'internallyReviewedTiles':4,'remainingCores':0,'pendingNecessaryRepairs':0,
 'existingArtworkAndDeliveryPreserved':True},ensure_ascii=False))

