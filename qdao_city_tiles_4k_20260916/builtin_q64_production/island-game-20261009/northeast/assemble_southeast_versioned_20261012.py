from native_work import *
import sys,re,numpy as np
tid,tag=sys.argv[1:3]; assert tid in ('r05_c14','r06_c14'); assert tag.startswith(tid)
sel=read(ZONE/f'selection-{tid}.json'); row,col=map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',tid).groups()); ox=(col-1)*4096; oy=(row-1)*4096
dest=ZONE/'tiles'/f'{tag}.png'; preview=ZONE/'qa'/f'{tag}-preview.png'; qdir=ZONE/'qa'/f'{tag}-final'
assert not dest.exists() and not preview.exists() and not qdir.exists()
out=Image.new('RGB',(4096,4096)); cover=np.zeros((4096,4096),dtype='uint8'); sources=[]
for r,line in enumerate(sel['cores']):
    for c,ident in enumerate(line):
        assert ident; p=ZONE/'native'/f'{ident}.png'; g=read(p.with_suffix('.png.generation.json')); im=Image.open(p)
        assert im.size==(1254,1254) and sha(p)==g['sha256'] and g['coreCrop']==[115,115,1139,1139]
        assert g['coreWorldBox']==[ox+c*1024,oy+r*1024,ox+(c+1)*1024,oy+(r+1)*1024]
        out.paste(im.crop((115,115,1139,1139)),(c*1024,r*1024)); cover[r*1024:(r+1)*1024,c*1024:(c+1)*1024]+=1
        sources.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':g['coreCrop'],'tileLocalPaste':[c*1024,r*1024],'nativeSize':list(im.size)})
overlays=[]
for ident in sel['overlays']:
    q=read(ZONE/'qa'/f'{ident}.overlay.json'); assert q['review'].startswith('passed_') and sha(q['source'])==q['sha256']
    out.paste(Image.open(q['source']).crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste'])); overlays.append(q)
assert (cover==1).all(); out.save(dest); out.resize((1536,1536),Image.Resampling.LANCZOS).save(preview); qdir.mkdir()
for r in range(4):
    for c in range(4): out.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(qdir/f'core-{r+1}-{c+1}-100pct.png')
for i in range(1,4):
    for j in range(4):
        out.crop((i*1024-128,j*1024,i*1024+128,(j+1)*1024)).save(qdir/f'vertical-{i}-segment-{j+1}-100pct.png')
        out.crop((j*1024,i*1024-128,(j+1)*1024,i*1024+128)).save(qdir/f'horizontal-{i}-segment-{j+1}-100pct.png')
for r in range(1,4):
    for c in range(1,4): out.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(qdir/f'cross-{r}-{c}-100pct.png')
external=[]
for side,neighbor in [('upper',f'r{row-1:02}_c{col:02}'),('left',f'r{row:02}_c{col-1:02}')]:
    ns=ZONE/f'selection-{neighbor}.json'; nd=read(ns) if ns.exists() else {}
    npth=Path(nd.get('candidatePath',ZONE/'tiles'/f'{neighbor}.png'))
    if not npth.exists(): external.append({'side':side,'neighbor':neighbor,'status':'pending adjacent tile assembly'}); continue
    ni=Image.open(npth).convert('RGB'); assert ni.size==(4096,4096)
    for j in range(4):
        if side=='upper':
            joined=Image.new('RGB',(1024,256)); joined.paste(ni.crop((j*1024,3968,(j+1)*1024,4096)),(0,0)); joined.paste(out.crop((j*1024,0,(j+1)*1024,128)),(0,128))
        else:
            joined=Image.new('RGB',(256,1024)); joined.paste(ni.crop((3968,j*1024,4096,(j+1)*1024)),(0,0)); joined.paste(out.crop((0,j*1024,128,(j+1)*1024)),(128,0))
        joined.save(qdir/f'external-{side}-segment-{j+1}-100pct.png')
    external.append({'side':side,'neighbor':neighbor,'file':npth.as_posix(),'sha256':sha(npth),'status':'pending complete4096 boundary visual review'})
record={'tileId':tid,'file':dest.as_posix(),'sha256':sha(dest),'size':[4096,4096],'worldBox':[ox,oy,ox+4096,oy+4096],'operation':'16 exact native1024 core crops plus recorded repair overlays, no resampling or feathering','sources':sources,'requiredOverlays':overlays,'baseCoverageMin':1,'baseCoverageMax':1,'uncoveredPixels':0,'finalArtUpscaled':False,'status':'complete_native_coverage_pending_whole_tile_QA','internalReview':'pending16core24seam9cross','externalSeams':external,'formalAccepted':False,'actualModel':None,'actualQuality':None,'generatedAtUtc':now(),'preview':preview.as_posix(),'inspectionCrops':qdir.as_posix()}
write(dest.with_suffix('.png.derivation.json'),record); sel.update(candidatePath=dest.as_posix(),candidateSha256=record['sha256'],preview=preview.as_posix(),inspectionCrops=qdir.as_posix(),updatedAtUtc=now()); write(ZONE/f'selection-{tid}.json',sel)
print(json.dumps({'file':dest.as_posix(),'sha256':record['sha256'],'inspectionCrops':qdir.as_posix()}))

