"""Save a new independent visual report only; never changes any art or existing review."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
CROP_RECORD=ROOT/'qa'/'final-candidate-20261012'/'crops.json'
TARGET=OUT/'final-independent-review-20261012.json'
CANDIDATE=ROOT/'candidate'/'r07_c06-candidate-hard-2e59491c741a.png'
EXPECTED_CANDIDATE_SHA='3cd3e84fb8cef071dbebd26c9147aea729dae71e912d51dbd373cbe0328293b4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

# Each source image below was displayed individually using view_image(detail='original').
# These notes describe the whole displayed crop, including the interior anchor transition.
notes={
 'v-r1-c1':('passed','Grout crossings align at the center seam and continue through the visible paving. Fine surface pattern variation remains.',[]),
 'v-r1-c2':('passed','Diagonal grout and bevels continue through the center join. Fine lattice differs near the anchor edge, with no disconnected groove visible in this crop.',[]),
 'v-r1-c3':('passed','Diagonal joints align and remain continuous across the center join in the visible strip.',[]),
 'v-r2-c1':('needs_repair','The center seam aligns, but grout tips and an abrupt rectangular surface cutoff remain at crop x≈243, 115 pixels east of the join; middle and lower lines do not continue into the fill.',['B02']),
 'v-r2-c2':('passed','Large slab grout and surface lattice continue across the center join without a visible break.',[]),
 'v-r2-c3':('needs_repair','The center seam aligns, but the right-edge anchor-to-fill boundary at crop x≈243 has a hard texture cutoff and dangling diagonal tips around crop y≈445 and 915.',['B03']),
 'v-r3-c1':('passed','Diagonal grout remains connected across the center seam. The visible lattice and honeycomb surface variation does not introduce a disconnected joint.',[]),
 'v-r3-c2':('passed','Center grout joins remain aligned; lattice and honeycomb slabs continue without a visible disconnected groove.',[]),
 'v-r3-c3':('needs_repair','At crop x≈243, 115 pixels inside the right patch, the fill has an abrupt rectangular texture edge and diagonal joints change or stop at that edge, especially near the lower intersection.',['B04']),
 'v-r4-c1':('passed','Grout and bevels connect across the center seam; honeycomb and lattice slab surfaces remain coherent within the visible crop.',[]),
 'v-r4-c2':('passed','Diagonal grout remains continuous across the center seam; no orphaned tip is visible in this strip.',[]),
 'v-r4-c3':('needs_repair','The center join aligns, but the anchor-to-fill cutoff near crop x≈243 is visible as a vertical material edge with changes in diagonal joint continuation.',['B05']),
 'h-r1-c1':('needs_repair','Center grout is aligned, but at crop y≈243, 115 pixels into the lower patch, disconnected diagonal strokes enter the fill near crop x≈16 and 166 after a horizontal anchor cutoff.',['B01']),
 'h-r1-c2':('passed','Grout, the narrow cream divider, and its border lines continue across the horizontal center join in the displayed crop.',[]),
 'h-r1-c3':('passed','Blue walkway paving, both cream trims, and adjacent diagonal slab joints continue across the horizontal join.',[]),
 'h-r1-c4':('passed','The displayed horizontal join preserves grout continuity and the octagonal lattice. Surface variation is visible; this local pass does not resolve the west transition shown in v-r2-c3.',[]),
 'h-r2-c1':('passed','Center grout and bevels connect across the row-two/row-three join; no disconnected tip is visible in the displayed area.',[]),
 'h-r2-c2':('needs_repair','At crop x≈115 in the upper half, the row-two patch has an abrupt vertical anchor cutoff with a diagonal line ending near crop y≈15 and an unmatched intersection lower down. The horizontal center divider is continuous.',['B02']),
 'h-r2-c3':('passed','Blue paving, cream trims, and diagonal slab joints continue through the horizontal center join.',[]),
 'h-r2-c4':('needs_repair','At crop x≈115 in the upper half, the row-two west-anchor field changes abruptly to the paper-and-walkway fill; a diagonal branch starts or stops at the cutoff.',['B03']),
 'h-r3-c1':('passed','Grout intersections and honeycomb/lattice slab surfaces continue through the horizontal center join without a visible joint break.',[]),
 'h-r3-c2':('passed','The cream divider, border lines, and adjacent slab grout remain continuous through the horizontal center join.',[]),
 'h-r3-c3':('passed','Blue walkway grout and cream trims continue through the horizontal center join. A small contour variation at the left trim does not disconnect the joint.',[]),
 'h-r3-c4':('passed','Thin square paving joints and the large diagonal slab edges cross the center join continuously in this crop; it does not resolve the separate west-anchor transition flagged in vertical crops.',[]),
 'j-r1-c1':('passed','The four-way seam area preserves connected slab grout and bevels; no isolated tip is visible within the displayed junction.',[]),
 'j-r1-c2':('passed','Slab grout meets the cream trim coherently and the four-way seam area has no visible gap.',[]),
 'j-r1-c3':('needs_repair','The center junction aligns, but the lower-right area has a straight rectangular surface-pattern cutoff near crop x≈307, where the row-two column-four anchor changes to fill.',['B03']),
 'j-r2-c1':('needs_repair','A diagonal grout line ends inside a slab near crop (307,77), beside a straight anchor cutoff; the neighboring intersection below also changes across that cutoff.',['B02']),
 'j-r2-c2':('passed','The four-way seam area preserves diagonal slab grout and its join to the cream walkway trim.',[]),
 'j-r2-c3':('needs_repair','A strong vertical anchor-to-fill edge near crop x≈307 cuts across surface texture and paper/walkway geometry. A diagonal grout tail ends at the edge above the main intersection.',['B03']),
 'j-r3-c1':('passed','The junction has connected slab edges and coherent honeycomb/lattice surfaces, with no visible dangling grout.',[]),
 'j-r3-c2':('passed','The slab grid joins the cream walkway trim continuously through the junction; small border contour variation remains.',[]),
 'j-r3-c3':('needs_repair','The lower-right quadrant shows an abrupt rectangular texture/material change near crop (307,307), at the column-four anchor-to-fill transition, with altered grout continuation.',['B05']),
 'north-c1':('passed','Diagonal grout and bevels continue across the actual north seam; the displayed mosaic paving remains coherent.',[]),
 'north-c2':('passed','The actual north seam preserves grout and cream-divider continuity. A change in fine surface lattice is visible near crop x≈115, but no disconnected groove is visible in this north crop.',[]),
 'north-c3':('passed','Blue walkway paving, cream trims, and adjacent slab grout continue across the actual north seam.',[]),
 'north-c4':('passed','The actual north seam preserves connected diagonal slab grout and octagonal lattice surfaces.',[]),
 'west-r1':('passed','Diagonal slab grout and bevels continue across the actual west seam; no disconnected tip is visible.',[]),
 'west-r2':('needs_repair','The actual vertical seam mostly aligns, but an interior horizontal anchor-to-fill cutoff at crop y≈115 leaves a diagonal stroke beginning near crop (144,115), with no matching continuation above it.',['B01']),
 'west-r3':('needs_repair','A diagonal grout branch in the left neighbor ends at the actual west seam near crop (128,553), while the right-side fill begins a displaced branch below it. The join is not continuous.',['B06']),
 'west-r4':('passed','Grout and bevels connect across the actual west seam; the honeycomb and lattice slab surfaces remain coherent in the displayed strip.',[]),
}
blockers=[
 {'id':'B01','kind':'interior-anchor-to-fill','sourcePatch':'s02_01_resume01','tileCoordinate':'y≈1139, 115 pixels south of the row-two north core boundary','finding':'Horizontal copied anchor ends before the new diagonal grout strokes begin; disconnected strokes are visible at the fill transition.','crops':['h-r1-c1','west-r2']},
 {'id':'B02','kind':'interior-anchor-to-fill','sourcePatch':'s02_02_resume02','tileCoordinate':'x≈1139, 115 pixels east of the column-two west core boundary; row two','finding':'Dangling grout and a straight texture cutoff remain inside the source, even though the actual core join aligns.','crops':['v-r2-c1','h-r2-c2','j-r2-c1']},
 {'id':'B03','kind':'interior-anchor-to-fill','sourcePatch':'s02_04_resume02','tileCoordinate':'x≈3187, 115 pixels east of the column-four west core boundary; row two','finding':'Dangling diagonal grout and rectangular surface/object transitions remain at the copied anchor edge.','crops':['v-r2-c3','h-r2-c4','j-r1-c3','j-r2-c3']},
 {'id':'B04','kind':'interior-anchor-to-fill','sourcePatch':'s03_04_resume01','tileCoordinate':'x≈3187, 115 pixels east of the column-four west core boundary; row three','finding':'A rectangular material/texture boundary and changed grout continuation are visible inside the patch.','crops':['v-r3-c3']},
 {'id':'B05','kind':'interior-anchor-to-fill','sourcePatch':'s04_04_resume01','tileCoordinate':'x≈3187, 115 pixels east of the column-four west core boundary; row four','finding':'The copied anchor meets the generated fill at a visible rectangular texture edge with altered diagonal joint continuation.','crops':['v-r4-c3','j-r3-c3']},
 {'id':'B06','kind':'external-west-core-seam','sourcePatch':'s03_01_resume01 and actual r07_c05 neighbor','tileCoordinate':'x=0, row three; local crop y≈553','finding':'A west-neighbor diagonal grout branch terminates at the core seam and does not connect to the displaced right-side branch.','crops':['west-r3']},
]
rec=json.loads(CROP_RECORD.read_text(encoding='utf-8-sig'))
assert len(rec['entries'])==41 and len(notes)==41
assert {e['name'] for e in rec['entries']}==set(notes)
assert sha(CANDIDATE)==EXPECTED_CANDIDATE_SHA
entries=[]
for e in rec['entries']:
    p=Path(e['file'])
    assert sha(p)==e['sha256'],e['name']
    with Image.open(p) as im:size=list(im.size)
    verdict,note,groups=notes[e['name']]
    entries.append({**e,'size':size,'actuallyViewed':True,'viewMethod':"view_image detail='original'; full individual crop displayed",'nativePixelScale':1,'verdict':verdict,'findings':[note],'blockerGroups':groups,'formalAccepted':False})
counts={k:sum(e['verdict']==k for e in entries) for k in ('passed','needs_repair')}
report={
 'schemaVersion':1,'tile':'r07_c06','createdAt':datetime.now(timezone.utc).isoformat(),
 'reviewType':'independent native-scale visual review','status':'needs_repair','formalAccepted':False,
 'candidate':{'file':str(CANDIDATE),'sha256':sha(CANDIDATE),'sha256MatchesParentProvidedValue':True},
 'qaArt':rec['art'],'cropRecord':{'file':str(CROP_RECORD),'sha256':sha(CROP_RECORD)},
 'candidatePixelBinding':'To be proven separately by parent; this review visually assesses the supplied crops and verifies each crop hash against crops.json.',
 'sourceRefs':rec['sources'],'neighbors':rec['neighbors'],
 'viewedCount':len(entries),'expectedCount':41,'internalViewedCount':sum(e['category'].startswith('internal-') for e in entries),'northViewedCount':4,'westViewedCount':4,
 'verdictCounts':counts,'blockingCropCount':counts['needs_repair'],'deduplicatedBlockerGroupCount':len(blockers),
 'entries':entries,'blockers':blockers,
 'limits':['A passed verdict applies only to the displayed crop, including its visible interior transition; it is not whole-source or formal acceptance.','East and south external neighbors are outside this requested review.','The 256-pixel seam strips show 13 pixels beyond the 115-pixel interior transition; an abrupt edge or disconnected groove visible there is flagged, while farther interior areas are not implied to pass.'],
 'writes':'Only this new report and its script in the independent review directory. No art, existing QA, selection, progress, Git or Unity edits.',
}
with TARGET.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'file':str(TARGET),'viewedCount':len(entries),'verdictCounts':counts,'deduplicatedBlockerGroupCount':len(blockers),'formalAccepted':False},indent=2))
