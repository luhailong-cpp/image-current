"""Snapshot real candidates. Fixed whole-canvas export only; no pose edits or per-frame registration."""
import hashlib,json,re,shutil
from collections import defaultdict
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'frames').exists() and (ROOT/'manifest.json').exists() and json.loads((ROOT/'manifest.json').read_text(encoding='utf-8')).get('formalAccepted'):
    raise SystemExit('Formal delivery exists; historical candidate exporter is disabled.')
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SCALE=1024/1254
DUR={'run':30,'hit':40,'attack':30,'cast':45}
EXPECTED={'run':{d:16 for d in ['N','NE','E','SE','S','SW','W','NW']},'hit':{'E':6,'W':6},'attack':{'E':12,'W':12},'cast':{'E':16,'W':16}}
# Each slot picks latest on-disk attempt only, remaining a candidate.
picks={}
for p in sorted((ROOT/'staging').glob('*/*/*.png')):
    action,direction=p.parts[-3:-1]
    m=re.match(r'(\d+)(?:-v(\d+))?\.png$',p.name)
    if not m or action not in DUR:continue
    rec=Path(str(p)+'.generation.json')
    if not rec.exists() and action=='run':
        rec=ROOT/'provenance/run-north'/f'run-{direction}-{m[1]}-v{m[2] or 1}.generation.json'
    if not rec.exists():continue
    key=(action,direction,int(m[1]))
    version=int(m[2] or 1)
    if key not in picks or version>picks[key][0]:picks[key]=(version,p,rec,'new_generation')
# Selected prior static candidates remain linked to their original evidence.
reviewpath=ROOT/'review/prior-run-review.json'
if reviewpath.exists():
    for f in json.loads(reviewpath.read_text(encoding='utf-8-sig'))['frames']:
        key=('run','E',f['frame'])
        if key in picks or f['status']!='reusable_candidate_static':continue
        src=Path(f['path']);dest=ROOT/'staging/reused-run/E'/src.name
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():shutil.copy2(src,dest)
        rec=Path(str(dest)+'.generation.json')
        original=json.loads(Path(f['generationRecord']).read_text(encoding='utf-8-sig'))
        original['relocatedForMerge']={'path':str(dest),'source':str(src),'sha256':SHA(src),'originalRecord':f['generationRecord'],'operation':'verbatim reuse, not new generation'}
        rec.write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding='utf-8')
        picks[key]=(1,dest,rec,'reused_static_candidate')
frames=[];groups=defaultdict(list)
# The E-run audit keeps new records in provenance rather than adjacent sidecars.
selection=ROOT/'review/run-E-selection.json'
if selection.exists():
    for f in json.loads(selection.read_text(encoding='utf-8-sig'))['frames']:
        src=Path(f['path']);rec=Path(f['sourceRecord'])
        if src.is_relative_to(ROOT) and ('run','E',f['frame']) not in picks:
            picks[('run','E',f['frame'])]=(1,src,rec,f['origin'])
ordering=ROOT/'review/frame-order-adjustments.json'
if ordering.exists():
    for f in json.loads(ordering.read_text(encoding='utf-8'))['overrides']:
        picks[(f['action'],f['direction'],f['frame'])]=(1,ROOT/f['native'],ROOT/f['record'],'reviewed_phase_reordering')
