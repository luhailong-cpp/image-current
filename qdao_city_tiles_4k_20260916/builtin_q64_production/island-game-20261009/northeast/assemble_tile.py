"""Native core assembly and deterministic QA crops. No image synthesis/resizing of final artwork."""
from native_work import *
import numpy as np,sys,re
tid=sys.argv[1]; selection=read(ZONE/f'selection-{tid}.json'); row,col=map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',tid).groups()); ox=(col-1)*4096; oy=(row-1)*4096
out=Image.new('RGB',(4096,4096)); coverage=np.zeros((4096,4096),dtype='uint8'); sources=[]
for r,line in enumerate(selection['cores']):
    for c,ident in enumerate(line):
        if ident is None: continue
        p=ZONE/'native'/f'{ident}.png'; rec=read(p.with_suffix('.png.generation.json')); im=Image.open(p); assert im.size==(1254,1254); assert sha(p)==rec['sha256']; assert rec['coreWorldBox']==[ox+c*1024,oy+r*1024,ox+(c+1)*1024,oy+(r+1)*1024]
        out.paste(im.crop(tuple(rec['coreCrop'])),(c*1024,r*1024)); coverage[r*1024:(r+1)*1024,c*1024:(c+1)*1024]+=1
        sources.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':rec['coreCrop'],'tileLocalPaste':[c*1024,r*1024],'nativeSize':list(im.size)})
overlays=[]
for overlay_id in selection['overlays']:
    q=read(ZONE/'qa'/f'{overlay_id}.overlay.json'); assert q['review'].startswith('passed_'); assert sha(q['source'])==q['sha256']; out.paste(Image.open(q['source']).crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste'])); overlays.append(q)
complete=bool((coverage==1).all()); complete_rows=0
for line in selection['cores']:
    if all(line): complete_rows+=1
    else: break
if not complete:
    if complete_rows:
        part=out.crop((0,0,4096,complete_rows*1024)); part.save(ZONE/'qa'/f'{tid}-partial-native.png'); part.resize((1536,complete_rows*384),Image.Resampling.LANCZOS).save(ZONE/'qa'/f'{tid}-partial-preview.png')
    write(ZONE/'qa'/f'{tid}-partial.json',{'tileId':tid,'status':'partial_not_complete4k','sourceCoreCount':len(sources),'fullRows':complete_rows,'uncoveredPixels':int((coverage==0).sum()),'sources':sources,'overlays':overlays,'finalArtUpscaled':False})
    print(json.dumps({'status':'partial','sourceCoreCount':len(sources),'fullRows':complete_rows})); sys.exit(0)
dest=ZONE/'tiles'/f'{tid}.png'; out.save(dest); out.resize((1536,1536),Image.Resampling.LANCZOS).save(ZONE/'qa'/f'{tid}-preview.png'); qa=ZONE/'qa'/f'{tid}-final'; qa.mkdir(exist_ok=True)
for r in range(4):
    for c in range(4): out.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(qa/f'core-{r+1}-{c+1}-100pct.png')
for i in range(1,4):
    for j in range(4):
        out.crop((i*1024-128,j*1024,i*1024+128,(j+1)*1024)).save(qa/f'vertical-{i}-segment-{j+1}-100pct.png'); out.crop((j*1024,i*1024-128,(j+1)*1024,i*1024+128)).save(qa/f'horizontal-{i}-segment-{j+1}-100pct.png')
for r in range(1,4):
    for c in range(1,4): out.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(qa/f'cross-{r}-{c}-100pct.png')
record={'tileId':tid,'file':dest.as_posix(),'sha256':sha(dest),'size':[4096,4096],'worldBox':[ox,oy,ox+4096,oy+4096],'operation':'16 native1024 core crops tiled with recorded native repair overlays; no resampling or feathering','sources':sources,'requiredOverlays':overlays,'baseCoverageMin':int(coverage.min()),'baseCoverageMax':int(coverage.max()),'uncoveredPixels':int((coverage==0).sum()),'finalArtUpscaled':False,'status':'complete_native_coverage_pending_whole_tile_QA','internalReview':'pending','externalSeams':'pending adjacent4k tiles','formalAccepted':False,'actualModel':None,'actualQuality':None,'generatedAtUtc':now(),'preview':(ZONE/'qa'/f'{tid}-preview.png').as_posix(),'inspectionCrops':qa.as_posix()}
write(dest.with_suffix('.png.derivation.json'),record); print(json.dumps({'file':dest.as_posix(),'sha256':record['sha256'],'size':[4096,4096],'uncoveredPixels':0}))
