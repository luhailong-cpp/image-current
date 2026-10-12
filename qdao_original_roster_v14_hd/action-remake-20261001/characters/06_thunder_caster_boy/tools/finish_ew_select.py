"""Select visually inspected E/W poses without changing their common camera."""
from pathlib import Path
import json,hashlib,copy
from PIL import Image
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected={}
for d in ['E','W']:
 for i in [2,3,4,5,6,7,11,12,13,14,15]:
  v=2 if d=='W' and i in [7,13,14,15] else 1
  selected[f'{d}/{i:02}']=f'run_{d}_{i:02}_progress_v{v}'
for key,stem in selected.items():
 d,num=key.split('/');src=R/'work'/f'{stem}.png';sg=src.with_name(src.name+'.generation.json')
 native=Image.open(src).convert('RGBA');assert native.size==(1254,1254)
 g=json.loads(sg.read_text(encoding='utf-8-sig'));dst=R/f'runtime/run/{key}.png';rg=dst.with_name(dst.name+'.generation.json')
 old=json.loads(rg.read_text(encoding='utf-8-sig'))
 if old['derivedFrom'][0]['sha256']==sha(src):continue
 (R/'records'/f'run_{d}_{num}_before_progress_{old["sha256"][:12]}.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
 image=Image.new('RGBA',(1024,1024));image.alpha_composite(native.resize((901,901),Image.Resampling.LANCZOS),(61,97));image.save(dst)
 new=copy.deepcopy(old);new.update(file=dst.relative_to(R).as_posix(),sha256=sha(dst),width=1024,height=1024,mode='RGBA',format='PNG',native=g['native'],generatedAt=g['generatedAt'],actualModel=None,actualQuality=None,unverifiedReason=g['unverifiedReason'],derivedFrom=[{'file':src.relative_to(R).as_posix(),'sha256':sha(src),'generationRecord':sg.relative_to(R).as_posix()}],operation='Uniform full-native-canvas resize 1254 to 901 then place at fixed (61,97) in 1024 RGBA. Same camera for all E/W frames, no bbox-derived parameters, per-frame alignment, mirroring or anatomy modification.',visualReview='实际查看原生单帧与同向序列表后选用；膝踝脚轴按E向右/W向左，连续支撑从前方移至身下及后蹬。两帧位置段实际记录见review/run_EW_contactpairs_20261004.json。')
 new['cameraRegistration']['sourceNativeSha256']=sha(src)
 new['cameraRegistration']['resampledSize']=[901,901];new['cameraRegistration']['placement']=[61,97]
 new['cameraRegistration']['matrixNativeToRuntime']=[[901/1254,0,61],[0,901/1254,97],[0,0,1]]
 rg.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
 g.update(exported=True,exportPath=dst.relative_to(R).as_posix(),visualReview=new['visualReview']);sg.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
 print(key,stem,sha(dst))
