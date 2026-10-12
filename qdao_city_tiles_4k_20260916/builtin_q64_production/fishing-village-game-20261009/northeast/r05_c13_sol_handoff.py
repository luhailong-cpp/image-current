"""Owned r05_c13 review/provenance handoff; no source art edits."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p).replace('\\','/'),'sha256':sha(p)}
def write(p,d):
    assert not p.exists()
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qa=Z/'qa'/'r05_c13-sol-v3'; m=json.loads((qa/'manifest.json').read_text())
old=json.loads((Z/'qa'/'r05_c13-sol-v2'/'manifest.json').read_text())
oldmap={q['name']:q for q in old['qa']}
changed=[q['name'] for q in m['qa'] if q['rawRGBPixelSha256']!=oldmap[q['name']]['rawRGBPixelSha256']]
assert len(changed)==9
for q in m['qa']:
    p=Path(q['path']);assert sha(p)==q['sha256']
    assert hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest()==q['rawRGBPixelSha256']
styles=['donghai-natural-stone-clear-routes-v10.png','donghai-natural-stone-detail-v1.png','mail-daoist-style.jpg']
proof=[]
for q in m['nativeCoreContributions']:
    p=Path(q['path']);g=p.with_name(p.name+'.generation.json');d=json.loads(g.read_text(encoding='utf-8-sig'))
    assert sha(p)==q['sha256']==d['sha256']
    assert Image.open(p).size==(1254,1254)
    assert d['actualModel'] is None and d['actualQuality'] is None and d['route']=='builtin'
    names=[Path(r['path']).name for r in d['references']]
    assert all(s in names for s in styles)
    for r in d['references']:assert sha(r['path'])==r['sha256']
    for k in ['prompt','receipt','source']:assert sha(d[k]['path'])==d[k]['sha256']
    proof.append({'patch':q['patchId'],'native':ref(p),'generationMetadata':ref(g),'prompt':d['prompt'],'receipt':d['receipt'],'hostSource':d['source'],'threeStyleReferencesVerified':True,'actualModel':None,'actualQuality':None})
write(qa/'central-sol-provenance-validation.json',{'tile':'r05_c13','createdAtUtc':datetime.now(timezone.utc).isoformat(),'selected16':proof,'checksPassed':True,'nativeDimensions':[1254,1254],'candidateDimensions':[4096,4096],'finalNative4KGenerationClaim':False,'allSourceCopiesByteForByte':True,'all16SavedCorePixelsEqualNativeSource':m['all16SavedCorePixelsEqualNativeSource']})
review={'tile':'r05_c13','candidate':m['tile'],'reviewer':'central_sol','createdAtUtc':datetime.now(timezone.utc).isoformat(),'verdict':'internal_native_main_geometry_pass','formalAccepted':False,'all49NativeQaCoveredByViewedOrExactUnchanged':True,'coverageChain':[{'version':'sol-v1','directNativeViews':49},{'version':'sol-v2','directChangedNativeViews':12,'identicalToPrior':37},{'version':'sol-v3','directChangedNativeViews':9,'identicalToPrior':40}],'directCurrentNativeViews':changed,'items':[dict(q,verdict='main_geometry_pass',reviewMethod='direct native original view' if q['name'] in changed else 'byte-identical previously viewed native QA') for q in m['qa']],'resolvedFindings':['p32/p42 internal x230 rectangular border replaced by curved cobalt gutter and diagonal timber overlap.','p32-v4 southern circular tile-end shift repaired with p32-v5 against p42-v2.'],'minorObservations':['Painted material microtexture and caustic detail vary slightly across some boundaries; no major geometry step found.','p43-v5 gold-cap small curl design differs slightly from historical lower anchor, but broad capital, column, hanger and lantern connect.'],'south4NativeSegmentsViewed':[ref(Z/'qa'/f'{p}-exact_native_bottom_230px.png') for p in ['r05_c13_p41-v3','r05_c13_p42-v2','r05_c13_p43-v5','r05_c13_p44-v1']],'southVerdict':'main_geometry_pass','eastIndependentEvidence':'east_sol reported4west segments plus3westjunctions and southwest corner passed against current c13 east sources; r05_c14-v4 QA saved','westIndependentEvidence':'root reports c12 last column seams against pinned c13 west sources passed','pending':['root independent c13 audit','north r04_c13 native neighbor not yet complete; no formal acceptance until boundary QA']}
write(qa/'central-sol-internal-review.json',review)
sel=json.loads((Z/'records'/'r05_c13.selection-sol-v3.json').read_text())
handoff={'schemaVersion':1,'tile':'r05_c13','owner':'central_sol','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'stable_proposed_candidate_internal_native_qa_pass_pending_independent_review_and_north_neighbor','formalAccepted':False,'candidate':m['tile'],'candidateDimensions':[4096,4096],'selectedCoreCoordinates':16,'nativeCoreContributions':m['nativeCoreContributions'],'selection':ref(Z/'records'/'r05_c13.selection-sol-v3.json'),'ownedWorkingSelection':ref(Z/'records'/'r05_c13.selection-sol-proposed-20261012.json'),'nativeQaManifest':ref(qa/'manifest.json'),'selfReview':ref(qa/'central-sol-internal-review.json'),'provenanceValidation':ref(qa/'central-sol-provenance-validation.json'),'all49InternalQaPassed':True,'availableSouth4NativeSegmentsPassed':True,'actualModel':None,'actualQuality':None,'route':'builtin','paidApiUsed':False,'networkPermissionRevokedInThisContinuation':False,'native4KGenerationClaim':False,'operations':['integer core crop115,115,1139,1139','opaque integer paste'],'all16CorePixelsEqualSource':True,'preservation':'All versions and successful host outputs retained; shared progress/index/helpers/config/historical freeze/stable/audit/Git/Unity untouched.','pending':['independent root review','north neighbor r04_c13 and its west/east joining reviews']}
write(Z/'records'/'r05_c13.sol-stable-handoff-20261012.json',handoff)
print(json.dumps({'candidate':m['tile'],'handoff':str(Z/'records'/'r05_c13.sol-stable-handoff-20261012.json'),'provenance16Passed':True,'internal49Passed':True}))
