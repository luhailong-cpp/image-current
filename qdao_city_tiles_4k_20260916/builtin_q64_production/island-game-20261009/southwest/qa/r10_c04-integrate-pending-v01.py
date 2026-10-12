import sys,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
import native_multi_tile_repair as m
prefix='c04-int-wall-v01-r10_c04'
steps=[
('r10_c04_postfoot_join_v01','c04-int-foot-v01',[[220,250,1254,1254]],[[380,403,1000,803]],[]),
('r10_c04_wallbase_col12_join_v01','c04-int-wallbase-v01',[[120,300,950,1254]],[[400,503,700,1139]],[]),
('r10_c04_roofcurve_join_v02','c04-int-roof-v01',[[0,150,1254,1139]],[[386,250,686,1139]],['bottom']),
('r10_c04_lowrib_col12_join_v01','c04-int-lowrib-v01',[[300,850,1000,1254]],[[430,1050,750,1254]],['bottom'])]
for stem,out,rois,targets,flush in steps:
    specs=[[ROOT/'qa'/f'{prefix}-candidate-4096.png',ROOT/'qa'/f'{prefix}-source-id-mask.png',ROOT/'qa'/f'{prefix}-report.json']]
    result=m.apply_repair(specs,stem,out,70,rois,targets,False,flush)
    prefix=out+'-r10_c04'
    print(json.dumps({'stem':stem,'prefix':prefix,'validation':result['tiles'][0]['validation']}),flush=True)
im=Image.open(ROOT/'qa'/f'{prefix}-candidate-4096.png')
im.resize((1254,1254),Image.Resampling.LANCZOS).save(ROOT/'qa'/f'{prefix}-preview-QA-only.png')
for label,box in [('wall',[300,900,1700,2300]),('wallbase',[420,2100,1750,3260]),('foot',[1350,2150,2650,3375]),('roof',[1400,3030,2860,4096]),('lowrib',[550,3400,1850,4096])]:
    im.crop(box).save(ROOT/'qa'/f'{prefix}-{label}-native100.png')
print(json.dumps({'finalPrefix':prefix}),flush=True)

