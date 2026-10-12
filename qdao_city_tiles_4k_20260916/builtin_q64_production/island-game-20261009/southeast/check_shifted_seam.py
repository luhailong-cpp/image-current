from PIL import Image
from pathlib import Path
from workflow import ROOT,sha,write,now
for a,b,key in [('r09_c12_p42_v01.png','r09_c12_p43_v02.png','r09p42-p43-shifted'),('r10_c12_p12_v01.png','r10_c12_p13_v02.png','r10p12-p13-shifted')]:
 pa=ROOT/'native'/a;pb=ROOT/'native'/b;out=ROOT/'qa'/f'{key}.png';im=Image.new('RGB',(512,1254));im.paste(Image.open(pa).crop((768,0,1024,1254)),(0,0));im.paste(Image.open(pb).crop((0,0,256,1254)),(256,0));im.save(out)
 write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'createdAt':now(),'operation':'native horizontal hard seam shifted 115px left within real overlap, no blending or resize','sourceA':str(pa),'shaA':sha(pa),'cropA':[768,0,1024,1254],'sourceB':str(pb),'shaB':sha(pb),'cropB':[0,0,256,1254],'seamX':256,'reason':'Keep complete native tube silhouette inside one source across tile edge; standard core cut truncates its left rim.'})

