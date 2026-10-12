"""Record the final static review and prepare a strictly local cleanup inventory.

This script deletes nothing. It must be run after final source selection/export.
"""
from pathlib import Path
import datetime, hashlib, json
ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
manifest['visualAcceptedFrames'] = 196
manifest['visualAcceptanceScope'] = 'Static identity, anatomy, prop ownership and pose readability; minor drawing residuals explicitly retained. Not full dynamic artistic or game acceptance.'
manifest['offlinePlaybackChecked'] = True
manifest['offlineDynamicAcceptance'] = 'not_certified_by_playback_function_checks'
manifest['deliveryStatus'] = 'local_assets_delivered_with_review_notes'
manifest['reviewNotes'] = ['NE15-v1 to16-v2 retains about17 nativepx heel-height reversal, ~1.6px at128display.',
 'N11 support about20 nativepx higher; N10 compression stronger; W08 to09 about5 nativepx reversal.',
 'E cast04 to05 lift and10 to11 recovery are brisk; W hit03 to04, attack03 to04 andcast11 to12 are brisk.',
 'Client movement, sliding, direction/idle transitions and event timing not validated.']
for f in manifest['frames']:
    f['visualAccepted'] = True
    f['visualAcceptanceScope'] = 'static_pose'
    f['status'] = 'static_reviewed_export'
    f['acceptanceNote'] = '静态身份/持物手/肢体与相位可读性已复核；轻微绘画残差保留。动态美术与客户端验收不得由文件或播放功能检查代替，见MERGE_HANDOFF.md。'
    write(Path(str(ROOT/f['file'])+'.generation.json'),f)
write(ROOT/'manifest.json',manifest)
playback = {'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'tool':'Codex in-app browser via cua_repl','url':'http://127.0.0.1:8818/preview/index.html?review=196',
 'groupsChecked':14,'imagesLoaded':196,'naturalSize':[1024,1024],
 'normalAndQuarterSpeedSequenceAdvance':True,'pauseStepAndFrameSelection':True,
 'runCycleComparisonMs':[480,640,720,800],'defaultRunCycleMs':720,
 'combatCycleMs':{'hit':240,'attack':360,'cast':720},
 'visualEvidence':'All14contact sheets inspected. Browser screenshots sampled enlarged and128/256views. FinalNE15-v1/16-v2 explicitly compared in browser; finalNE normal/slow wrap andruntime loading checked.',
 'continuousHumanMovieWatchClaimed':False,'fullDynamicArtAcceptance':False,'clientValidated':False}
write(ROOT/'provenance/browser-playback-review.json',playback)
selected = {f['derivedFrom']['file']:f['file'] for f in manifest['frames']}
keep_images = {f['file'] for f in manifest['frames']} | {'preview/'+key.replace('/','-')+'-contact.png' for key in {f['slot'].rsplit('/',1)[0] for f in manifest['frames']}}
files = []
for p in sorted(ROOT.rglob('*')):
    if not p.is_file(): continue
    rel = p.relative_to(ROOT).as_posix()
    is_candidate = rel.startswith('candidate/')
    is_old_image = p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif'} and rel not in keep_images
    if is_candidate or is_old_image:
        assert p.resolve().is_relative_to(ROOT)
        files.append({'file':rel,'sha256':sha(p),'bytes':p.stat().st_size,
          'reason':'native source exported to final runtime' if rel in selected else 'superseded image or review intermediate',
          'runtimeFile':selected.get(rel)})
write(ROOT/'provenance/cleanup-inventory.json',{'scope':str(ROOT),'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'status':'prepared_not_deleted','retainImageCount':len(keep_images),'removeFiles':files,
  'preserved':'Final runtime PNG+metadata,14current preview contactPNG,all original generation text records/prompts/jobs,review reports anddelivery tooling.'})
print(json.dumps({'staticPoseAccepted':196,'dynamicAccepted':0,'cleanupFiles':len(files),'cleanupBytes':sum(f['bytes'] for f in files),'retainImageCount':len(keep_images)}))
