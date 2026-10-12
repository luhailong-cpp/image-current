from workflow import *
from PIL import Image
native=ROOT/'native/r12_c12_p12_v02.png';n=Image.open(native).convert('RGB');nb=patch('r12_c12_p12')['nativeGlobalBox']
for col in [1,3]:
 pid=f'r12_c12_p1{col}';p=patch(pid);box=p['nativeGlobalBox'];guide=Image.open(ROOT/'guides'/f'{pid}.native-context-v02.png').convert('RGB');inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])];crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];guide.paste(n.crop(crop),dest);out=ROOT/'guides'/f'{pid}.native-context-v03.png';assert not out.exists();guide.save(out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'derivedFrom':[{'file':str(native),'sha256':sha(native),'sourceCrop':crop,'destination':dest}],'priorGuide':str(ROOT/'guides'/f'{pid}.native-context-v02.png'),'nativeGlobalBox':box,'usableAsFinalArt':False})
q=ROOT/'qa/r12_c12';q.mkdir(exist_ok=True);p=Image.open(ROOT/'tiles/r11_c12.candidate-v02.png').convert('RGB');im=Image.new('RGB',(1024,512));im.paste(p.crop([1024,3840,2048,4096]),(0,0));im.paste(n.crop([115,115,1139,371]),(0,256));im.save(q/'north-p12-v02.png')
print('ready')

