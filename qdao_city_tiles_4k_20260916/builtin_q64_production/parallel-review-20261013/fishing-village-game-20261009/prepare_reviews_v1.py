from review_tools_v1 import *
import shutil

def sheet(paths, dest, cols=4):
    ims=[Image.open(p).convert('RGB') for p in paths]
    w=max(i.width for i in ims); h=max(i.height for i in ims)
    canvas=Image.new('RGB',(cols*w,((len(ims)+cols-1)//cols)*(h+28)),(26,26,26))
    draw=ImageDraw.Draw(canvas)
    for n,(p,im) in enumerate(zip(paths,ims)):
        x=(n%cols)*w; y=(n//cols)*(h+28)
        canvas.paste(im,(x,y+28)); draw.text((x+5,y+7),Path(p).stem,fill='white'); im.close()
    canvas.save(dest)
    write(str(dest)+'.trace.json',dict(classification='100 percent native pixel contact sheet; labels outside art; no scaling',inputs=[record(p) for p in paths],output=record(dest)))

def group(name, sources, selection_records, vertical=None, horizontal=None, junctions=None):
    d=OUT/name; d.mkdir(exist_ok=True)
    strips=[]; joints=[]
    if vertical:
        x,y0,y1=vertical
        for n,y in enumerate(range(y0,y1,1024)):
            strips.append(crop_global(sources,[x-256,y,x+256,y+1024],d/f'V{n+1:02d}-100pct.png'))
        for n,y in enumerate(range(y0+1024,y1,1024)):
            joints.append(crop_global(sources,[x-256,y-256,x+256,y+256],d/f'VJ{n+1:02d}-100pct.png'))
    if horizontal:
        y,x0,x1=horizontal
        for n,x in enumerate(range(x0,x1,1024)):
            strips.append(crop_global(sources,[x,y-256,x+1024,y+256],d/f'H{n+1:02d}-100pct.png'))
        for n,x in enumerate(range(x0+1024,x1,1024)):
            joints.append(crop_global(sources,[x-256,y-256,x+256,y+256],d/f'HJ{n+1:02d}-100pct.png'))
    for n,(x,y) in enumerate(junctions or []):
        joints.append(crop_global(sources,[x-512,y-512,x+512,y+512],d/f'FOUR{n+1:02d}-100pct.png'))
    # Horizontal/vertical strips have distinct aspect ratios: separate for native sheets.
    for prefix in ('V','H'):
        p=[x for x in strips if x.name.startswith(prefix)]
        if p: sheet(p,d/f'{prefix}-segments-sheet-100pct.png',cols=4 if prefix=='V' else 2)
    regular=[p for p in joints if not p.name.startswith('FOUR')]
    if regular: sheet(regular,d/'junctions-sheet-100pct.png')
    write(d/'manifest-v1.json',dict(created_at_utc=datetime.now(timezone.utc).isoformat(),group=name,source_coordinate_count=len(set(s['tile'] for s in sources)),sources=sources,selection_records=[record(p) for p in selection_records],native_scale=True,segments=[str(p) for p in strips],junctions=[str(p) for p in joints],review_status='unreviewed',formal_accepted=False,stale_if='Any source pixel hash or any adopted selection changes'))

acc=SRC/'accelerated-jewelry-approach'
progress=read(acc/'progress.json')
accsources={s['tile']:source(s['tile'],s['file']) for s in progress['currentAdoptedCandidates']}
ne=SRC/'northeast'; active=read(ne/'records/active-candidates.json')
nesources={t:source(t,s['path']) for t,s in active['tiles'].items()}
partial4=[]
sel4=ne/'records/r04_c12.working-selection.json'
for k,v in read(sel4).items():
    t=k[:7]; r=int(k[-2]); c=int(k[-1]); x,y=origin(t); x+=(c-1)*1024; y+=(r-1)*1024
    partial4.append(source(t,ne/'native'/v,'current_selected_partial_native_core',[x,y,x+1024,y+1024],[115,115,1139,1139]))
partial6=[]
sel6=ne/'records/west_sol/r06_c11.selected.json'
for k,v in read(sel6).items():
    t=k[:7]; r=int(k[-2]); c=int(k[-1]); x,y=origin(t); x+=(c-1)*1024; y+=(r-1)*1024
    assert sha(v['path'])==v['sha256']
    partial6.append(source(t,v['path'],'current_selected_partial_native_core',[x,y,x+1024,y+1024],[115,115,1139,1139]))

g1=OUT/'G01-jewelry-six-reused-native-v1'; g1.mkdir(exist_ok=True)
old=acc/'resume-20261012/jewelry-approach-six-8192x12288-candidate-v1.png'
new=g1/'jewelry-six-8192x12288-native-candidate-reused-v1.png'
assert not new.exists(); shutil.copyfile(old,new); assert sha(old)==sha(new)
write(g1/'manifest-v1.json',dict(group='G01',operation='byte-identical reuse/copy of existing native six-tile assembly; no new generation',output=record(new),original=record(old),sources=list(accsources.values()),assembly_record=record(acc/'resume-20261012/candidate-manifest.json'),existing_qa=[record(acc/'resume-20261012'/n) for n in ['root-final-review.json','region-horizontal-review.json','root-region-subset-review.json']],native_pixels_resized=False,internal_and_region_review='reuse only where recorded source identities match; cross-region pending',formal_accepted=False,actual_model=None,stale_if='Any source or adopted selection changes'))
preview(list(accsources.values()),[36864,8192,45056,20480],g1/'preview-downsampled-labelled-v1.png',scale=1/4)

group('G02-jewelry-east-r04-r05-v1',[accsources['r04_c11'],accsources['r05_c11'],nesources['r05_c12']]+partial4,[acc/'progress.json',sel4,ne/'records/active-candidates.json'],vertical=[45056,12288,20480])
group('G03-jewelry-south-and-east-r06-v1',[accsources['r05_c11'],nesources['r05_c12'],nesources['r06_c12']]+partial6,[acc/'progress.json',sel6,ne/'records/active-candidates.json'],vertical=[45056,20480,24576],horizontal=[20480,41984,45056],junctions=[(45056,20480)])
sw=SRC/'southwest'; se=SRC/'southeast'
south=[source('r10_c07',sw/'tiles/r10_c07_v1.png'),source('r11_c07',sw/'qa/full-tile-r11_c07-candidate-4096.png'),source('r10_c08',se/'r10_c08/processed/colorpass/r10_c08-colorpass-candidate.png'),source('r11_c08',se/'r11_c08/processed/joint-edge-color-v1/candidate-4096.png')]
group('G04-southwest-southeast-r10-r11-v1',south,[sw/'current-tile-ledger.json',se/'delivery-index.json'],vertical=[28672,36864,45056])
print(json.dumps({'prepared_groups':4,'native_crop_count':43,'output':str(OUT)},ensure_ascii=False))
