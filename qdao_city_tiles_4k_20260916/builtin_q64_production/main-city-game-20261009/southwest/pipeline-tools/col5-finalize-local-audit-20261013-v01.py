from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
B=Path(__file__).resolve().parents[1];O=B/'pipeline-tools/col5-local-audit-20261013-v01'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(O/'manifest.json');by={r['id']:r for r in m['records']};now=datetime.now(timezone.utc).isoformat()
observations={
'r13_c05':{
'V1-1':'Horizontal groove crosses the join without a visible break. Broad cloudy/cellular stone and diagonal fine weave remain excessive.',
'V1-2':'Three horizontal grooves traverse the join; no hole at the narrow crop. Cloud-like pale stone patches remain.',
'V1-3':'Two horizontal grooves and canopy shadow remain connected; dense fine weave on lit and shaded ground.',
'V1-4':'Three horizontal grooves connect; quiet material target still fails.',
'V2-1':'Diagonal groove has an isolated pointed end inside paving near upper-left of crop; original layout semantics need checking before repair. Dense patterned faces.',
'V2-2':'Horizontal joint and canopy edge connect; lower leaves and mottled shadow have varied scale/tone.',
'V2-3':'Foliage and red/gold ornament overlap without a transparent hole. Large leaf sizes and bright yellow-green tips vary across the region.',
'V2-4':'Two-tier gray support beneath red/gold object is visible; its inferred topology remains unverified against approved layout. Diagonal ground joint crosses crop.',
'V3-1':'Tall red post and pale wall edge continue; rough cellular wall texture and dark/light lacquer differences persist.',
'V3-2':'Post/wall boundaries continue; abrupt different surface tones remain visible, especially at lower pink footing.',
'V3-3':'Pink foot has narrow dark vertical incision descending from its top bevel and a sharp triangular notch on front face just above foliage; reentrant shape is visible. Leaf scale varies.',
'V3-4':'Red/gold curved object and foliage overlap continuously; leaf sizes/stems and ground shadow detail differ.',
'H1-1':'Vertical ground joints cross boundary; left blue-gray vs cream division is sharp. Dense patterned paving.',
'H1-2':'T junction and vertical joint connect; material remains cloudy and crossed with fine diagonal strokes.',
'H1-3':'Diagonal groove crosses join with small bevel irregularities; lacquer post changes illumination in this area.',
'H1-4':'Wall/post edges connect; pale face has rough cloudy finish and dark lacquer-to-light lacquer variation.',
'H2-1':'Long diagonal changes into a horizontal segment at visible angular elbow before vertical junction. Layout semantics need checking; this is not certified correct topology.',
'H2-2':'Vertical/T ground grooves and nearby canopy silhouette connect; material remains patterned.',
'H2-3':'Dense canopy and pink post foot connect without a transparent gap; sizes of leaves vary substantially.',
'H2-4':'Pink lower wall profile has several abrupt stepped/reentrant cuts beneath the pale wall, including a dark narrow notch at the left. Needs smooth intended architectural edge restoration.',
'H3-1':'Red paper and vertical joint remain present; lower edge includes a horizontal joint and very patterned stone.',
'H3-2':'Vertical groove remains connected; lower horizontal joint and patterned ground require approved-layout semantics review.',
'H3-3':'Red curved body/gold markings remain continuous through seam; inferred ornament detail not layout-certified.',
'H3-4':'Canopy is fully painted; leaf sizes and brightness vary through join, no transparent hole.',
'X1-1':'T joints connect. Large patchy cloud/cellular stone fails quiet target.',
'X1-2':'Pale stone and cast canopy shadow transition without hole, dense patchy fine weave persists.',
'X1-3':'Post is continuous, but horizontal dark/light lacquer change visible near intersection; pale wall remains rough.',
'X2-1':'Two horizontal grooves and vertical junction connect; boxed slab geometry requires layout review, material fails.',
'X2-2':'Leaf cluster connects without missing pixels; canopy leaf scale varies.',
'X2-3':'Pink foot and wall form sharp inward notches and staggered pieces, corroborating V3-3/H2-4 geometry concern.',
'X3-1':'Horizontal groove crosses intersection, dense patterned stone remains.',
'X3-2':'Gray two-step pedestal is visible below red/gold upright; inferred support geometry remains unverified.',
'X3-3':'Curved red/gold trim and leaves overlap continuously; no cutout hole, material/leaf variation persists.'},
'r14_c05':{
'V1-1':'Three horizontal paving grooves and clipped red paper connect across join; dense fine pattern remains.',
'V1-2':'Red paper group and bottom horizontal seam connect; fine weave density differs.',
'V1-3':'Mostly one pale stone face, no transparent seam. Dense crosshatched/cellular texture remains.',
'V1-4':'Two diagonal groove branches meet a pointed dead end inside right part of the strip near its upper third; they fail to continue into left paving. Lower diagonal also present. Native geometry fails.',
'V2-1':'Descending diagonal remains connected; material is dense weave.',
'V2-2':'Rising diagonal and a T branch connect; topology still must match original paving, texture remains.',
'V2-3':'Descending diagonal has a visible small offset/break near upper quarter. Rising diagonal is split into two widely separated blunt-ended segments lower in crop. Native geometry fails.',
'V2-4':'No central junction hole; lower clipped diagonal appears. Dense weave/cellular ground persists.',
'V3-1':'Three clipped descending diagonals cross join; dense patterned material persists.',
'V3-2':'Diagonal X intersection is connected; groove widths/tonal finish differ.',
'V3-3':'Pale stone becomes noticeably smoother on right of join; clipped lower diagonal remains. Material transition needs correction.',
'V3-4':'Rising diagonal is interrupted by a broad pale gap near lower half, leaving two blunt ends. Top descending joint remains. Native geometry fails.',
'H1-1':'Red paper clusters and vertical line remain; fine texture becomes denser across ground.',
'H1-2':'Vertical groove crosses seam continuously; dense fine patterned stone remains.',
'H1-3':'Rising diagonal ends bluntly inside paving near crop x330, rather than continuing across horizontal row join. Native geometry fails. Right upper descending fragment retained.',
'H1-4':'Two descending diagonals and right paper group connect; ground pattern inconsistent.',
'H2-1':'Top red paper, vertical line and right T continue; dense weave remains.',
'H2-2':'Vertical/T and descending diagonal continue; fine stone weave density varies.',
'H2-3':'Rising diagonal is connected through row join; dense texture remains.',
'H2-4':'Descending diagonal and tiny upper-left clip connect; smoother new face differs from neighboring woven ground.',
'H3-1':'Vertical and descending diagonal continue; material remains densely patterned.',
'H3-2':'Vertical and rising diagonal cross row join; no hole. Weave texture remains.',
'H3-3':'Upper-right clipped diagonal continues; broad ground face is cloudy and woven.',
'H3-4':'Two clipped lower/upper corner diagonal fragments remain; density/tone differences persist.',
'X1-1':'Paper group remains present; stone tone/pattern variation visible around four-way patch region.',
'X1-2':'Rising line and T branch connect, but source paving topology not certified.',
'X1-3':'Two diagonal fragments connect; dense weave persists.',
'X2-1':'Horizontal joint traverses crop; ground pattern changes across region.',
'X2-2':'Descending diagonal contains the same small offset/break visible in V2-3, near lower-right of intersection crop. Native geometry fails.',
'X2-3':'X of two diagonals connects; dense stone pattern remains.',
'X3-1':'Most crop is woven pale stone; clipped bottom-right diagonal remains.',
'X3-2':'Rising diagonal terminates bluntly near upper-left/center of crop rather than continuing; corroborates displaced segments around V2-3.',
'X3-3':'Descending diagonal connects; cloudy/weave material remains.'}}
viewed=[];panel_views=[]
for tile,obs in observations.items():
    for name,note in obs.items():
        e=by[tile+'/'+name];viewed.append({**e,'actuallyViewed':True,'viewMethod':'view_image detail=original via unchanged exact-crop panels','observation':note,'formalAccepted':False})
    for kind in ['V','H','X']:
        for k in range(1,4):
            e=by[f'{tile}/{kind}{k}-panel'];panel_views.append({'file':e['file'],'sha256':e['sha256'],'pixels':e['pixels'],'viewImageDetail':'original','members':e['members']})
