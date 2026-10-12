import sys,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_s03_01_v03';base=ROOT/'native/r10_c04_s03_01_v02.png'
req=p.load(ROOT/'prompts/r10_c04_s03_01_v02.request.json');box=req['coordinates']['nativeGlobalBox']
im=Image.open(base).convert('RGB');sources=[p.metadata(base,'native edit target')]
for n in ['r10_c04_s03_02_v02','r10_c04_wall_col12_join_v01']:
    fp=ROOT/'native'/f'{n}.png';b=p.load(str(fp)+'.generation.json')['coordinates']['nativeGlobalBox']
    ib=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
    crop=[ib[0]-b[0],ib[1]-b[1],ib[2]-b[0],ib[3]-b[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
    im.paste(Image.open(fp).crop(crop),dest);sources.append({**p.metadata(fp,'native correct constraint'),'sourceCrop':crop,'destinationTopLeft':dest})
gp=ROOT/'guides'/f'{stem}.native-repair-guide.png';im.save(gp)
p.dump(str(gp)+'.derivation.json',{'operation':'mechanical same-coordinate native edits guide; no resize or recolor','sources':sources,'sha256':p.hashfile(gp)})
req['references'][0]=p.metadata(gp,'native exact edit target with correct RIGHT constraint')
req['references'][1]=p.metadata(ROOT/'native/r10_c04_s03_02_v02.png','RIGHT native geometry context: single wall plinth and gold rim position')
p.dump(ROOT/'prompts'/f'{stem}.request.json',req);p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',req['coordinates'])
print(json.dumps(req))

