from pathlib import Path
import sys, shutil
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
mode,ident=sys.argv[1:3]
assert ident.startswith('r03_c11_cross_')
if mode=='prepare':
    x,y=map(int,sys.argv[3:5]); src=ZONE/'tiles/r03_c11.png'; tile=Image.open(src).convert('RGB'); d=read(src.with_suffix('.png.derivation.json'))
    box=[x-115,y-115,x+1139,y+1139]; dest=ZONE/'guides'/f'{ident}.png'; assert not dest.exists(); tile.crop(box).save(dest)
    q={'operation':'exact native assembled tile crop, no resampling','sourceTile':src.as_posix(),'sourceTileSha256':sha(src),'sources':d['sources'],'priorOverlays':d['requiredOverlays'],'tileLocalBox':box,'tileLocalPaste':[x,y],'nativeWorldBox':[40960+box[0],8192+box[1],40960+box[2],8192+box[3]],'coreWorldBox':[40960+x,8192+y,40960+x+1024,8192+y+1024],'coreCrop':[115,115,1139,1139],'finalArt':False};write(dest.with_suffix('.png.derivation.json'),q)
    refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target, exact native assembled tile crop to repair interior geometry; all four outer edges fixed','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()}];write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
    print(dest.as_posix())
elif mode=='preview':
    d=read(ZONE/'guides'/f'{ident}.png.derivation.json'); x,y=d['tileLocalPaste']; p=ZONE/'native'/f'{ident}.png'; im=Image.open(p).convert('RGB'); assert im.size==(1254,1254)
    original=Image.open(ZONE/'tiles/r03_c11.png').convert('RGB'); original.paste(im.crop((115,115,1139,1139)),(x,y)); dest=ZONE/'qa'/f'{ident}-candidate.png'; original.save(dest)
    for side,b in {'top':[x,y-128,x+1024,y+128],'bottom':[x,y+896,x+1024,y+1152],'left':[x-128,y,x+128,y+1024],'right':[x+896,y,x+1152,y+1024]}.items():original.crop(b).save(ZONE/'qa'/f'{ident}-{side}-100pct.png')
    write(ZONE/'qa'/f'{ident}.overlay.json',{'operation':'exact native core overlay, no scaling or feathering','source':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[x,y],'worldPaste':[40960+x,8192+y],'review':'pending four edge and interior review','targetMosaic':dest.as_posix()})
    print(dest.as_posix())
elif mode=='merge':
    p=ZONE/'qa'/f'{ident}.overlay.json'; d=read(p); d['review']='passed_native_interior_and_four_perimeters';d['reviewedAtUtc']=now();write(p,d)
    p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d['status']='passed_native_interior_and_four_perimeters';write(p,d)
    src=ZONE/'tiles/r03_c11.png';hist=ZONE/'qa/history'/('r03_c11-'+sha(src)[:12]+'-before-'+ident);hist.mkdir(exist_ok=False);shutil.copy2(src,hist/src.name);shutil.copy2(src.with_suffix('.png.derivation.json'),hist/'r03_c11.png.derivation.json');shutil.copy2(ZONE/'selection-r03_c11.json',hist/'selection-r03_c11.json')
    p=ZONE/'selection-r03_c11.json';d=read(p);d['overlays'].append(ident);d['updatedAtUtc']=now();write(p,d)
    print('passed repair selected; previous candidate archived')
