from pathlib import Path
import sys,json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent;TILE=HERE.parent;ZONE=TILE.parent
sys.path.insert(0,str(ZONE));import assemble
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
_,plan=assemble.load_plan('r07_c13');out=HERE/'row1-final';out.mkdir(exist_ok=True)
canvas=Image.new('RGB',(4096,1024));sources=[]
for c in range(1,5):
    item=next(v for v in plan['patches'] if v['id']==f'p1{c}');im,evidence=assemble.inspect_source(TILE,item);sources.append(evidence)
    canvas.paste(im.crop([115,115,1139,1139]),((c-1)*1024,0))
p=out/'row1-native-cores.png';canvas.save(p)
north=ZONE/'r06_c13/candidates/r06_c13.candidate.png';nh=sha(north);nim=Image.open(north).convert('RGB');assert nim.size==(4096,4096)
records=[];montage=Image.new('RGB',(1380,1024));junctions=Image.new('RGB',(1380,460))
for c in range(1,4):
    x=c*1024;box=[x-230,0,x+230,1024];s=canvas.crop(box);p=out/f'v{c}-row1-1to1.png';s.save(p);montage.paste(s,((c-1)*460,0));records.append({'id':f'v{c}','file':str(p),'sha256':sha(p),'rowBox':box,'kind':'internal vertical pair','seamX':230})
    j=Image.new('RGB',(460,460));j.paste(nim.crop([x-230,3866,x+230,4096]),(0,0));j.paste(canvas.crop([x-230,0,x+230,230]),(0,230));p=out/f'north-junction-c{c}-1to1.png';j.save(p);junctions.paste(j,((c-1)*460,0));records.append({'id':f'north-junction-{c}','file':str(p),'sha256':sha(p),'kind':'external/internal four-way intersection','seamX':230,'seamY':230})
montage.save(out/'internal-montage-1to1.png');junctions.save(out/'north-junctions-montage-1to1.png')
for c in range(4):
    x=c*1024;s=Image.new('RGB',(1024,460));s.paste(nim.crop([x,3866,x+1024,4096]),(0,0));s.paste(canvas.crop([x,0,x+1024,230]),(0,230));p=out/f'north-c{c+1}-1to1.png';s.save(p);records.append({'id':f'north-c{c+1}','file':str(p),'sha256':sha(p),'kind':'north shared segment','seamY':230})
assert sha(north)==nh
save(out/'source-and-crops.json',{'tile':'r07_c13','ownedPatches':['p11','p12','p13','p14'],'validatedSelectedNativeCount':4,'sources':sources,'northCandidate':str(north),'northCandidateSha256':nh,'rowComposite':str(out/'row1-native-cores.png'),'rowCompositeSha256':sha(out/'row1-native-cores.png'),'rowPixels':[4096,1024],'completeTileCandidate':False,'internalPairCount':3,'northSharedSegmentCount':4,'northJunctionCount':3,'records':records,'formalAcceptedCount':0,'actualModel':None,'actualQuality':None,'visualStatus':'awaiting-review'})
print(json.dumps({'nativeSourcesStrictlyVerified':4,'internalPairs':3,'northSegments':4,'northJunctions':3,'northCandidateSha256':nh,'out':str(out)}))
