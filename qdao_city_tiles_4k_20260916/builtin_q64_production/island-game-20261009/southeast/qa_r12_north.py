from workflow import *
from PIL import Image
q=ROOT/'qa/r12c12-north';q.mkdir(exist_ok=True);north=ROOT/'tiles/r11_c12.candidate-v02.png';nim=Image.open(north).convert('RGB');bottom=Image.new('RGB',(4096,256));parts=[]
for c,v in [(1,'v03'),(2,'v02'),(3,'v04'),(4,'v04')]:
 f=ROOT/'native'/f'r12_c12_p1{c}_{v}.png';im=Image.open(f).convert('RGB');core=im.crop((115,115,1139,371));out=Image.new('RGB',(1024,512));out.paste(nim.crop(((c-1)*1024,3840,c*1024,4096)),(0,0));out.paste(core,(0,256));out.save(q/f'north-{c}.png');bottom.paste(core,((c-1)*1024,0));parts.append({'source':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,371]})
full=Image.new('RGB',(4096,512));full.paste(nim.crop((0,3840,4096,4096)),(0,0));full.paste(bottom,(0,256))
for i in range(1,4):full.crop((i*1024-256,0,i*1024+256,512)).save(q/f'junction-{i}.png')
write(q/'index.json',{'northCandidate':str(north),'northSha256':sha(north),'southNativeSources':parts,'operation':'exact source crop/paste','status':'pending_root_native_review'})
print('Created 4 full north edge segments and 3 true boundary junctions')
