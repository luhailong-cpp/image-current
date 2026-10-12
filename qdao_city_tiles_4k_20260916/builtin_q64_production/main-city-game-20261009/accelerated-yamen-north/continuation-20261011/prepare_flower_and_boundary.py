import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent
# QA west boundaries against frozen left tiles after new east-column repair
out=HERE/'merged-south-v3'
for top in ('r03','r04'):
 left=next((ROOT/(top+'_c04')/'candidate').glob('*'+('424e41dd0ce0' if top=='r03' else '71cabb17b21f')+'.png'))
 right=ROOT/(top+'_c05')/'continuation-20261011/south-v3/integrated-candidate-native.png'
 a=Image.open(left).convert('RGB');b=Image.open(right).convert('RGB')
 ys=(3072,4096) if top=='r03' else (0,1024)
 q=Image.new('RGB',(320,1024));q.paste(a.crop((3936,ys[0],4096,ys[1])),(0,0));q.paste(b.crop((0,ys[0],160,ys[1])),(160,0))
 p.save_png(out/(top+'-west-changed-native.png'),q.transpose(Image.Transpose.ROTATE_90))
d=HERE/'flower-return01';d.mkdir(exist_ok=True)
f=ROOT/'r03_c05/continuation-20261011/south-v3/integrated-candidate-native.png';box=[400,2842,1654,4096]
p.save_png(d/'context-native.png',Image.open(f).crop(box))
p.put_json(d/'preparation.json',{'tile':'r03_c05','sourceCandidate':str(f),'sourceSHA256':p.sha(f),'tileBox':box,'worldBox':[16784,11034,18038,12288],'nativePixels':[1254,1254],'resized':False,'defect':'D3 duplicate circular eave flower at tile x1024 y3440..3590; confined repair only'})
print(d)

