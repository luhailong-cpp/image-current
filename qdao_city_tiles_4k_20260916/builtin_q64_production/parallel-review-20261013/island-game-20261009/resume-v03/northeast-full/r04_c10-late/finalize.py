from pathlib import Path
import json,hashlib,datetime
O=Path(__file__).resolve().parent
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
d=read(O/'prepared.json');snapshot=read(O/'input-snapshot.json')
boardmap={p:b['file'] for b in d['boards'] for p in b['panels']}
for e in d['evidence']:
 e.update(actuallyViewed=True,viewedVia=boardmap[e['file']],inspectionTool='view_image',inspectionDetail='original',inspectionScale=1,viewedAtUtc=now,status='local_visual_passed',geometry='passed',material='no_abrupt_boundary_discontinuity_seen')
 e['finding']='石板外轮廓、砖缝及表面纹理跨接线连续；未见漏填、平移错位或沿接线的矩形色带。'
for b in d['boards']:b.update(actuallyViewed=True,viewedAtUtc=now,inspectionDetail='original')
emap={e['file']:e for e in d['evidence']}
for edge in d['edges']:
 edge['segments']=[emap[e['file']] for e in edge['segments']]
 edge.update(status='shared_edge_local_visual_passed',reviewedPixelLength=4096,formalAccepted=False)
t=d['tiles'][0];t['evidence']=d['evidence'];t.update(internalReview='passed_24seams_9crosses_frozen_candidate',internalSeamCount=24,internalCrossCount=9,actuallyViewedEvidenceCount=41,formalAccepted=False,pendingArtIssues=[],edgeReviews=d['edges'])
changes=[]
for e in snapshot['files']:
 p=Path(e['file']);current=sha(p) if p.is_file() else None
 if current!=e['sha256']:changes.append(dict(file=e['file'],snapshotSha256=e['sha256'],currentSha256=current,kind='image' if p.suffix.lower()=='.png' else 'metadata'))
live=read(P/'selection-r04_c10.json');old=read(O.parent.parent/'northeast/snapshots/selection-r04_c10.json')
selectionUnchanged=all(live.get(k)==old.get(k) for k in ['cores','overlays','candidatePath'])
recheck=dict(checkedAtUtc=now,checkedFileCount=len(snapshot['files']),unchangedFileCount=len(snapshot['files'])-len(changes),changes=changes,sourcePixelsUnchanged=not any(e['kind']=='image' for e in changes),currentProductionArtSelectionUnchanged=selectionUnchanged,currentSelectionFile=(P/'selection-r04_c10.json').as_posix(),currentSelectionSha256=sha(P/'selection-r04_c10.json'),policy='Report is bound to parent frozen candidate; later selection changes recorded only, never followed automatically.')
write(O/'source-recheck.json',recheck)
visual=dict(reviewedAtUtc=now,viewedBoards=d['boards'],evidence=d['evidence'],additionalDirectViews=[(O/f).as_posix() for f in ['vertical-3-segment-1-100pct.png','north-segment-1-100pct.png','north-segment-2-100pct.png','east-segment-1-100pct.png']],tool='view_image',detail='original',nativeScale=True,totalEvidenceCount=41,internalSeams=24,internalCrosses=9,neighborSegments=8,scope='Seam and junction inspection only; all core interiors and missing neighbors are outside this supplement.')
write(O/'visual-review.json',visual)
write(O/'repair-queue.json',dict(artRepairs=[],metadataNotes=[dict(tileId='r04_c10',status='nonblocking_record_discrepancy',finding=t['recordDiscrepancy'],productionModified=False)]))
d.update(status='frozen_batch_review_complete',completedAtUtc=now,sourceRecheck=recheck,visual=(O/'visual-review.json').as_posix(),reusedPassedEvidenceCount=0,reuseExplanation='Existing complete-candidate border records were pending_visual_review; this supplement actually viewed all 41 evidence crops, via nine exact unscaled boards plus four direct crops.',repairs=[],formalAcceptedCount=0,scopeLimitations=['Candidate SHA256 1c2426a455f774064d391de1606e142c84bd819e94f7e4794ffb4d95d0ebcef6 only.', 'South/west incomplete neighbors and full core-interior art acceptance not included.', 'Original two-tile northeast-full summary and all production files remain unchanged.'])
write(O/'summary.json',d)
print(json.dumps(dict(tileId=t['tileId'],sha256=t['sha256'],replay=t['replayMatchesCandidate'],visual=41,sourceRecheck=recheck),ensure_ascii=False))
