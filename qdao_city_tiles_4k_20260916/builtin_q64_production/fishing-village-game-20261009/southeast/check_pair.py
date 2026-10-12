from native_workflow import ZONE,TILE,sha,write,now
from PIL import Image
import sys

a=TILE/'native'/(sys.argv[1]+'.png');b=TILE/'native'/(sys.argv[2]+'.png')
left=Image.open(a).convert('RGB');right=Image.open(b).convert('RGB')
assert left.size==right.size==(1254,1254)
out=Image.new('RGB',(2278,1254));out.paste(left.crop((0,0,1139,1254)),(0,0));out.paste(right.crop((115,0,1254,1254)),(1139,0))
qa=TILE/'qa';qa.mkdir(exist_ok=True)
full=qa/f'{a.stem}-{b.stem}-unscaled-pair.png';out.save(full)
strip=qa/f'{a.stem}-{b.stem}-join-100pct.png';out.crop((883,0,1395,1254)).save(strip)
write(strip.with_suffix('.png.derivation.json'),{'createdAt':now(),'operation':'hard-cut unscaled stitch at native overlap midpoint and exact 512px join strip; no blending/resampling','sources':[{'file':str(a),'sha256':sha(a)},{'file':str(b),'sha256':sha(b)}],'fullPair':str(full),'strip':str(strip),'seamX':256,'visualAcceptance':'pending'})
print(str(strip))