external_notes={
'chain/r12_c05--r13_c05-1':'Exact current r12v14 bottom versus r13 top: sharp horizontal brightness/material frontier at boundary, especially blue-gray left face; vertical grooves roughly align.',
'chain/r12_c05--r13_c05-2':'Sharp material frontier. Vertical paving groove visibly shifts laterally at boundary; descending blue/cream diagonal roughly continues at right.',
'chain/r12_c05--r13_c05-3':'Red post side profile changes abruptly at boundary with rectangular dark/light lacquer frontier; adjacent ground/wall below is much more patterned.',
'chain/r12_c05--r13_c05-4':'A projecting horizontal pale stone ledge appears below boundary on r13, although approved p01_04 coarse guide has a plain vertical wall. Clear topology failure plus rough gray vs warm wall mismatch.',
'chain/r13_c05--r14_c05-1':'Vertical ground line aligns approximately; horizontal material frontier and fine-pattern change visible. Horizontal groove near lower crop belongs to r14 interior, not evidence of boundary acceptance.',
'chain/r13_c05--r14_c05-2':'Vertical and descending diagonal groove positions broadly continue; definite sharp horizontal material/brightness frontier across tile boundary.',
'chain/r13_c05--r14_c05-3':'Descending diagonals continue broadly, but sharply different weave density across boundary remains.',
'chain/r13_c05--r14_c05-4':'Leaves/shadow present on both sides; their scale, leaf tips and blue-gray ground tone vary. No transparent gap, not accepted.',
'r13_c05/right-partial-row1':'Available top1024 only: invented pale horizontal ledge from r13 stops sharply at vertical boundary; right wall is warm and smooth, left wall rough pale gray. Red crossbeam remains painted with profile/tone variation. Remaining3072 pixels unavailable.'}
for name,note in external_notes.items():
    e=by[name];viewed.append({**e,'actuallyViewed':True,'viewMethod':'view_image detail=original','observation':note,'formalAccepted':False})
