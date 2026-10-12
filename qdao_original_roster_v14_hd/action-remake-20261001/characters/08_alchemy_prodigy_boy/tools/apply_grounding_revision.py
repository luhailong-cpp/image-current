"""Apply explicitly reviewed AI edits to registered runtime frames.

Input is an edit of an existing registered 1024 canvas. Only a uniform full-
canvas resample is allowed, with no offset, fit-to-bounds, or foot alignment.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
before_path=ROOT/'provenance/grounding-20261003/before-manifest.json'
before=json.loads(before_path.read_text(encoding='utf-8'))
before_by_slot={f['slot']:f for f in before['frames']}
selection=json.loads((ROOT/'grounding-selection.json').read_text(encoding='utf-8-sig'))
for f in manifest['frames']:
    if f['slot'] not in selection:continue
    chosen=selection[f['slot']]
    src=ROOT/chosen['source']
    record=Path(str(src)+'.generation.json')
    rec=json.loads(record.read_text(encoding='utf-8'))
    assert sha(src)==rec['sha256']
    with Image.open(src) as im:
        assert im.mode=='RGBA' and min(im.size)>=1024 and im.width==im.height
        native=list(im.size)
        out=im.resize((1024,1024),Image.Resampling.LANCZOS)
    dest=ROOT/f['file']
    out.save(dest)
    input_snapshot=ROOT/chosen.get('editInputSnapshot','provenance/grounding-20261003/before-manifest.json')
    original=next(x for x in json.loads(input_snapshot.read_text(encoding='utf-8'))['frames'] if x['slot']==f['slot'])
    f.update({'sha256':sha(dest),
        'derivedFrom':{'file':chosen['source'],'sha256':sha(src),'nativeSize':native,
          'generationRecord':record.relative_to(ROOT).as_posix(),'generationRecordSha256':sha(record)},
        'editInput':{'file':original['file'],'sha256':original['sha256'],
          'historicalManifest':input_snapshot.relative_to(ROOT).as_posix(),'historicalManifestSha256':sha(input_snapshot)},
        'operation':{'type':'fixed_whole_canvas_resample_of_registered_runtime_edit',
          'sourceCanvasToPx':[1024,1024],'offsetPx':[0,0],'canvas':[1024,1024],
          'rootPx':[512,942],'perFrameBoundingBoxFit':False,'footPixelAlignment':False},
        'status':'grounding_pose_repaired','staticPoseReviewed':True,'visualAccepted':True,
        'visualAcceptanceScope':'static_pose','dynamicAccepted':False,'clientIntegrated':False,
        'groundingRevision':{'date':'2026-10-03','reason':chosen['reason']}})
    write(Path(str(dest)+'.generation.json'),f)
manifest['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest['groundingRevisionSelection']='grounding-selection.json'
manifest['transform']['note']='Historical initial export. Revised runtime-input edits use full-canvas-to1024 with zero offset; consult per-frame operation. No per-frame fit or whole-sprite grounding translation.'
write(ROOT/'manifest.json',manifest)
print(json.dumps({'revisedSlots':list(selection),'frames':len(manifest['frames'])}))
