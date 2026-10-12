"""Exact, unscaled border samples from current 4K candidates."""
from pathlib import Path
from PIL import Image
from workflow import ROOT,write,sha,now
a=ROOT/'tiles/r09_c12.candidate-v02.png'
b=ROOT/'tiles/r10_c12.candidate-v02.png'
ia=Image.open(a).convert('RGB');ib=Image.open(b).convert('RGB')
entries=[]
for c in range(4):
 x=c*1024
 ca=[x,3840,x+1024,4096];cb=[x,0,x+1024,256]
 im=Image.new('RGB',(1024,512))
 im.paste(ia.crop(ca),(0,0));im.paste(ib.crop(cb),(0,256))
 p=ROOT/'qa'/f'r09_c12-v02-r10_c12-v02.south-border-{c+1}.png'
 im.save(p)
 rec={'file':str(p),'sha256':sha(p),'operation':'exact unscaled crop and paste; seam at y=256','sources':[{'file':str(a),'sha256':sha(a),'crop':ca,'destination':[0,0]},{'file':str(b),'sha256':sha(b),'crop':cb,'destination':[0,256]}],'status':'pending_visual_review'}
 write(Path(str(p)+'.generation.json'),rec);entries.append(rec)
write(ROOT/'qa/r09_c12-v02-r10_c12-v02.border-review.json',{'createdAt':now(),'entries':entries,'formalAccepted':False})
