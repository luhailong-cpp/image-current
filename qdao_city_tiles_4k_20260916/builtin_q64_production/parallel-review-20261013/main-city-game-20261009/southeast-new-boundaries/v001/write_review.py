from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

D=Path(__file__).resolve().parent
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(name,d):
    with (D/name).open('x',encoding='utf-8') as f:f.write(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=read(D/'crop-manifest.json');details=read(D/'detail-crop-manifest.json')
observations={
 'E-r13_c13-r13_c14-q1':('PASS_LOCAL_MAJOR_GEOMETRY','Timber brace and curved parasol border cross the true core boundary without an observed broken contour. Paving lines and shading remain connected in this segment.'),
 'E-r13_c13-r13_c14-q2':('FAIL_LOCAL_UMBRELLA_BAND_CONTOUR','The red/ivory parasol band edges change direction sharply together at the true x=53248 core cut. The cream stripe and outer red border form an abrupt corner at the same cut; no supporting rib or visible fabric crease explains both direction changes. The pole/cap itself remains connected.'),
 'E-r13_c13-r13_c14-q3':('PASS_LOCAL_MAJOR_GEOMETRY','Wooden board edges, bevels, diagonal rail and adjacent paving contours remain continuous across the true boundary. Local grain/tone variation does not create a new broken structural edge.'),
 'E-r13_c13-r13_c14-q4':('PASS_LOCAL_MAJOR_GEOMETRY','Diagonal slab joints and their intersection connect across the core cut; platform underside, ground shadow and paper fragments show no new structural seam here.'),
 'N-r13_c14-r14_c14-q1':('PASS_LOCAL_MAJOR_GEOMETRY','Paving grout intersection and diagonal runs, paper fragments and shadow shapes continue across the horizontal core cut. No new grout stub or offset seen within this 320px band.'),
 'N-r13_c14-r14_c14-q2':('PASS_LOCAL_MAJOR_GEOMETRY','Upright post edges and gold bevel continue across the seam; paving intersection and the support/shadow boundary remain aligned.'),
 'N-r13_c14-r14_c14-q3':('PASS_LOCAL_MAJOR_GEOMETRY_PRIOR_REPAIR_ENDPOINT_NOT_CLEARED','Main timber board boundaries and ledge bevel remain continuous within the +/-160px seam band. Focused original-pixel view at the old x2842/2874 area shows the vertical facet and shading transition without a newly observed core-line dislocation. This limited band does not independently close the previously unresolved deeper repair endpoint/perimeter.'),
 'N-r13_c14-r14_c14-q4':('PASS_LOCAL_MAJOR_GEOMETRY','Large upper ledge, lower bright rim and their shadow surfaces continue across the true core cut. No new contour step is observed within the 320px band.'),
 'N-r13_c15-r14_c15-q1':('PASS_LOCAL_MAJOR_GEOMETRY_REPAIRED_N01','The vertical board-end joint at child-local x~230 now crosses y=0 and reaches the diagonal lower plank boundary. Its width and alignment remain coherent; no duplicate groove or new alpha-edge break is observed.'),
 'J-53248-53248':('PASS_LOCAL_MAJOR_GEOMETRY','All four current candidates meet with continuous slab outlines and grout intersections. The shaded stone and red paper fragments do not reveal a new four-core corner break; fine stone texture variations remain a cosmetic note.'),
 'J-57344-53248':('PASS_LOCAL_MAJOR_GEOMETRY','The broad wood deck, bright ledge edge, lower platform corner and repaired board-end joint remain coherent at this four-tile meeting. No new core-corner geometry break observed.')}

entries=[];viewed=[]
for e0 in m['entries']:
    e=dict(e0);assert sha(e['file'])==e['sha256']
    if e['id'] in observations:
        verdict,note=observations[e['id']];e.update(localVerdict=verdict,observation=note,actualViewedThisReview=True,
          viewTool='view_image with detail=original',nativePixelScaleActuallyViewed=1,
          reviewedDisplayFile=e.get('displayRotation',{}).get('file',e['file']))
        viewed.append(e['reviewedDisplayFile'])
    else:
        assert e['localVerdict']=='PASS_LOCAL_MAJOR_GEOMETRY_REUSED_PIXEL_IDENTICAL'
        p=e['priorEvidenceComparison'];assert p['pixelIdentical'] and p['priorActuallyViewed'] and p['priorStatus']=='pass_observed'
        assert sha(p['report'])==p['reportSHA256'] and sha(p['file'])==p['sha256']
        e['observation']='Prior actually viewed 1024x512 external-core join has an RGB-identical central1024x320 subset on the current adopted candidates. Prior local pass is reused, with no repeat view.'
    if 'displayRotation' in e:assert sha(e['displayRotation']['file'])==e['displayRotation']['sha256']
    entries.append(e)

for d in details:
    assert sha(d['file'])==d['sha256'];d.update(actualViewedThisReview=True,viewTool='view_image with detail=original',nativePixelScaleActuallyViewed=1);viewed.append(d['file'])
fail={'id':'SE-E13-UMBRELLA-BAND','severity':'blocking_local_geometry','pair':['r13_c13','r13_c14'],
 'evidenceId':'E-r13_c13-r13_c14-q2','axis':'x','boundaryWorldX':53248,
 'approximateWorldBox':[53213,50516,53283,50650],
 'approximateEastTileRelativeBox':[-35,1364,35,1498],
 'description':observations['E-r13_c13-r13_c14-q2'][1],
 'detailEvidence':details[0],
 'coordinateMapping':'In the rotated1024x320 strip, display(x,y) maps to world(x=53407-y,y=50176+x); the true seam lies between display rows159 and160.',
 'actionNeeded':'Native geometry repair/review by the owning production window. No repair performed by this independent review.'}
end=[]
for t in m['inputs']:
    actual=sha(t['file']);end.append({'tile':t['tile'],'file':t['file'],'recordedSHA256':t['sha256'],'endSHA256':actual,'unchanged':actual==t['sha256'],'pixels':t['pixels'],'worldBox':t['worldBox']})
unchanged=all(x['unchanged'] for x in end)
report={'schemaVersion':1,'reviewedAtUTC':datetime.now(timezone.utc).isoformat(),'reviewer':'independent_southeast_boundaries',
 'scope':'Three specified current-candidate borders and two640px junctions only. This is local review, not formal tile/group/map acceptance.',
 'inputs':m['inputs'],'cropManifest':{'file':str(D/'crop-manifest.json'),'sha256':sha(D/'crop-manifest.json')},
 'entries':entries,'supplementalDetailImages':details,'actuallyViewedFiles':viewed,
 'newBoundarySegmentsActuallyViewed':9,'priorPixelIdenticalBoundarySegmentsReused':3,'junctionsActuallyViewed':2,'supplementalDetailImagesActuallyViewed':2,
 'localBoundaryResults':{'segments':12,'localMajorGeometryPassed':11,'localGeometryFailed':1,'junctionsLocalMajorGeometryPassed':2},
 'newlyObservedOrReconfirmedBlockingFindings':[fail],
 'priorIssuesNotClosed':[{'tile':'r14_c14','location':'child-local x2842/2874 north repair endpoint/perimeter','reason':'The +/-160px border strip and focused facet view only support local contour continuity. Prior unresolved deeper endpoint remains open until its whole support/perimeter is checked.',
 'evidence':'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14/repairs/north-far-east-ledges-20261012-v1/root-visual-qa-20261013.json'},
 {'scope':'Other boundaries of the six-tile group','reason':'Existing FAILs are outside this specific new-review scope and remain. No deliverable group mosaic is produced.'}],
 'repairedHistoricalFinding':{'id':'N01','pair':['r13_c15','r14_c15'],'status':'old_fail_superseded_by_new_current_native_view_local_pass','evidenceId':'N-r13_c15-r14_c15-q1'},
 'endSourceHashVerification':end,'allSixInputSourcesUnchangedAtEnd':unchanged,'reportStale':not unchanged,
 'formalAccepted':False,'deliverableGroupMosaicCreated':False,'newGenerationPerformed':False,'productionFilesModified':False,
 'snapshotRule':'Valid only for the six recorded candidate hashes and exact crop world boxes. Any source change makes affected entries stale; current generation model preference does not freeze production.'}
save('review.json',report)
save('end-source-hashes.json',{'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'allUnchanged':unchanged,'sources':end})
summary='''东南6块指定边界独立检查 v001\n\n输入：r13/r14 × c13/c14/c15，6张当前4096×4096采用候选，哈希及世界坐标绑定在crop-manifest.json；生产目录只读。\n检查：3条边共12段（每段1024×320或320×1024原像素），9段新实看，3段与旧通过证据逐像素一致后复用；另外新实看2个640×640四块交点及2张原尺寸细节图。竖缝只做无插值90度旋转供观看，映射已记录。\n局部结论：11段主要轮廓通过、1段伞面条带折角失败；2个交点主要轮廓连续。\n失败位置：r13_c13→r13_c14第2段，真core界world x53248，约world[53213,50516,53283,50650]。红边与米白条带在同一切线突然折角，杆体本身连续。见E-r13_c13-r13_c14-q2-rotate90ccw.png及detail-E-q2-canopy.png。\nr13_c15→r14_c15第一段旧N01已由当前图新实看通过；后三段当前像素等同旧已实看通过证据，旧N01 FAIL不再沿用。\nr13_c14→r14_c14四段只通过±160像素局部主要轮廓；旧x2842/2874更深修复端点/周界仍未自动关闭。其他现有FAIL不在本次清除范围，因此没有制作可交付合图，不声明整块、整区或地图完成。\n末尾6张输入源hash均未变化；后续生产换源需重验。\n'''
with (D/'summary.txt').open('x',encoding='utf-8') as f:f.write(summary)
assert unchanged
print(json.dumps({'review':str(D/'review.json'),'newViewedSegments':9,'reusedSegments':3,'junctions':2,'failedSegmentIds':['E-r13_c13-r13_c14-q2'],'allSixSourcesUnchanged':unchanged},ensure_ascii=False,indent=2))
