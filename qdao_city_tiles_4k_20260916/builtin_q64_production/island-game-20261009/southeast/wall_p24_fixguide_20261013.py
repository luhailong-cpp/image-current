from PIL import Image
from workflow import *
pid='r08_c10_p24';v='v03'
src=ROOT/'native'/f'{pid}_v02.png';ns=ROOT/'native'/'r08_c11_p21_v06.png'
im=Image.open(src).convert('RGB');im.paste(Image.open(ns).convert('RGB').crop((0,0,230,1254)),(1024,0))
out=ROOT/'guides'/f'{pid}.native-context-{v}.png';assert not out.exists();im.save(out)
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'derivedFrom':[{'file':str(src),'sha256':sha(src)},{'file':str(ns),'sha256':sha(ns),'sourceCrop':[0,0,230,1254],'destination':[1024,0]}],'usableAsFinalArt':False,'nativeGlobalBox':patch(pid)['nativeGlobalBox']})

