from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(__file__).resolve().parent
orig=T/'layout-only/p11-native-conditioned.png'
below=T/'native/p21-v1.png'
im=Image.open(orig).convert('RGB');s=Image.open(below).convert('RGB')
# Input guide only: replace obsolete blurred shaft footprint with ground,
# then project the authoritative native shaft upward. Never consumed as art.
for y in range(0,1024):
    sample=im.getpixel((1210,min(1000,max(650,y))))
    for x in range(320,800):im.putpixel((x,y),sample)
shaft=s.crop((568,0,704,40))
for y in range(0,1024,40):im.paste(shaft.crop((0,0,136,min(40,1024-y))),(568,y))
# Restore original exact lower neighbor strip after guide-only operations.
im.paste(s.crop((0,0,1254,230)),(0,1024))
out=T/'layout-only/p11-post-continuity-conditioned-v3.png';im.save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d={'file':str(out),'sha256':sha(out),'classification':'layout-only conditioning input; never final artwork','outputDimensions':[1254,1254],'operation':'obsolete blurred post area replaced by approximate ground guide; native shaft swatch projected vertically for geometry conditioning; exact native bottom230 restored','sources':[{'path':str(p),'sha256':sha(p)} for p in (orig,below)],'finalArtPixelsGenerated':False,'projectionNativeShaftBox':[568,0,704,40],'newShaftX':[568,704],'exactBottomNativeSourceBox':[0,0,1254,230]}
out.with_suffix('.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps(d))
