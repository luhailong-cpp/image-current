import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
prefix=sys.argv[1];p=ROOT/'qa'/(prefix+'-candidate-4096.png');art=Image.open(p).convert('RGB');assert art.size==(4096,4096)
idx=load(ROOT/'current-native-map.json'); north=Path(idx['candidateArtifacts']['r10_c04']['path']);west=Path(idx['candidateArtifacts']['r11_c03']['path'])
n=Image.open(north).convert('RGB');w=Image.open(west).convert('RGB');assert n.size==w.size==(4096,4096)
views=[]
for i in range(4):
 q=ROOT/'qa'/(prefix+f'-north-r10c04-c{i+1}-native100.png');assert not q.exists();out=Image.new('RGB',(1024,600));out.paste(n.crop((i*1024,3796,(i+1)*1024,4096)),(0,0));out.paste(art.crop((i*1024,0,(i+1)*1024,300)),(0,300));out.save(q);views.append({'path':str(q),'side':'north','sourceCropRule':'top300 r10c04 bottom; bottom300 r11c04 top','globalBoundaryY':40960,'scale':'1:1','sha256':hashfile(q)})
 q=ROOT/'qa'/(prefix+f'-west-r11c03-r{i+1}-native100.png');assert not q.exists();out=Image.new('RGB',(600,1024));out.paste(w.crop((3796,i*1024,4096,(i+1)*1024)),(0,0));out.paste(art.crop((0,i*1024,300,(i+1)*1024)),(300,0));out.save(q);views.append({'path':str(q),'side':'west','sourceCropRule':'left300 r11c03 right; right300 r11c04 left','globalBoundaryX':12288,'scale':'1:1','sha256':hashfile(q)})
dump(ROOT/'qa'/(prefix+'-neighbors-native-views.json'),{'createdAtUtc':now(),'sources':[metadata(p,'current central tile'),metadata(north,'north neighbor'),metadata(west,'west neighbor')],'operation':'native100 crop and concatenation; QA only','views':views,'formalAccepted':False});print({'views':len(views)})

