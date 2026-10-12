from workflow import *
from PIL import Image
folder=ROOT/'qa/center-r10c12-external-20261011';folder.mkdir(exist_ok=True)
spec={'center':'r10_c12.candidate-v02.png','north':'r09_c12.candidate-v07.png','south':'r11_c12.candidate-v02.png','west':'r10_c11.candidate-v04.png','east':'r10_c13.candidate-v02.png'}
ims={k:Image.open(ROOT/'tiles'/v).convert('RGB') for k,v in spec.items()};c=ims['center'];entries=[]
for side in ['north','south','west','east']:
 for i in range(4):
  s=1024*i;n=ims[side]
  if side in ['north','south']:
   out=Image.new('RGB',(1024,512))
   if side=='north':out.paste(n.crop([s,3840,s+1024,4096]),(0,0));out.paste(c.crop([s,0,s+1024,256]),(0,256))
   else:out.paste(c.crop([s,3840,s+1024,4096]),(0,0));out.paste(n.crop([s,0,s+1024,256]),(0,256))
  else:
   out=Image.new('RGB',(512,1024))
   if side=='west':out.paste(n.crop([3840,s,4096,s+1024]),(0,0));out.paste(c.crop([0,s,256,s+1024]),(256,0))
   else:out.paste(c.crop([3840,s,4096,s+1024]),(0,0));out.paste(n.crop([0,s,256,s+1024]),(256,0))
  f=folder/f'{side}-{i+1}.png';out.save(f);entries.append({'id':f'{side}-{i+1}','file':str(f),'sha256':sha(f),'nativePixelCrop':True,'status':'pending_visual_review'})
write(folder/'index.json',{'createdAt':now(),'inputs':{k:{'file':str(ROOT/'tiles'/v),'sha256':sha(ROOT/'tiles'/v)} for k,v in spec.items()},'entries':entries,'formalAccepted':False,'missingDiagonalNeighbors':['r11_c11','r11_c13']})
print(str(folder))