for name in ['chain/r12_c05--r13_c05-panel','chain/r13_c05--r14_c05-panel']:
    e=by[name];panel_views.append({'file':e['file'],'sha256':e['sha256'],'pixels':e['pixels'],'viewImageDetail':'original','members':e['members']})
guide_views=[]
for name in ['r13_c05/guides/p01_04.layout-only.png','r13_c05/guides/p03_04.layout-only.png']:
    p=B/name;guide_views.append({'file':str(p),'sha256':sha(p),'actuallyViewed':True,'viewImageDetail':'original','gameArt':False,'purpose':'approved coarse geometry comparison only; no detail/accuracy claim'})
ag=Path('D:/work/image/AGENTS.md')
report={'createdAtUtc':now,'manifest':{'file':str(O/'manifest.json'),'sha256':sha(O/'manifest.json')},'rootInstructionsRead':{'file':str(ag),'sha256':sha(ag)},'modelRequirement':m['modelRequirement'],'scope':{'internalSeamsViewed':48,'intersectionsViewed':18,'fullExternalBoundarySegmentsViewed':8,'partialRightBoundarySegmentsViewed':1,'fullCurrentCandidatesReviewed':['r13_c05','r14_c05'],'nativeArtCropsActuallyViewed':len(viewed),'nativePanelsActuallyViewed':len(panel_views),'individualPartialBoundaryActuallyViewed':1,'noCandidateOverviewUsedForAcceptance':True,'newImageCallsSinceModelGate':0,'artworkModified':False},'actualPanelViews':panel_views,'actuallyViewedCrops':viewed,'actuallyViewedCoarseGuides':guide_views,'pendingBuiltButUnviewedCrops':[r for r in m['records'] if r['id'].startswith('chain/r09_') or r['id'].startswith('chain/r10_') or r['id'].startswith('chain/r11_')],'missingExternalNeighbors':m['missingExternalNeighbors'],'actualModel':None,'actualQuality':None,'internalAccepted':False,'formalAccepted':False,'status':'local_QA_completed_with_concrete_failures_external_coverage_incomplete'}
write(O/'actual-views-and-findings.json',report)
assemblies={tile:read(m['sourceCandidates'][tile]['assembly']) for tile in ['r13_c05','r14_c05']}
def evidence(names):return [{'file':by[n]['file'],'sha256':by[n]['sha256'],'cropBox':by[n].get('cropBox'),'sourceBoxes':by[n].get('sourceBoxes')} for n in names]
issues=[]
def issue(id,tile,priority,kind,note,names,patches=None,repair=None,geometry_confirmed=True):
    sources=[x for x in assemblies[tile]['nativeSources'] if x['id'] in (patches or [])]
    issues.append({'id':id,'tile':tile,'priority':priority,'kind':kind,'concreteFinding':note,'nativeEvidence':evidence(names),'selectedNativeSourceEvidence':sources,'sourceCandidate':m['sourceCandidates'][tile]['candidate'],'suggestedRepair':repair,'geometryFindingConfirmed':geometry_confirmed,'toleranceEnlarged':False,'state':'open_generation_paused_until_explicit_verified_GPT_Image_2_5_route','actualModel':None,'actualQuality':None,'formalAccepted':False})
