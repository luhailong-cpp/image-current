from pathlib import Path
from PIL import Image
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_postfoot_join_v01';box=[13500,38797,14754,40051]
stems=['r10_c04_s02_02_v01','r10_c04_s02_03_v02','r10_c04_s03_02_v02','r10_c04_s03_03_v01']
canvas=Image.new('RGB',(1254,1254));cover=Image.new('L',(1254,1254),0);sources=[]
for s in stems:
 f=ROOT/'native'/(s+'.png');rec=p.load(str(f)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox'];cb=list(rec['coordinates']['coreGlobalBox'])
 if rec['coordinates']['subrow']==3:cb[3]=nb[3]
 ib=[max(box[0],cb[0]),max(box[1],cb[1]),min(box[2],cb[2]),min(box[3],cb[3])]
 assert ib[0]<ib[2] and ib[1]<ib[3]
 crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
 with Image.open(f) as im:canvas.paste(im.crop(crop),dest)
 cover.paste(255,(dest[0],dest[1],dest[0]+ib[2]-ib[0],dest[1]+ib[3]-ib[1]))
 sources.append({**p.metadata(f,'selected/base native same-global core contribution'),'sourceCrop':crop,'destinationTopLeft':dest,'intersectionGlobalBox':ib})
assert cover.getextrema()==(255,255)
guide=ROOT/'guides'/(stem+'.native-guide.png');assert not (ROOT/'receipts'/(stem+'.tool.json')).exists();canvas.save(guide)
co={'tile':'r10_c04','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254],'repairTargetGlobalBox':[13880,39200,14500,39600],'repairTargetLocalBox':[380,403,1000,803],'repairKind':'whole post foot, platform and shared col2-col3 seam geometry','bottomCoverage':'last 115 rows use sr3 native halo, reaching y40051 to seed sr4 TOP'}
p.dump(ROOT/'prompts'/(stem+'.coordinates.json'),co)
p.dump(str(guide)+'.derivation.json',{'operation':'native same-global core crop/paste, extending sr3 bottom native halo to y40051; no interpolation, feather, color or reposition','sources':sources,'coordinates':co,'sha256':p.hashfile(guide),'completeCoverage':True})
refs=[p.metadata(guide,'exact-coordinate whole-object repair canvas'),p.metadata(ROOT/'native'/'r10_c04_s03_02_v02.png','native left object context; correct TOP and wall, wrong right base height')]+[p.metadata(*r) for r in p.REFS]
p.dump(ROOT/'prompts'/(stem+'.request.json'),{'tool':'image_gen.imagegen','createdAtUtc':p.now(),'coordinates':co,'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'sourceAssembly':sources})
print({'stem':stem,'globalBox':box,'refs':[r['path'] for r in refs]})