for (action,direction,index),(_,src,rec,origin) in sorted(picks.items()):
    im=Image.open(src);im.load()
    if im.size!=(1254,1254) or im.mode!='RGBA':raise ValueError(f'Unexpected native {src} {im.size} {im.mode}')
    source=json.loads(rec.read_text(encoding='utf-8-sig'))
    if source.get('sha256') and source['sha256'].lower()!=SHA(src):raise ValueError(f'Stale source record {src}')
    out=ROOT/'candidate'/action/direction/f'{index:02}.png'
    out.parent.mkdir(parents=True,exist_ok=True)
    exported=im.resize((1024,1024),Image.Resampling.LANCZOS)
    exported.save(out)
    derived={'file':str(out),'sha256':SHA(out),'width':1024,'height':1024,'mode':'RGBA','derivedFrom':{'path':str(src),'sha256':SHA(src),'generationRecord':str(rec)},'operation':'uniform entire 1254x1254 canvas resampled to1024x1024 Lanczos; no crop/translation/bboxfit/grounding','actualModel':source.get('actualModel'),'actualQuality':source.get('actualQuality'),'visualApproved':False,'status':'candidate_export_not_formal'}
    outrec=Path(str(out)+'.generation.json');outrec.write_text(json.dumps(derived,ensure_ascii=False,indent=2),encoding='utf-8')
    frame={'id':f'{action}_{direction}_{index:02}','action':action,'direction':direction,'index':index-1,'path':out.relative_to(ROOT).as_posix(),'nativePath':src.relative_to(ROOT).as_posix(),'sha256':SHA(out),'nativeSha256':SHA(src),'durationMs':DUR[action],'status':'candidate_export','visualApproved':False,'sourceRecord':outrec.relative_to(ROOT).as_posix(),'origin':origin,'transform':{'scale':SCALE,'translation':[0,0],'perFrameBboxScaling':False,'lowestPixelGrounding':False},'events':[]}
    if action=='hit' and index==3:frame['events']=['recoil_peak']
    if action=='attack' and index==6:frame['events']=['contact_proposed']
    if action=='cast' and index==9:frame['events']=['release_proposed']
    frames.append(frame);groups[(action,direction)].append((index,out))
manifest={'schemaVersion':1,'characterId':'07_moon_shadow_assassin_girl','updatedAt':datetime.now(timezone.utc).isoformat(),'canvas':{'width':1024,'height':1024,'mode':'RGBA'},'registration':{'method':'shared_camera_root','globalScale':SCALE,'rootAnchor':[512,942.08],'rootMeaning':'prompt target, remains pending visual sequence calibration','perFrameBboxScaling':False,'lowestPixelGrounding':False},'frames':frames,'formalAccepted':False,'clientIntegration':'not_performed','note':'在制候选；数量/结构通过不等于美术完成；缺槽无占位图。'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
prev=ROOT/'preview';prev.mkdir(exist_ok=True)
preview_records=[]
for (action,direction),seq in groups.items():
    thumbs=[]
    sheet=Image.new('RGB',(4*300,((len(seq)+3)//4)*326),'#e5e7eb')
    draw=ImageDraw.Draw(sheet)
    for i,(idx,p) in enumerate(seq):
        im=Image.open(p).resize((300,300),Image.Resampling.LANCZOS)
        bg=Image.new('RGBA',(300,300),'#e5e7eb');bg.alpha_composite(im);thumbs.append(bg.convert('RGB'))
        sheet.paste(bg.convert('RGB'),((i%4)*300,(i//4)*326))
        draw.text(((i%4)*300+8,(i//4)*326+302),f'{action}/{direction}/{idx:02} CANDIDATE',fill='black')
    cp=prev/f'{action}-{direction}-contact.jpg';sheet.save(cp,quality=90)
    sources=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':SHA(p)} for _,p in seq]
    preview_records.append({'path':cp.relative_to(ROOT).as_posix(),'sha256':SHA(cp),'sources':sources,'operation':'300px thumbnails composited on gray, contact sheet; inspection only, not game frames'})
    if len(seq)==EXPECTED[action][direction]:
        for suffix,mult in [('normal',1),('slow',4)]:
            gif=prev/f'{action}-{direction}-{suffix}.gif'
            thumbs[0].save(gif,save_all=True,append_images=thumbs[1:],duration=DUR[action]*mult,loop=0,disposal=2)
            preview_records.append({'path':gif.relative_to(ROOT).as_posix(),'sha256':SHA(gif),'sources':sources,'operation':'300px indexed-color animation preview, GIF timing quantized to10ms','requestedDurationMs':DUR[action]*mult})
            apng=prev/f'{action}-{direction}-{suffix}.png'
            thumbs[0].save(apng,save_all=True,append_images=thumbs[1:],duration=DUR[action]*mult,loop=0)
            preview_records.append({'path':apng.relative_to(ROOT).as_posix(),'sha256':SHA(apng),'sources':sources,'operation':'300px APNG animation preview with exact requested timing','durationMs':DUR[action]*mult})
summary={'candidateSlots':len(frames),'target':196,'formalAccepted':0,'groups':{f'{a}/{d}':{'present':len(groups[(a,d)]),'expected':n} for a,ds in EXPECTED.items() for d,n in ds.items()}}
(prev/'progress.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(prev/'derivations.json').write_text(json.dumps({'updatedAt':datetime.now(timezone.utc).isoformat(),'artifacts':preview_records},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))

