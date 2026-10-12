from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
which=int(sys.argv[1]);assert which in (1,2)
stem=f'r09_r10_c04_court_join{which}_v01';x=13500 if which==1 else 14500;box=[x,36280,x+1254,37534]
guide=R/'guides'/(stem+'.native-guide.png');assert not guide.exists()
canvas=Image.new('RGB',(1254,1254));cover=Image.new('L',(1254,1254),0);sources=[]
def paste(f,nb,ib,role):
    crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
    canvas.paste(Image.open(f).crop(crop),dest);cover.paste(255,(dest[0],dest[1],dest[0]+ib[2]-ib[0],dest[1]+ib[3]-ib[1]))
    sources.append({**p.metadata(f,role),'sourceGlobalBox':nb,'intersectionGlobalBox':ib,'sourceCrop':crop,'destinationTopLeft':dest})
paste(R/'output/r09_c04-native-candidate-v01.png',[12288,32768,16384,36864],[x,36280,x+1254,36864],'actual r09 output same-global native bottom')
main=p.load(R/'qa/r10_c04-worker-map.json')['r10_c04']
for col in range(4):
    s=main[0][col]
    if not s:continue
    f=R/'native'/(s+'.png');rec=p.load(str(f)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox'];cb=rec['coordinates']['coreGlobalBox']
    ib=[max(box[0],cb[0]),36864,min(box[2],cb[2]),37534]
    if ib[0]<ib[2]:paste(f,nb,ib,'selected r10 top-row native core')
if which==2:
    prev=R/'native/r09_r10_c04_court_join1_v01.png';paste(prev,[13500,36280,14754,37534],[14500,36280,14754,37534],'first actual AI repair left254 native overlap; preserve continuity')
assert cover.getextrema()==(255,255);canvas.save(guide)
co={'tiles':['r09_c04','r10_c04'],'nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254],'repairTargetGlobalBox':[x+100,36814,x+1154,36914],'repairTargetLocalBox':[100,534,1154,634],'repairKind':'cross-row grey court material continuity only; preserve grout/red paper/wood geometry'}
p.dump(R/'prompts'/(stem+'.coordinates.json'),co)
p.dump(str(guide)+'.derivation.json',{'operation':'same-global mechanical native crop/paste, no scaling/shift/feather/color; prior first source wins second left254','sources':sources,'coordinates':co,'sha256':p.hashfile(guide),'completeCoverage':True})
refs=[p.metadata(guide,'exact same-coordinate cross-row edit target')]
if which==2:refs.append(p.metadata(R/'native/r09_r10_c04_court_join1_v01.png','previous adjacent repair context; final254px are fixed LEFT254 in edit target'))
refs += [p.metadata(*a) for a in p.REFS]
p.dump(R/'prompts'/(stem+'.request.json'),{'tool':'image_gen.imagegen','createdAtUtc':p.now(),'coordinates':co,'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'sourceAssembly':sources})
for ref in refs:assert p.hashfile(ref['path'])==ref['sha256']
print({'stem':stem,'guide':guide.as_posix(),'refs':[x['path'] for x in refs]})
