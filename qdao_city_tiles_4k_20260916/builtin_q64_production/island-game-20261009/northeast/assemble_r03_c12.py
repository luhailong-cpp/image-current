from native_work import *
import numpy as np
ids=[['r03_c12_p01_01','r03_c12_p01_02_v2','r03_c12_p01_03','r03_c12_p01_04'],['r03_c12_p02_01_v2','r03_c12_p02_02_v2','r03_c12_p02_03','r03_c12_p02_04_v2'],['r03_c12_p03_01','r03_c12_p03_02','r03_c12_p03_03_v2','r03_c12_p03_04_v2'],['r03_c12_p04_01','r03_c12_p04_02','r03_c12_p04_03','r03_c12_p04_04']]
out=Image.new('RGB',(4096,4096)); sources=[]; coverage=np.zeros((4096,4096),dtype='uint8')
for row,line in enumerate(ids):
    for col,ident in enumerate(line):
        p=ZONE/'native'/f'{ident}.png'; im=Image.open(p); assert im.size==(1254,1254)
        out.paste(im.crop((115,115,1139,1139)),(col*1024,row*1024)); coverage[row*1024:(row+1)*1024,col*1024:(col+1)*1024]+=1
        sources.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[col*1024,row*1024],'nativeSize':[1254,1254]})
overlays=[]
for overlay_id in ['r03_c12_cross_02_02_repair','r03_c12_cross_01_01_repair','r03_c12_cross_01_02_repair']:
    overlay=read(ZONE/'qa'/f'{overlay_id}.overlay.json'); assert overlay['review'].startswith('passed_')
    out.paste(Image.open(overlay['source']).crop(tuple(overlay['coreCrop'])),tuple(overlay['tileLocalPaste'])); overlays.append(overlay)
dest=ZONE/'tiles/r03_c12.png'; out.save(dest)
out.resize((1536,1536),Image.Resampling.LANCZOS).save(ZONE/'qa/r03_c12-preview.png')
qa=ZONE/'qa/r03_c12-final'; qa.mkdir(exist_ok=True)
for r in range(4):
    for c in range(4): out.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(qa/f'core-{r+1}-{c+1}-100pct.png')
for i in range(1,4):
    for j in range(4):
        out.crop((i*1024-128,j*1024,i*1024+128,(j+1)*1024)).save(qa/f'vertical-{i}-segment-{j+1}-100pct.png')
        out.crop((j*1024,i*1024-128,(j+1)*1024,i*1024+128)).save(qa/f'horizontal-{i}-segment-{j+1}-100pct.png')
for r in range(1,4):
    for c in range(1,4): out.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(qa/f'cross-{r}-{c}-100pct.png')
record={'tileId':'r03_c12','file':dest.as_posix(),'sha256':sha(dest),'size':[4096,4096],'worldBox':[45056,8192,49152,12288],'operation':'16 native1024 core crops tiled without resampling; three native1024 joint geometry/color repair overlays; no feathering','sources':sources,'requiredOverlays':overlays,'baseCoverageMin':int(coverage.min()),'baseCoverageMax':int(coverage.max()),'uncoveredPixels':int((coverage==0).sum()),'finalArtUpscaled':False,'status':'complete_native_coverage_pending_whole_tile_QA','internalReview':'pending','externalSeams':'pending adjacent4k tiles','formalAccepted':False,'actualModel':None,'actualQuality':None,'generatedAtUtc':now(),'preview':(ZONE/'qa/r03_c12-preview.png').as_posix(),'inspectionCrops':qa.as_posix()}
write(dest.with_suffix('.png.derivation.json'),record)
print(json.dumps({'file':dest.as_posix(),'sha256':record['sha256'],'uncoveredPixels':record['uncoveredPixels'],'size':record['size']},ensure_ascii=False))
