from workflow import *
from PIL import Image
import sys
pid=sys.argv[1];version=sys.argv[2];neighbors=sys.argv[3:];p=patch(pid);box=p['nativeGlobalBox'];base=ROOT/'guides'/f'{pid}.native-context-v02.png'
if not base.exists():base=ROOT/'guides'/f'{pid}.layout-only.png'
im=Image.open(base).convert('RGB');parts=[{'file':str(base),'sha256':sha(base),'role':'prior layout+any north anchor guide'}]
for name in neighbors:
 src=ROOT/'native'/name;rec=read(Path(str(src)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox'];inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
 assert inter[0]<inter[2] and inter[1]<inter[3]
 crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(Image.open(src).convert('RGB').crop(crop),dest);parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest,'worldIntersection':inter})
out=ROOT/'guides'/f'{pid}.native-context-{version}.png';assert not out.exists();im.save(out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'derivedFrom':parts,'nativeGlobalBox':box,'usableAsFinalArt':False});print(out)

