from pathlib import Path
from PIL import Image
import sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
m3=p.load(R/'qa/r10_c03-worker-map.json');m4=p.load(R/'qa/r10_c04-worker-map.json');items=[]
def save(label,out,sources,box):
    path=R/'qa'/('r10-independent-'+label+'-native100.png');assert not path.exists();out.save(path)
    entry={'path':path.as_posix(),'operation':'mechanical native crop/paste only, no scaling/filter/color/shift','dimensions':list(out.size),'globalBox':box,'sources':sources,'sha256':p.hashfile(path)}
    p.dump(str(path)+'.derivation.json',entry);items.append(entry)
for row in range(4):
    a=m3['r10_c03'][row][3];b=m4['r10_c04'][row][0]
    if not(a and b):continue
    ap=R/'native'/(a+'.png');bp=R/'native'/(b+'.png');out=Image.new('RGB',(600,1024))
    out.paste(Image.open(ap).crop((839,115,1139,1139)),(0,0));out.paste(Image.open(bp).crop((115,115,415,1139)),(300,0))
    sources=[{**p.metadata(ap,'left c03 col4 selected core'),'crop':[839,115,1139,1139],'destination':[0,0]},{**p.metadata(bp,'right c04 col1 selected core'),'crop':[115,115,415,1139],'destination':[300,0]}]
    y=36864+row*1024;save(f'c03c04-shared-row{row+1}-snapshot20261011',out,sources,[11988,y,12588,y+1024])
upper=R/'output/r09_c04-native-candidate-v01.png'
for col in range(4):
    a=m4['r10_c04'][0][col]
    if not a:continue
    ap=R/'native'/(a+'.png');x=col*1024;out=Image.new('RGB',(1024,600))
    out.paste(Image.open(upper).crop((x,3796,x+1024,4096)),(0,0));out.paste(Image.open(ap).crop((115,115,1139,415)),(0,300))
    sources=[{**p.metadata(upper,'actual r09 c04 published local candidate bottom'),'crop':[x,3796,x+1024,4096],'destination':[0,0]},{**p.metadata(ap,'r10 c04 selected first-row core'),'crop':[115,115,1139,415],'destination':[0,300]}]
    save(f'c04-actual-top-col{col+1}-snapshot20261011',out,sources,[12288+x,36564,13312+x,37164])
p.dump(R/'qa/r10-independent-shared-snapshot20261011.json',{'createdAtUtc':p.now(),'mapSnapshots':{'c03':m3['r10_c03'],'c04':m4['r10_c04']},'items':items,'knownPendingOwners':['root: c04 topsteps / shared gold gourd','root: c03 top flowers and leaf package','c04worker: col1/2 upper rail'],'formalAccepted':False})
print({'strips':[x['path'] for x in items]})
