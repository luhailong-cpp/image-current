"""Select one inspected run E/W native using the established camera."""
from pathlib import Path
import sys,json,hashlib,copy
from PIL import Image
R=Path(__file__).resolve().parents[1];stem=sys.argv[1];note=sys.argv[2]
a,d,n=stem.split('_')[:3];assert a=='run' and d in ['E','W']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=R/'work'/f'{stem}.png';sg=src.with_name(src.name+'.generation.json');g=json.loads(sg.read_text(encoding='utf-8-sig'))
im=Image.open(src).convert('RGBA');assert im.size==(1254,1254)
dst=R/f'runtime/run/{d}/{n}.png';rg=dst.with_name(dst.name+'.generation.json');old=json.loads(rg.read_text(encoding='utf-8-sig'))
(R/'records'/f'run_{d}_{n}_before_full_limb_{old["sha256"][:12]}.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((901,901),Image.Resampling.LANCZOS),(61,97));out.save(dst)
new=copy.deepcopy(old);new.update(file=dst.relative_to(R).as_posix(),sha256=sha(dst),width=1024,height=1024,mode='RGBA',format='PNG',native=g['native'],generatedAt=g['generatedAt'],actualModel=None,actualQuality=None,unverifiedReason=g['unverifiedReason'],derivedFrom=[{'file':src.relative_to(R).as_posix(),'sha256':sha(src),'generationRecord':sg.relative_to(R).as_posix()}],operation='Uniform full-native-canvas resize1254 to901 then fixed placement(61,97); shared E/W camera; no bbox fit, warp, mirroring or interpolation.',visualReview=note)
new['cameraRegistration'].update(sourceNativeSha256=sha(src),resampledSize=[901,901],placement=[61,97],matrixNativeToRuntime=[[901/1254,0,61],[0,901/1254,97],[0,0,1]])
rg.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
g.update(exported=True,exportPath=dst.relative_to(R).as_posix(),visualReview=note);sg.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':new['file'],'sha256':new['sha256']}))

