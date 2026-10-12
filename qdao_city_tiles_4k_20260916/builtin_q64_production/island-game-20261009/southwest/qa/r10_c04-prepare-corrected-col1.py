import sys,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_s03_01_v02'
reqpath=ROOT/'prompts'/f'{stem}.request.json'
req=p.load(reqpath);box=req['coordinates']['nativeGlobalBox']
gp=ROOT/'guides'/f'{stem}.native-overlap-guide.png'
im=Image.open(gp).convert('RGB')
der=p.load(str(gp)+'.derivation.json')
for n,role in [('r10_c04_s03_02_v02','actual right native structural base'),('r10_c04_wall_col12_join_v01','corrected top wall source, same-coordinate continuation')]:
    fp=ROOT/'native'/f'{n}.png';rec=p.load(str(fp)+'.generation.json');b=rec['coordinates']['nativeGlobalBox']
    ib=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
    if ib[2]>ib[0] and ib[3]>ib[1]:
        crop=[ib[0]-b[0],ib[1]-b[1],ib[2]-b[0],ib[3]-b[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
        im.paste(Image.open(fp).crop(crop),dest);der['sources'].append({**p.metadata(fp,role),'sourceCrop':crop,'destinationTopLeft':dest})
im.save(gp);der['sha256']=p.hashfile(gp);p.dump(str(gp)+'.derivation.json',der)
req['references'][0]=p.metadata(gp,'native TOP corrected wall, LEFT and RIGHT exact same-coordinate constraints; remainder layout only')
req['references'][1]=p.metadata(ROOT/'native/r10_c03_s03_04_v01.png','actual LEFT native finial cone context; guide coordinates lock size')
p.dump(reqpath,req)
co=p.load(ROOT/'prompts/r10_c04_wall_col12_join_v01.coordinates.json')
p.dump(ROOT/'qa/r10_c04_wall_col12_join_v01-handoff.json',{'source':'native/r10_c04_wall_col12_join_v01.png','sha256':p.hashfile(ROOT/'native/r10_c04_wall_col12_join_v01.png'),'globalBox':co['nativeGlobalBox'],'roi':[0,380,1254,1254],'mandatoryTarget':[0,520,800,1254],'base':'r10_c04_s02_01_v02','status':'native visually accepted repair; pending root integration','notes':'Right cap height held; left cap lowered to continuity, wrong inset vertical edge removed. Gold finial retained. Bottom corrected source used directly for next TOP guide. No resampling or recoloring.'})
print(json.dumps(req))

