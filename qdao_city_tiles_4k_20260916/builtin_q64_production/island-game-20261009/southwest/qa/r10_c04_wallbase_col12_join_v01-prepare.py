from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
stem='r10_c04_wallbase_col12_join_v01';box=[12750,38797,14004,40051]
canvas=Image.new('RGB',(1254,1254));cover=Image.new('L',(1254,1254),0);sources=[]
for s,nb,ib in [('r10_c04_s03_01_v03',[12173,38797,13427,40051],[12750,38797,13312,40051]),('r10_c04_s03_02_v02',[13197,38797,14451,40051],[13312,38797,14004,40051]),('r10_c04_postfoot_join_v01',[13500,38797,14754,40051],[13500,38797,14004,40051]),('r10_c04_wall_col12_join_v01',[12685,37773,13939,39027],[12750,38797,13939,39027])]:
    f=R/'native'/(s+'.png');actual=p.load(str(f)+'.generation.json')['coordinates']['nativeGlobalBox'];assert actual==nb
    crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
    canvas.paste(Image.open(f).crop(crop),dest);cover.paste(255,(dest[0],dest[1],dest[0]+ib[2]-ib[0],dest[1]+ib[3]-ib[1]))
    sources.append({**p.metadata(f,'same-coordinate actual AI native source in guide'),'sourceCrop':crop,'destinationTopLeft':dest,'intersectionGlobalBox':ib})
assert cover.getextrema()==(255,255)
guide=R/'guides'/(stem+'.native-guide.png');assert not guide.exists();canvas.save(guide)
co={'tile':'r10_c04','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254],'repairTargetGlobalBox':[13150,39300,13450,39936],'repairTargetLocalBox':[400,503,700,1139],'repairKind':'col1/2 whole wall base and gold disk edge continuity','bottomSeedGlobalBox':[12750,39821,14004,40051]}
p.dump(R/'prompts'/(stem+'.coordinates.json'),co)
p.dump(str(guide)+'.derivation.json',{'operation':'native same-global crop/paste guide only; whole-foot corrected RIGHT contribution and walltop last; no interpolation or retouch','sources':sources,'coordinates':co,'sha256':p.hashfile(guide),'completeCoverage':True})
refs=[p.metadata(guide,'exact-coordinate edit target'),p.metadata(R/'guides/r10_c04_s03_02_v02.postfoot-context.png','correct RIGHT context with true wall/plinth/gold-disk edge heights; no translation')]+[p.metadata(*a) for a in p.REFS]
p.dump(R/'prompts'/(stem+'.request.json'),{'tool':'image_gen.imagegen','createdAtUtc':p.now(),'coordinates':co,'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'sourceAssembly':sources})
for ref in refs:assert p.hashfile(ref['path'])==ref['sha256']
print({'guide':guide.as_posix(),'globalBox':box,'references':[x['path'] for x in refs]})
