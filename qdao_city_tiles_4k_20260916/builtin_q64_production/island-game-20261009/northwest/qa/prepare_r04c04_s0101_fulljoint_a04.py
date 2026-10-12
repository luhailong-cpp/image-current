from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib
Z=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
stem='r04_c04_s01_01_a04'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=read(Z/'guides/r04_c04_s01_01_a03.input.json')
base=Z/'native/r04_c04_s01_01_a03.png'
left=Z/'native/r04_c03_s01_04_a02.png'
top=Z/'native/r03_c04_s04_01_a01.png'
a=np.array(Image.open(base).convert('RGB'))
a[:,:230]=np.array(Image.open(left).convert('RGB'))[:,1024:]
a[:230]=np.array(Image.open(top).convert('RGB'))[1024:]
out=Z/'guides'/f'{stem}.native-joint-edit.png'
assert not out.exists()
Image.fromarray(a).save(out)
srcs=[{'path':p.as_posix(),'sha256':sha(p),'generationRecord':{'path':str(p)+'.generation.json','sha256':sha(str(p)+'.generation.json')}} for p in (base,left,top)]
der=Z/'guides'/f'{stem}.native-joint-edit.derivation.json'
write(der,{'operation':'same-coordinate exact native hard paste for image-generation edit target only','sources':srcs,'baseSource':0,'pasteOrder':[{'source':1,'sourceCrop':[1024,0,1254,1254],'destination':[0,0]},{'source':2,'sourceCrop':[0,1024,1254,1254],'destination':[0,0]}],'nativeSize':[1254,1254],'globalBox':old['globalBox'],'allPixelsExactlyCopied':True,'resizing':False,'feathering':False,'colorCorrection':False,'output':{'path':out.as_posix(),'sha256':sha(out)},'notFinalArt':True})
target={'path':out.as_posix(),'sha256':sha(out),'nativeSize':[1254,1254],'role':'edit target with explicit wrong fence/post interior and exact left/top native strips; repair entire fence object and all entry/exit boundaries to image 5 guide','derivedFrom':srcs,'derivationRecord':{'path':der.as_posix(),'sha256':sha(der)}}
refs=[target]+old['inputs'][1:4]+[old['inputs'][0]]
rec={k:v for k,v in old.items() if k not in ['inputs','versionStem','attempt','imageGenReferencedImagePaths','guideDerivation','operation']}
rec.update(versionStem=stem,attempt='a04',inputs=refs,imageGenReferencedImagePaths=[r['path'] for r in refs],editTarget=target,layoutGuide=old['inputs'][0],operation='entire visible fence/post joint reconstruction from native edit target and original layout guide; fixed neighbor entrance edges')
write(Z/'guides'/f'{stem}.input.json',rec)
write(Z/'guides'/f'{stem}.references.json',refs)
print(json.dumps({'editTarget':str(out),'refs':[r['path'] for r in refs]}))

