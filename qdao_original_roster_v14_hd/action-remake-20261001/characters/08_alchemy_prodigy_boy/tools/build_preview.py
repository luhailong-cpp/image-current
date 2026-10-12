"""Fixed whole-canvas review export; never fit individual bounding boxes."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
selection = json.loads((ROOT/'review-selection.json').read_text(encoding='utf-8-sig'))
groups, files = [], []
preview = ROOT/'preview'
preview.mkdir(exist_ok=True)
for key, sources in selection.items():
    action, direction = key.split('/')
    ms = {'run':45,'hit':40,'attack':30,'cast':45}[action]
    frames=[]
    thumbnails=[]
    for idx, source in enumerate(sources,1):
        if source is None:
            frames.append(None)
            continue
        src = ROOT/source
        if not src.is_file():
            raise FileNotFoundError(src)
        im = Image.open(src).convert('RGBA')
        assert im.width == im.height and im.width >= 1024
        # One global camera fit, fixed for every frame and direction.
        # Full source canvas is resampled to 940 square, translated by (42,50).
        # Motion and airborne offset remain in the pixels; no alpha bbox alignment.
        out=Image.new('RGBA',(1024,1024))
        out.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,50))
        dest=ROOT/f'candidate/{key}/{idx:02}.png'
        dest.parent.mkdir(parents=True,exist_ok=True)
        out.save(dest)
        source_record=Path(str(src)+'.generation.json')
        if not source_record.exists():
            source_record=ROOT/f'provenance/combat-{direction}/{src.stem}.generation.json'
        assert source_record.is_file(), source_record
        rec={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'slot':f'{key}/{idx:02}',
             'derivedFrom':{'file':source,'sha256':sha(src),'nativeSize':list(im.size),
                            'generationRecord':source_record.relative_to(ROOT).as_posix(),'generationRecordSha256':sha(source_record)},
             'operation':{'type':'fixed_whole_canvas_resample','sourceCanvasToPx':[940,940],'offsetPx':[42,50],
                          'canvas':[1024,1024],'rootPx':[512,942],'perFrameBoundingBoxFit':False},
             'status':'review_candidate','visualAccepted':False,'dynamicAccepted':False,'clientIntegrated':False}
        Path(str(dest)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
        frames.append('../'+rec['file']+'?v='+rec['sha256'][:12])
        files.append(rec)
        tile=Image.new('RGB',(256,282),'#e9e4d5')
        thumb=out.resize((256,256),Image.Resampling.LANCZOS)
        tile.paste(thumb,(0,24),thumb)
        ImageDraw.Draw(tile).text((8,5),f'{key} {idx:02}',fill='#173c31')
        thumbnails.append(tile)
    cols=4
    sheet=Image.new('RGB',(cols*256,((len(thumbnails)+cols-1)//cols)*282),'#e9e4d5')
    for idx,tile in enumerate(thumbnails):
        sheet.paste(tile,((idx%cols)*256,(idx//cols)*282))
    sheet.save(preview/f'{action}-{direction}-contact.png')
    groups.append({'key':key,'ms':ms,'frames':frames})
(preview/'data.js').write_text('window.PREVIEW_DATA='+json.dumps(groups,ensure_ascii=False)+';',encoding='utf-8')
html = preview/'index.html'
if html.exists():
    import re
    source = html.read_text(encoding='utf-8')
    source = re.sub(r'src="data\.js(?:\?v=[^"]*)?"', 'src="data.js?v='+sha(preview/'data.js')[:12]+'"', source)
    html.write_text(source, encoding='utf-8')
manifest={'character':'08_alchemy_prodigy_boy','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'targetFrames':196,'reviewExported':len(files),'visualAccepted':0,'dynamicAccepted':0,
          'clientIntegrated':False,'rootPx':[512,942],'frames':files}
(ROOT/'review-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reviewExported':len(files),'groups':[g['key'] for g in groups]}))
