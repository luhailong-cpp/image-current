from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from workflow import sample,read,write,sha,W,B
box=[15130,15500,16384,16754];con=read(B.parent/'production-contract.json')
layout=Image.open(con['layoutReference']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in box),resample=Image.Resampling.BICUBIC)
base=np.asarray(layout).copy();der=[]
for ap in [B/'delivery-2x2/stage-v4/r04_c04.assembly.json']:
 a,m,ids,rec=sample(ap,box);base[m]=a[m];der.append({'assembly':str(ap),'sha256':sha(ap),'nativePixels':int(m.sum())})
p=B/'native/r05_c04_s01_s03_v01.png';g=read(str(p)+'.generation.json')['globalNativeBox'];it=[max(box[0],g[0]),max(box[1],g[1]),min(box[2],g[2]),min(box[3],g[3])]
src=[it[0]-g[0],it[1]-g[1],it[2]-g[0],it[3]-g[1]];dst=[it[0]-box[0],it[1]-box[1],it[2]-box[0],it[3]-box[1]]
base[dst[1]:dst[3],dst[0]:dst[2]]=np.asarray(Image.open(p).convert('RGB').crop(src));der.append({'file':str(p),'sha256':sha(p),'sourceCrop':src,'destinationBox':dst})
Image.fromarray(base).save(W/'guides/slim-post-head-context.png')
# Restore the approved missing object only as fuzzy position guide, never as final pixels.
base[520:1254,430:1254]=np.asarray(layout)[520:1254,430:1254]
out=W/'guides/slim-post-head-positional.png';Image.fromarray(base).save(out)
write(str(out)+'.derivation.json',{'globalNativeBox':box,'derivedFrom':der,'layout':con['layoutReference'],'layoutSha256':sha(con['layoutReference']),'fuzzyObjectRegion':[430,520,1254,1254],'operation':'integer native-context paste plus layout-only extent crop; never final pixels','guideSha256':sha(out)})
print(str(out))

