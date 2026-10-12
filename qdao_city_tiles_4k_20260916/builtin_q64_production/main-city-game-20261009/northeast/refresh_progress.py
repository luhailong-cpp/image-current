"""Inventory actual zone assets; generation/review/completion remain distinct."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
from PIL import Image
ZONE=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reservation_path=ZONE/'reserved-tiles-20261013.json'
reserved=set(read(reservation_path).get('reservedTiles',[])) if reservation_path.exists() else set()
owned_target=64-len(reserved)
native={}
issues=[]
for path in ZONE.rglob('*.generation.json'):
    try:
        d=read(path)
        if not str(d.get('route','')).startswith('builtin'): continue
        f=Path(d['file']).resolve()
        if not f.is_relative_to(ZONE): continue
        if not f.is_file(): issues.append({'record':str(path),'issue':'source missing'}); continue
        if d.get('sha256') != sha(f): issues.append({'record':str(path),'issue':'hash mismatch'}); continue
        with Image.open(f) as im:
            size=im.size; fmt=im.format
        if size != (1254,1254) or fmt!='PNG':
            issues.append({'record':str(path),'issue':'unexpected native size/format','size':size}); continue
        native[str(f)]={'file':str(f),'record':str(path),'sha256':d['sha256'],'dimensions':list(size)}
    except (OSError,KeyError,TypeError,ValueError) as e:
        issues.append({'record':str(path),'issue':str(e)})
tiles=[]
for tile in sorted(ZONE.iterdir()):
    if not tile.is_dir() or not re.fullmatch(r'r\d{2}_c\d{2}',tile.name): continue
    if tile.name in reserved:continue
    selected=read(tile/'selected-native.json') if (tile/'selected-native.json').exists() else {}
    cores=[p for p in [f'p{r}{c}' for r in range(1,5) for c in range(1,5)]
           if str((tile/'native'/selected.get(p,p+'.png')).resolve()) in native]
    progress=read(tile/'tile-progress.json') if (tile/'tile-progress.json').exists() else {}
    candidate=Path(progress['candidate']) if progress.get('candidate') else tile/'candidates'/f'{tile.name}.candidate.png'
    assert candidate.resolve().is_relative_to(tile.resolve()), 'Candidate must stay inside tile'
    full=False
    candidate_hash=None
    if candidate.is_file() and len(cores)==16:
        with Image.open(candidate) as im:
            im.load()
            full=im.size==(4096,4096) and (im.mode=='RGB' or (im.mode=='RGBA' and im.getextrema()[3]==(255,255)))
        if full: candidate_hash=sha(candidate)
    progress=read(tile/'tile-progress.json') if (tile/'tile-progress.json').exists() else {}
    internal=bool(full and progress.get('internalPassed4kCount')==1 and progress.get('candidateSha256')==candidate_hash)
    count=sum(Path(v['file']).is_relative_to(tile) for v in native.values())
    tiles.append({'tile':tile.name,'generatedNativeCount':count,'selectedCoreCount':len(cores),'missingCoreCount':16-len(cores),'fullyCovered4kCount':int(full),'internalPassed4kCount':int(internal),'formalAcceptedCount':0,'candidate':str(candidate) if full else None,'candidateSha256':candidate_hash,'workerStatus':progress.get('status'),'nextPatch':progress.get('nextPatch')})
total_generated=len(native); covered=sum(t['fullyCovered4kCount'] for t in tiles); cores=sum(t['selectedCoreCount'] for t in tiles)
connected=set()
current_hashes={t['tile']:t['candidateSha256'] for t in tiles}
if (ZONE/'connected-groups.json').exists():
    for group in read(ZONE/'connected-groups.json')['groups']:
        if all(current_hashes.get(tid)==s['sha256'] for tid,s in group['sources'].items()):
            connected.update(group['sources'])
data={'zone':'northeast','updatedAt':datetime.now(timezone.utc).isoformat(),'status':'native_art_production_and_connected_2x2_seam_review','firstTile':'r05_c13','zoneRows':[1,8],'zoneColumns':[9,16],'assignedTileCount':64,'generatedNativeCount':total_generated,'generatedNativeInsideTileDirectories':sum(t['generatedNativeCount'] for t in tiles),'generatedSharedBorderRepairCount':total_generated-sum(t['generatedNativeCount'] for t in tiles),'usableSelectedCoreCount':cores,'complete4kCandidateCount':covered,'fullyCovered4kCount':covered,'internalPassed4kCount':sum(t['internalPassed4kCount'] for t in tiles),'externalPassed4kCount':0,'formalAcceptedCount':0,'missingFullyCovered4kCount':64-covered,'missingNativeCoreCount':1024-cores,'tiles':tiles,'actualModel':None,'actualQuality':None,'priorUserSuppliedAGENTSInstructionsApply':False,'runtimeWorkRequested':False,'paidApiAllowed':False,'nextStep':'Finish connected r05/r06 c13/c14 candidates and all shared seams; continue existing assigned art queue after review.','inventoryIssues':issues}
data['connectedGroupReviewed4kCount']=len(connected)
data['originalZoneTargetTileCount']=64
data['assignedTileCount']=owned_target
data['transferredTileCount']=len(reserved)
data['transferredTileIds']=sorted(reserved)
data['missingFullyCovered4kCount']=owned_target-covered
data['missingNativeCoreCount']=owned_target*16-cores
data['deduplicatedTargetTileCount']=owned_target
data['complete16Core4kCandidateCount']=covered
data['missingNativeTileCount']=owned_target-sum(t['selectedCoreCount']==16 for t in tiles)
data['fullyNativeTilesAwaiting4kAssemblyCount']=sum(t['selectedCoreCount']==16 and not t['fullyCovered4kCount'] for t in tiles)
data['completeTilesPendingInternalReviewCount']=sum(t['fullyCovered4kCount'] and not t['internalPassed4kCount'] for t in tiles)
data['completionCountingNote']='Zone drawing and internal review counted independently from unfinished outside-zone neighbors; formal world acceptance is separate.'
if connected:
    data['status']='continuing_adjacent_native_art_after_first_connected_group_review'
    data['nextStep']='Continue active r07/r08 c13/c14 queue with recorded real north/west native dependencies; review each completed tile and shared edge.'
    data['workQueue']=str(ZONE/'work-queue-20261010.json')
resume_path=ZONE/'production-resume-20261012.json'
if resume_path.exists():
    resume=read(resume_path)
    if resume.get('newArtworkGenerationAllowed') and not resume.get('generationStopped'):
        data.update({'status':'resumed_native_generation_during_snapshot_upload','generationStopped':False,'productionResume':str(resume_path),'migrationFreeze':resume.get('historicalFreeze'),'workQueue':str(ZONE/'work-queue-20261012.json'),'nextStep':resume.get('nextStep')})
model_pause=ZONE/'image-model-pause-20261012.json'
if model_pause.exists():
    hold=read(model_pause)
    if hold.get('newGenerationPaused'):
        data.update({'status':'new_generation_paused_pending_verified_gpt_image_2_5_route_local_review_active','generationStopped':True,'newArtworkGenerationAllowed':False,'requestedImageModel':hold.get('requestedImageModel'),'verifiedImageGenerationRoute':None,'imageModelPause':str(model_pause),'workQueue':str(ZONE/'work-queue-finish-20261012.json'),'nextStep':'Preserve returned outputs, assemble and review existing native art; missing cores and new P2 painting wait for an explicitly selectable and verified GPT Image 2.5 route without paid API.'})
(ZONE/'progress.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ZONE/'current-native-inventory.json').write_text(json.dumps({'updatedAt':data['updatedAt'],'outputs':list(native.values()),'issues':issues},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:data[k] for k in ['generatedNativeCount','usableSelectedCoreCount','fullyCovered4kCount','internalPassed4kCount','formalAcceptedCount','inventoryIssues']},ensure_ascii=False))
