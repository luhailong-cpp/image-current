from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
stem='r10_c04_roofcurve_join_v01';box=[13800,39821,15054,41075]
canvas=Image.new('RGB',(1254,1254));cover=Image.new('L',(1254,1254),0);sources=[]
for s,x0,x1 in [('r10_c04_s04_02_v02',13800,14336),('r10_c04_s04_03_v01',14336,15054)]:
    f=R/'native'/(s+'.png');rec=p.load(str(f)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox'];ib=[x0,box[1],x1,box[3]]
    crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],0]
    canvas.paste(Image.open(f).crop(crop),dest);cover.paste(255,(dest[0],0,dest[0]+x1-x0,1254))
    sources.append({**p.metadata(f,'same-coordinate selected/base core plus vertical native halos'),'sourceCrop':crop,'destinationTopLeft':dest,'intersectionGlobalBox':ib})
assert cover.getextrema()==(255,255)
guide=R/'guides'/(stem+'.native-guide.png');assert not guide.exists();canvas.save(guide)
co={'tile':'r10_c04','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254],'repairTargetGlobalBox':[14186,40071,14486,41031],'repairTargetLocalBox':[386,250,686,1210],'repairKind':'whole curved gold/red eave and cylindrical blue tile row continuity across col2/3'}
p.dump(R/'prompts'/(stem+'.coordinates.json'),co)
p.dump(str(guide)+'.derivation.json',{'operation':'same-global native crop/paste only, no interpolation or color operation','sources':sources,'coordinates':co,'sha256':p.hashfile(guide),'completeCoverage':True})
refs=[p.metadata(guide,'exact-coordinate whole-curve edit target'),p.metadata(R/'native/r10_c04_s04_03_v01.png','right native context fixes scroll and gold rim geometry, no scale/shift')]+[p.metadata(*a) for a in p.REFS]
p.dump(R/'prompts'/(stem+'.request.json'),{'tool':'image_gen.imagegen','createdAtUtc':p.now(),'coordinates':co,'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'sourceAssembly':sources})
p.dump(R/'qa/r10_c04_s04_02_v02-review.json',{'status':'structure_clear_base_pending_whole_repair','reason':'RIGHT gold/red/blue joint remains about100px offset; must integrate whole-curve source before formal acceptance.','repairStem':stem})
print({'guide':guide.as_posix(),'references':[x['path'] for x in refs]})
