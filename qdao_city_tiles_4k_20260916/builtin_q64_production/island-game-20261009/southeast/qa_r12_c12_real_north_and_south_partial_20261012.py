from workflow import *
from PIL import Image
tid='r12_c12';rev='sol-20261012-v01'
f=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';im=Image.open(f).convert('RGB')
north=ROOT/'tiles/r11_c12.candidate-v02.png';ni=Image.open(north).convert('RGB')
q=ROOT/'qa/r12_c12-sol-20261012-v01/external-north';q.mkdir(exist_ok=False);cuts=[]
for c in range(4):
 x=c*1024;o=Image.new('RGB',(1024,512));o.paste(ni.crop((x,3840,x+1024,4096)),(0,0));o.paste(im.crop((x,0,x+1024,256)),(0,256));o.save(q/f'north-{c+1}.png');cuts.append({'file':str(q/f'north-{c+1}.png'),'northCrop':[x,3840,x+1024,4096],'candidateCrop':[x,0,x+1024,256],'status':'pending_visual_review'})
for c in [1,2,3]:
 x=c*1024;o=Image.new('RGB',(512,512));o.paste(ni.crop((x-256,3840,x+256,4096)),(0,0));o.paste(im.crop((x-256,0,x+256,256)),(0,256));o.save(q/f'north-junction-{c}.png')
south=ROOT/'native/r13_c12_p11_v02.png';si=Image.open(south).convert('RGB');o=Image.new('RGB',(1024,512));o.paste(im.crop((0,3840,1024,4096)),(0,0));o.paste(si.crop((115,115,1139,371)),(0,256));o.save(q/'south-p11-v02.png')
write(q/'manifest.json',{'candidate':str(f),'candidateSha256':sha(f),'northCandidate':str(north),'northSha256':sha(north),'southPartialSource':str(south),'southPartialSha256':sha(south),'cuts':cuts,'northEdgeFullCoverage':True,'southEdgeFullCoverage':False,'operation':'exact true original-pixel neighbor core crops, no blending or resizing','formalAccepted':False})
print(q)