issue('C5-R14-G01','r14_c05',1,'broken_paving_groove','V2 row3 descending diagonal has an offset/break; lower rising diagonal is split into widely separated blunt-ended pieces. X2-2 and X3-2 independently expose same affected region.',['r14_c05/V2-3','r14_c05/X2-2','r14_c05/X3-2'],['p03_02','p03_03','p04_02','p04_03'],'Choose one approved continuous groove path in native coordinates across joined crop; locally restore only disconnected groove and adjacent ground. Do not add a grid to bridge disagreement.')
issue('C5-R14-G02','r14_c05',1,'broken_paving_groove','V3 row4 rising groove has a broad empty gap with blunt ends across join between p04_03 and p04_04.',['r14_c05/V3-4'],['p04_03','p04_04'],'One joined native1254 edit around the current discontinuity with both neighbor anchors; preserve nearby descending groove.')
issue('C5-R14-G03','r14_c05',1,'dead_end_paving_groove','H1 segment3 rising groove stops bluntly inside the stone near crop x330, reflecting omitted upper continuation.',['r14_c05/H1-3'],['p01_03','p02_03'],'Restore only original missing diagonal continuation across a joined native crop; keep other diagonal and stone plane.')
issue('C5-R14-G04','r14_c05',1,'dead_end_paving_branches','V1 row4 branches form a pointed dead end in right side of seam strip while left paving has no matching continuation. Incoming p04_01 and p04_02 topology conflicts.',['r14_c05/V1-4'],['p04_01','p04_02'],'Resolve against approved layout using paired exact native anchors; restore a coherent original groove, do not keep unsupported internal termination.')
issue('C5-R14-M01','r14_c05',2,'material_density_and_transitions','Dense diagonal weave/cellular mottles throughout paving; V3 row3 changes abruptly from woven face to smoother face. External r13/r14 boundary has straight material frontier.',['r14_c05/V1-3','r14_c05/V3-3','r14_c05/H2-4','chain/r13_c05--r14_c05-2','chain/r13_c05--r14_c05-3'],[x['id'] for x in assemblies['r14_c05']['nativeSources']],'After geometry fixes, localized native edits to broad quiet pale gray/blue-gray faces with neighboring scale and tone locked. No blur, resize, recolor or global restyling.')
issue('C5-R13-G01','r13_c05',1,'invented_wall_ledge','p01_04 invented a large projecting horizontal stone ledge across plain vertical wall. It appears below r12/r13 top4 and stops at available r13/r13c06 boundary. Approved same-crop guide has plain wall.',['chain/r12_c05--r13_c05-4','r13_c05/right-partial-row1'],['p01_04'],'Locally restore original continuous vertical wall plane and preserve red column/crossbeam; use approved p01_04 guide geometry plus exact top/right native references.')
issue('C5-R13-G02','r13_c05',1,'pink_foot_reentrant_cuts','V3 row3/X2-3 show a long thin incision under bevel and triangular notch above leaves; H2-4 has stepped/reentrant pink wall cuts beneath pale wall.',['r13_c05/V3-3','r13_c05/H2-4','r13_c05/X2-3'],['p02_03','p02_04','p03_03','p03_04'],'Repair only intended rounded pink footing/wall silhouette and leaf overlap in joined native crop; preserve established post and foliage footprint. Source coarse guide lacks reliable microdetail, so exact architectural semantics must be fixed before generation.')
issue('C5-R13-E01','r13_c05',1,'external_profile_and_alignment','Current r12v14/r13 segment2 vertical groove shifts laterally at boundary; segment3 red post side profile and lacquer brightness change abruptly with straight frontier.',['chain/r12_c05--r13_c05-2','chain/r12_c05--r13_c05-3'],['p01_02','p01_03'],'Repair only lower r13 border locally using exact current r12v14 anchor. Do not reopen or replay previous failed r12c05 repair loops.')
issue('C5-R13-M01','r13_c05',2,'material_density_and_transitions','Paving/wall surfaces contain large torn cloud patches and dense fine weave. All four top boundary segments have abrupt warm/smooth versus pale/patterned transition.',['r13_c05/V1-1','r13_c05/V1-2','r13_c05/H1-4','chain/r12_c05--r13_c05-1','chain/r12_c05--r13_c05-4'],[x['id'] for x in assemblies['r13_c05']['nativeSources']],'Localized material restoration after geometry repair with approved natural stone target and exact boundary anchors; no global recolor/blur.')
issue('C5-R13-S01','r13_c05',2,'layout_semantics_pending','Isolated diagonal groove end at V2 row1; diagonal-to-horizontal elbow at H2-1; inferred stepped pedestal under red/gold ornament at X3-2. Existing crops are fully painted but do not prove approved topology.',['r13_c05/V2-1','r13_c05/H2-1','r13_c05/X3-2'],['p01_02','p01_03','p02_01','p03_01','p04_02','p04_03'],'Compare exact approved local layout/context before deciding edits. Keep as pending semantic review, not certified repair or acceptance.',False)
issue('C5-R13-F01','r13_c05',2,'foliage_scale_and_overlap','Large leaves and bright yellow-green tips vary in projected scale through V2-3/V3-3/H3-4; lower external boundary also changes leaf tips and shadow tone.',['r13_c05/V2-3','r13_c05/V3-3','r13_c05/H3-4','chain/r13_c05--r14_c05-4'],['p03_02','p03_03','p03_04','p04_03','p04_04'],'Any future local edit must preserve original wall-side tree footprint and match neighboring native leaf sizes; review with geometry repairs, no new tree islands.',False)
queue={'createdAtUtc':now,'schemaVersion':1,'lane':'southwest col5 r09-r16','status':'paused_new_art_local_QA_complete_for_r13_r14','modelRequirement':m['modelRequirement'],'rootInstructions':report['rootInstructionsRead'],'actualViewReport':{'file':str(O/'actual-views-and-findings.json'),'sha256':sha(O/'actual-views-and-findings.json')},'issues':issues,'pendingMissingNativeSlots':{x['tile']:x['missingPatchIds'] for x in m['inventory'] if x['missingNativeSlots']},'missingLaneNativeSlots':32,'selectedLaneNativeSlots':96,'priorChainStatus':{'r09_c05_to_r10_c05':'exact native panels built but not viewed in this bounded review; pending','r10_c05_to_r11_c05':'exact native panels built but not viewed in this bounded review; pending','r11_c05_to_r12_c05':'exact native panels built but not viewed in this bounded review; pending','r12_c05_current':'v14 provisional retained; no repair calls and no repeat of failed earlier loops','r12_c05_to_r13_c05':'all4segments actually viewed; failed geometry/material','r13_c05_to_r14_c05':'all4segments actually viewed; material and leaf variation remain open'},'missingExternalNeighbors':m['missingExternalNeighbors'],'resumeConstraints':['Explicitly verified GPT Image2.5 route required before any generation or AI edit','No paid API or Git operations','Preserve old images, rejected returns, receipts and native hashes','Maximum2px local quilt/feather only; final no resizing, warping, recoloring or blur','Coverage is not acceptance; unavailable and unviewed boundaries remain pending'],'internalAccepted':False,'formalAccepted':False,'actualModel':None,'actualQuality':None}
write(O/'lane-repair-queue.json',queue)
state={'createdAtUtc':now,'owner':'/root/sw_col5_resume_20261012b','status':'local_only_qa_finished_new_generation_paused','selectedNativeSlots':96,'plannedNativeSlots':128,'missingNativeSlots':32,'currentCandidates':{t:m['sourceCandidates'][t] for t in ['r13_c05','r14_c05']},'latestGenerationBeforeGate':'r14_c05 p04_04 lines-guided-v01; existing unverified builtin metadata retained without model relabeling','nextGenerationFrontier':'r15_c05:p01_01 when explicit verified GPT Image2.5 route becomes available','localRepairQueue':{'file':str(O/'lane-repair-queue.json'),'sha256':sha(O/'lane-repair-queue.json')},'actualViewScope':report['scope'],'newImageCallsAfterModelGate':0,'sharedGlobalFilesEdited':False,'artworkModifiedDuringLocalQA':False,'internalAccepted':False,'formalAccepted':False,'actualModel':None,'actualQuality':None}
write(O/'lane-state.json',state)
print(json.dumps({'report':str(O/'actual-views-and-findings.json'),'queue':str(O/'lane-repair-queue.json'),'state':str(O/'lane-state.json'),'issueCount':len(issues),'nativeArtCropsViewed':len(viewed),'missingNativeSlots':32},ensure_ascii=False))
