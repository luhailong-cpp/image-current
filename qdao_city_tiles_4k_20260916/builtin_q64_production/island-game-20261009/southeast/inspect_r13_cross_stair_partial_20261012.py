from workflow import *
from PIL import Image
import sys
v=sys.argv[1] if len(sys.argv)>1 else 'v01'
wide=len(sys.argv)>2 and sys.argv[2]=='wide'
im=Image.new('RGB',(4096,4096),(70,70,70))
versions=read(ROOT/'progress-r13_c12.json')['workingVersions'];versions['23']='v02'
for rc,v in versions.items():
 r,c=map(int,rc);f=ROOT/'native'/f'r13_c12_p{rc}_{v}.png'
 im.paste(Image.open(f).convert('RGB').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
source=ROOT/'native'/f'r13_c12_stair_cross_joint_{v}.png'
sx=0 if wide else 115;sx1=1254 if wide else 1139;x=1421+sx;x1=1421+sx1
im.paste(Image.open(source).convert('RGB').crop((sx,115,sx1,1139)),(x,1024))
q=ROOT/'qa'/f'r13-stair-cross-{v}{"-wide" if wide else ""}';q.mkdir(exist_ok=True)
cuts={'left':(x-256,1024,x+256,2048),'right':(x1-256,1024,x1+256,2048),'top':(x,768,x1,1280),'bottom':(x,1792,x1,2304),'whole':(x-256,768,x1+256,2304)}
for k,b in cuts.items():im.crop(b).save(q/f'{k}.png')
write(q/'manifest.json',{'source':str(source),'sha256':sha(source),'status':'pending outer object contour review; bottom east missing actual p33','sourceCrop':[sx,115,sx1,1139],'destinationBox':[x,1024,x1,2048],'underlayVersions':versions,'cuts':{k:list(b) for k,b in cuts.items()},'qaOnly':True})
print(str(q))
