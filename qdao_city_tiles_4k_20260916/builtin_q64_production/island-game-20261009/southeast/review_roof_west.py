from workflow import *
from PIL import Image
l=ROOT/'tiles/r09_c11.candidate.png';r=ROOT/'tiles/r09_c12.candidate-v03.png';a=Image.open(l).convert('RGB');b=Image.open(r).convert('RGB');im=Image.new('RGB',(512,1024));im.paste(a.crop([3840,0,4096,1024]),(0,0));im.paste(b.crop([0,0,256,1024]),(256,0));im.save(ROOT/'qa/r09_c12-v03/changed-west-edge.png')
write(ROOT/'qa/r09_c12-v03/changed-west-edge.json',{'sources':[{'file':str(l),'sha256':sha(l)},{'file':str(r),'sha256':sha(r)}],'operation':'original pixel assembled west border segment 1','formalAccepted':False})

