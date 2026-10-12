from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,shutil
T=Path(__file__).resolve().parent;Q=T/'qa/checkpoint-20261013-v1';NOW=datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=T/'selected-patches-before-recovered-20261013-v1.json';assert not old.exists();shutil.copy2(T/'selected-patches.json',old)
sel=read(T/'selected-patches-recovered-candidate-20261013-v1.json')
sel.update(status='partial_native_candidate_generation_paused_GPT_Image_2_5_required',internalReady=False,formalAccepted=False,updatedAt=NOW,geometryReview='Available one internal lantern join and two south joins usable; whole tile incomplete',materialReview='Daylight painterly material usable with visible paving color/texture difference; final equalization pending',recoveredPatch='p42-v2',recoveredReceiptCaveat='Original exec cell148 response unavailable; existing disk file visually and temporally associated; actual model unknown, not relabelled2.5',modelRequirement='GPT Image 2.5',modelRequirementVerified=False,nextGenerationAllowed=False,checkpointQa=str(Q/'manifest.json'))
write(T/'selected-patches-checkpoint-20261013-v1.json',sel);write(T/'selected-patches.json',sel)
m=read(Q/'manifest.json')
for e in m['evidence']:
    name=Path(e['file']).stem
    review=dict(reviewedAt=NOW,method='view_image at native100percent',geometry='usable',structuralBlockers=[],materials='usable_candidate_color_texture_pending',colorOnlyRisks=['Native paving variation across south seam; no final tile color equalization performed'] if 'south' in name else ['Small lantern paper/red material source variation; no broken silhouette'],candidateUsable=True,formalAccepted=False,wholeTileReady=False)
    e['visualReview']=review;d=read(str(e['file'])+'.derivation.json');d['visualReview']=review;write(str(e['file'])+'.derivation.json',d)
m.update(selectedCount=2,reviewedCount=4,allAvailableManualQaViewed=True,internalReady=False,formalAccepted=False,status='partial geometry usable; material/color pending; no complete4k tile',generationPausedReason='Current builtin route cannot independently verify GPT Image2.5')
write(Q/'manifest.json',m)
for v,reason in [('v3','Retained intermediate shaft repair; v4 closes extraneous left13px extension and better preserves lower guide contours.')]:
    write(T/f'native/p41-{v}.rejection.json',dict(status='superseded_not_selected',reason=reason,selected=False,updatedAt=NOW))
progress=read(T/'progress.json');progress.update(status=sel['status'],updatedAt=NOW,selectedPatchCount=2,usableNativeCount=2,generatedNativeCount=6,exactCoreCoverage=2097152,coverageFraction=.125,remainingPositions=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in sel['patches']],internalReady=False,formalAccepted=False,complete4kCount=0,internalReady4kCount=0,formalAcceptedCount=0,geometryReview=sel['geometryReview'],materialReview=sel['materialReview'],modelRequirementVerified=False,actualModel=None,actualQuality=None,inFlight=dict(activeRequestsKnown=0,lastRequest='p42-v2',execCell='148',state='cell not found; associated finished file recovered from disk; original tool result unavailable',unarchivedReturnedImagesKnown=0),nextStep='No new generation until verifiable GPT Image2.5 route;14 native positions plus final33 internal QA and color work remain')
progress['selectedSources']=[dict(patch=k,file=str(T/p),sha256=sha(T/p),nativeSize=list(Image.open(T/p).size),generationRecord=str(T/p)+'.generation.json',corePixels=1048576) for k,p in sel['patches'].items()]
write(T/'progress.json',progress);write(T/'progress-checkpoint-20261013-v1.json',progress)
allnative=[dict(file=str(p),sha256=sha(p),dimensions=list(Image.open(p).size),selected=p.relative_to(T).as_posix() in sel['patches'].values(),record=str(p)+'.generation.json',actualModel=None,actualQuality=None) for p in sorted((T/'native').glob('*.png'))]
checkpoint=dict(createdAt=NOW,tile='r08_c09',selected=progress['selectedSources'],selectedCount=2,allNativeCandidates=allnative,nativeCandidateCount=6,missingCount=14,missingPatches=progress['remainingPositions'],selectedManifest=str(T/'selected-patches.json'),selectedManifestSha256=sha(T/'selected-patches.json'),geometryReview=sel['geometryReview'],materialReview=sel['materialReview'],qa=str(Q/'manifest.json'),qaSha256=sha(Q/'manifest.json'),inFlight=progress['inFlight'],generationPaused=True,pauseAuthority=[dict(file='D:/work/image/AGENTS.md',sha256=sha('D:/work/image/AGENTS.md')),dict(file='D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md',sha256=sha('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md'))],pauseReason='No independently verifiable GPT Image2.5 selector or returned actual-model metadata in available builtin route; no further generation calls allowed',actualModel=None,actualQuality=None,requestedFutureModel='GPT Image2.5',nextGenerationAllowed=False,noPaidApiUsed=True,formalAccepted=False,internalReady=False)
write(T/'local-handoff-20261013.json',checkpoint);write(T/'checkpoint-20261013-v1.json',checkpoint)
print(json.dumps(dict(checkpoint=str(T/'checkpoint-20261013-v1.json'),selected=2,candidates=6,missing=14,inFlightKnown=0),indent=2))
