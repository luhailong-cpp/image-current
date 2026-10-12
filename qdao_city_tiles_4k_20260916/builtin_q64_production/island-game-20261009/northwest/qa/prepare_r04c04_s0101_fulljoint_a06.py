from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stem='r04_c04_s01_01_a06'
old=read(Z/'guides/r04_c04_s01_01_a05.input.json')
guide=Path(old['inputs'][4]['path']);src=Z/'native/r04_c04_s01_01_a05.png'
a=np.array(Image.open(guide).convert('RGB'));b=np.array(Image.open(src).convert('RGB'))
a[230:650,230:]=b[230:650,230:]
a[750:1080,760:1090]=b[750:1080,760:1090]
out=Z/'guides'/f'{stem}.whole-fence-reconstruct-guide.png';assert not out.exists();Image.fromarray(a).save(out)
der=Z/'guides'/f'{stem}.whole-fence-reconstruct-guide.derivation.json'
sources=[{'path':p.as_posix(),'sha256':sha(p)} for p in (guide,src)]
write(der,{'operation':'exact coordinate source selection for AI guide only; expose original layout of entire incorrect fence while retaining corrected native sphere and upper paving','sources':sources,'baseSource':0,'nativeSource':1,'nativePreservedRectangles':[[230,230,1254,650],[760,750,1090,1080]],'nativeSize':[1254,1254],'globalBox':old['globalBox'],'allPixelsExactlyCopiedFromNamedSources':True,'resizing':False,'feathering':False,'pixelPainting':False,'layoutPixelsForbiddenInFinal':True,'output':{'path':out.as_posix(),'sha256':sha(out)}})
target={'path':out.as_posix(),'sha256':sha(out),'nativeSize':[1254,1254],'role':'reconstruct complete blurred fence at original low position while preserving exact native neighbor edges and corrected native ball; guide only, no final pixels','derivationRecord':{'path':der.as_posix(),'sha256':sha(der)},'derivedFrom':sources}
refs=[target]+old['inputs'][1:]
rec={k:v for k,v in old.items() if k not in ['versionStem','attempt','inputs','editTarget','imageGenReferencedImagePaths','operation']}
rec.update(versionStem=stem,attempt='a06',inputs=refs,editTarget=target,imageGenReferencedImagePaths=[r['path'] for r in refs],operation='full-fence reconstruction with incorrect native railing removed from guide')
write(Z/'guides'/f'{stem}.input.json',rec);write(Z/'guides'/f'{stem}.references.json',refs)
print(out)

