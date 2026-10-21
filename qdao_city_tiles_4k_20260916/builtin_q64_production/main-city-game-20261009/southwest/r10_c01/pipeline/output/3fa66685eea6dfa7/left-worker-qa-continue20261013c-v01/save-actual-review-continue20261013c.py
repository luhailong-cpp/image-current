import json, hashlib
from pathlib import Path
from datetime import datetime,timezone
q=Path(__file__).resolve().parent
m=json.loads((q/'manifest.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
views=[dict(id='overview',file=m['overview']['file'],sha256=m['overview']['sha256'],qaOnly=True,viewed=True,detail='original')]
for p in m['panels']:
    assert sha(p['file'])==p['sha256']
    views.append(dict(id=p['id'],file=p['file'],sha256=p['sha256'],viewed=True,detail='original',nativeRegionCount=len(p['regions']),nativeRegionResampling=False))
issues=[
dict(id='stand-floor-front',patches=['p03_04','p04_04'],status='open',severity='blocking-internal',evidence=['internal-H3','internal-V3','overview'],finding='Visible vertical rectangular floor-tone front at p03_04 native x750; support left end is abruptly cut. Guidance-mask boundary remains visible in generated pixels.',action='AI repair floor tone and support end using current native neighbors; retain geometry and all versions.'),
dict(id='wall-shadow-steps',patches=['p01_03','p02_03','p02_04'],status='open',severity='blocking-internal',evidence=['internal-H1','internal-V3','internal-nine-corners'],finding='Grey wall shadow under lantern forms hard polygonal steps; lighting plane continuity needs repair.',action='Consolidated AI shadow/material repair preserving architecture.'),
dict(id='right-upper-beam',patches=['p01_04'],neighbor='r10_c02/p01_01',status='open',severity='blocking-external',evidence=['external-right-row1-only'],finding='Upper wooden member is visibly at different vertical extents in the two native overlap strips; current c01 side contains a dead-ended beam stub. Lower stone band and sill are near-aligned but do not establish passage.',action='Coordinate c01/c02 repair against approved forge geometry, then rebuild and inspect changed boundary only.'),
dict(id='lantern-fringe-length',patches=['p01_03'],status='open',severity='layout',finding='Remaining single tassel extends approximately to native y950 rather than coarse guide y820 after prior edit.',action='Defer further same-point looping; repair in consolidated layout pass.'),
dict(id='anvil-scoring',patches=['p02_04'],status='open',severity='finish',finding='Anvil surface develops cracks/scoring inconsistent with quiet approved finish.',action='AI surface repair preserving silhouette.'),
dict(id='bottom-left-floor-border',patches=['p04_01'],status='unconfirmed-layout',severity='propagation-hold',finding='Bluish L-shaped floor return near bottom-left needs support check against approved layout.',action='Do not use this portion as r11_c01 seed until checked/repaired.'),
dict(id='crate-box-corners',patches=['p02_02','p02_03','p03_02','p04_02'],status='open',severity='layout',finding='Minor approximately 50-100 pixel footprint/corner deviations from coarse guides remain.',action='Consolidated native layout review and necessary AI edit.'),
dict(id='floor-paper-detail',patches=['p04_02','p04_03','p04_04'],status='open',severity='finish-layout',finding='Interior red-paper clusters reduced/omitted and fine floor cellular texture is dense; some grout phase remains uncertain.',action='Review against approved fragment and quiet stone reference; repair necessary areas.'),
dict(id='top-overlap-tone',patches=['p01_01','p01_02','p01_03','p01_04'],status='open-review',severity='external',evidence=['external-top-cols-1-2','external-top-cols-3-4'],finding='Major wall seams, fringe, gold lantern collar and wooden upright correspond in native top overlaps; visible local tone/texture differences remain. Upper tile is provisional and not accepted.',action='Final external comparison after required repairs and confirmed upper sources.')]
r=dict(schemaVersion=1,createdAtUtc=datetime.now(timezone.utc).isoformat(),tile='r10_c01',worker='sw_left_continue_20261013c',coverage=dict(selectedNative=16,expected=16,nativePixels=[1254,1254],core=[4096,4096],context=[4326,4326],sourceResampling=False),assembly=m['assembly'],core=m['core'],context=m['context'],qaConstructionManifest=dict(file=str(q/'manifest.json'),sha256=sha(q/'manifest.json')),views=views,visualInspectionComplete=True,actualNativeRegionsViewed=43,internalNativeRegionsViewed=33,externalNativeRegionsViewed=10,externalCompleteness=m['externalCompleteness'],issues=issues,internalPassed=False,externalPassed=False,formalAccepted=False,acceptanceState='full-native-coverage; failed/open visual QA',sourceImagesModifiedByReview=False,gitMutated=False,nextProduction='Continue independent r10_c02 missing native patches; do not propagate unresolved r10_c01 bottom-left border.')
out=q/'worker-review-and-repair-queue.json'
assert not out.exists()
out.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(file=str(out),sha256=sha(out),views=len(views),nativeRegions=43,internalPassed=False,externalPassed=False,formalAccepted=False),ensure_ascii=False))

