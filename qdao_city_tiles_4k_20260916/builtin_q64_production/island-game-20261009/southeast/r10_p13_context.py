from PIL import Image
from pathlib import Path
from workflow import ROOT,read,write,sha,now
p='r10_c12_p13';base=ROOT/'guides'/f'{p}.layout-only.png';left=ROOT/'native'/'r10_c12_p12_v01.png';top=ROOT/'native'/'r09_c12_p43_v02.png'
im=Image.open(base).convert('RGB');im.paste(Image.open(left).crop((1024,0,1139,1254)),(0,0));im.paste(Image.open(top).crop((0,1024,1254,1254)),(0,0))
out=ROOT/'guides'/f'{p}.native-context-v02.png';assert not out.exists();im.save(out)
write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'operation':'mechanical unscaled native anchor paste; retain left core pixels only because its right halo invents an inconsistent tube wholly outside its final core','usableAsFinalArt':False,'derivedFrom':[{'file':str(f),'sha256':sha(f)} for f in [base,left,top]],'placements':[{'source':str(left),'sourceCrop':[1024,0,1139,1254],'destination':[0,0]},{'source':str(top),'sourceCrop':[0,1024,1254,1254],'destination':[0,0]}]})

