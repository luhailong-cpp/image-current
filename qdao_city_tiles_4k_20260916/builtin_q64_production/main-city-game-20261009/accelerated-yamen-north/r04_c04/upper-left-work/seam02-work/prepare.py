from pathlib import Path
from PIL import Image
import hashlib, json

out = Path(__file__).parent
native = out.parent.parent / 'native'
upper = native / 's02_01_v4.png'
lower = native / 's03_01_v1.png'
guide = out / 'seam02-center-guide.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(upper) as a, Image.open(lower) as b:
    assert a.size == b.size == (1254,1254)
    result = Image.new('RGB', (1254,1254))
    result.paste(a.crop((0,512,1254,1139)), (0,0))
    result.paste(b.crop((0,115,1254,742)), (0,627))
    result.save(guide)
    result.crop((620,427,970,827)).save(out/'seam02-before-tassel-native.png')
    result.crop((0,507,1254,747)).save(out/'seam02-before-wall-native.png')
sources = [
    {'path':str(upper),'sha256':sha(upper),'size':[1254,1254],'sourceCrop':[0,512,1254,1139],'destinationBox':[0,0,1254,627]},
    {'path':str(lower),'sha256':sha(lower),'size':[1254,1254],'sourceCrop':[0,115,1254,742],'destinationBox':[0,627,1254,1254]}
]
data = {'worldBox':[12173,13709,13427,14963], 'nativeSize':[1254,1254], 'seamYLocal':627,'seamYWorld':14336,'guide':str(guide),'guideSha256':sha(guide),'sources':sources,'resize':False,'transform':'unscaled integer crop and paste only','purpose':'true seam-centered edit target'}
(out/'guide-provenance.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(data))
