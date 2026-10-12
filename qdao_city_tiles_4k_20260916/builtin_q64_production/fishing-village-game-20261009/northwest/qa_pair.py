from pathlib import Path
from PIL import Image
import numpy as np,json,argparse
from assemble_r03_c03 import append_hard,sha
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('a');ap.add_argument('b');ap.add_argument('direction',choices=['h','v']);ap.add_argument('out');args=ap.parse_args()
a,b=[np.array(Image.open(ROOT/'native'/f'{p}.png').convert('RGB')) for p in [args.a,args.b]]
if args.direction=='v':a,b=a.transpose(1,0,2),b.transpose(1,0,2)
joined,ids,record=append_hard(a,np.ones(a.shape[:2],np.uint8),b,np.full(b.shape[:2],2,np.uint8),args.out)
if args.direction=='v':joined=joined.transpose(1,0,2)
out=ROOT/args.out;out.parent.mkdir(parents=True,exist_ok=True)
record['sources']=[{'file':str(ROOT/'native'/f'{p}.png'),'sha256':sha(ROOT/'native'/f'{p}.png')} for p in [args.a,args.b]]
for i in range(2):
 box=[900,627*i,1400,627*(i+1)] if args.direction=='h' else [627*i,900,627*(i+1),1400]
 dst=str(out)+f'-segment{i+1}.png';Image.fromarray(joined).crop(box).save(dst)
 record.setdefault('crops',[]).append({'file':dst,'crop':box})
Path(str(out)+'.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'crops':record['crops'],'MAE':record['overlapMeanAbsoluteRGB']}))
