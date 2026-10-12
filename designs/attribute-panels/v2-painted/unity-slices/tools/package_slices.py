from pathlib import Path
from PIL import Image
import hashlib,json,shutil

out=Path('E:/work/image/designs/attribute-panels/v2-painted/unity-slices')
assets=Path('E:/work/mmorpg-client/Assets/Resources/UI/Ugui/AttributesPaintedV2')
temp=Path('E:/work/tmp/attribute-slices-20260909')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((out/'manifest.json').read_text())
rows=[]
for e in m['sprites']:
    a=out/'png'/(e['name']+'.png');b=assets/a.name
    im=Image.open(a)
    assert im.size==(e['width'],e['height']),e['name']
    assert sha(a)==sha(b),e['name']
    assert e['borderLeftBottomRightTop'][0]+e['borderLeftBottomRightTop'][2]<im.width
    assert e['borderLeftBottomRightTop'][1]+e['borderLeftBottomRightTop'][3]<im.height
    if e['processing']=='Exact native-pixel crop.':
        assert e['sourceRectNativeTopLeft'][2:]==[im.width,im.height],e['name']
    rows.append({'name':e['name'],'sha256':sha(a),'size':list(im.size),'alphaRange':list(im.getchannel('A').getextrema())})
sources=[{'file':str(p.relative_to(out)).replace('\\','/'),'sha256':sha(p),'size':list(Image.open(p).size)} for p in sorted((out/'sources').glob('*.png'))]
v={'status':'passed','sprites':len(rows),'identicalToUnityCopies':True,'pngSizesPassed':True,'bordersPassed':True,'exactCropCoordinatesPassed':True,'sources':sources,'files':rows}
(out/'file-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'tools').mkdir(exist_ok=True)
for name in ['SliceAttributeArtwork.cs','VerifyAttributeSlices.cs','inspect_slices.py','package_slices.py']:
    shutil.copy2(temp/name,out/'tools'/name)
print(json.dumps({k:v[k] for k in ['status','sprites','identicalToUnityCopies','pngSizesPassed','bordersPassed','exactCropCoordinatesPassed']},ensure_ascii=False))
