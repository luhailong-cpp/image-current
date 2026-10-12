from pathlib import Path
import runpy, json, argparse, hashlib
from PIL import Image
import numpy as np
root=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest')
qa=root/'r11_c05'/'qa'/'boundary-review-20261010'
qa.mkdir(parents=True,exist_ok=True)
b=root/'r11_c05'/'borders'
api=runpy.run_path(str(root/'border_assembly.py'),run_name='readonly_boundary_review')
snapshot=api['Snapshot']()
assembly,algo=api['load_algorithm'](snapshot)
sources,source_record=api['native_sources'](root/'r11_c05',range(1,2),snapshot)
context,metrics=assembly['assemble_pixels'](sources,(1,1,1,4),2)
snapshot.check()
context_path=b/'r11-p01.original.context.png'
if context_path.exists():
    assert np.array_equal(api['read_png'](context_path),context)
else:
    api['save_png'](context_path,context)
final10=root/'r10_c05'/'repairs'/'output'/'r10_c05.repaired.candidate.png'
r10hash=api['digest'](final10)
output=b/'r11-p01.north-fixed.context.png'
if not output.exists():
    result=api['run'](argparse.Namespace(self_test=False,prepare_only=False,input=str(context_path),output=str(output),feather=2,context_feather=2))
else:
    result={'status':'using_existing_unmodified_output','record':str(output.with_suffix('.border.json'))}
fixed=api['read_png'](output)
old_core=context[115:1139,115:4211]
new_core=fixed[115:1139,115:4211]
r10=api['read_png'](final10)
paths=[]
for name,core in [('before',old_core),('after',new_core)]:
    joined=np.concatenate((r10[-320:],core[:480]),axis=0)
    path=qa/f'north-boundary-{name}.png'
    Image.fromarray(joined).save(path,optimize=True)
    paths.append(str(path))
    for c in range(4):
        path=qa/f'north-boundary-{name}-c{c+1}.png'
        Image.fromarray(joined[:,c*1024:(c+1)*1024]).save(path,optimize=True)
    for x in (1024,2048,3072):
        path=qa/f'first-row-vertical-seam-{x}-{name}.png'
        Image.fromarray(core[:,x-256:x+256]).save(path,optimize=True)
Image.fromarray(new_core).save(b/'r11-p01.north-fixed.core.png',optimize=True)
assert api['digest'](final10)==r10hash
record={'context':str(context_path),'fixedContext':str(output),'fixedCore':str(b/'r11-p01.north-fixed.core.png'),'beforeAfterBoundaryCrops':paths,'r10FinalSha256Unchanged':r10hash,'sourceNativeUnchanged':True,'newPixelsGenerated':False,'resized':False,'visualQa':'pending','mechanicalResult':result,'contextReplayExact':True,'fixedCorePixels':[4096,1024]}
(qa/'mechanical-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
