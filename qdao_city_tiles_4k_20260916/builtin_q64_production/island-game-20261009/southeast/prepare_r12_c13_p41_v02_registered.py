from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g=R/'guides/r12_c13_p41.native-edit-v02.png';m=read(Path(str(g)+'.generation.json'));im=Image.open(g).convert('RGB')
body=R/'tiles/r12_c13.candidate-sol-20261012-v01.png';w=R/'tiles/r12_c12.candidate-sol-20261012-v01.png'
im.paste(Image.open(body).convert('RGB').crop((0,2957,1139,3187)),(115,0))
im.paste(Image.open(w).convert('RGB').crop((3981,2957,4096,3187)),(0,0))
b=(230,230,800,1254);im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(42)),(230,230))
im.save(g);m['sha256']=sha(g);m['derivedFrom'].extend([{'file':body.as_posix(),'sha256':sha(body),'role':'registered corrected lower p31 board pixels north only'},{'file':w.as_posix(),'sha256':sha(w),'role':'exact actual west first115 north corner'}]);m['placements'].extend([{'source':body.as_posix(),'sourceCrop':[0,2957,1139,3187],'destination':[115,0],'resampled':False},{'source':w.as_posix(),'sourceCrop':[3981,2957,4096,3187],'destination':[0,0],'resampled':False}]);m['guideOnlySoftenedRegion']=b;m['usableAsFinalArt']=False;write(Path(str(g)+'.generation.json'),m)
rp=R/'prompts/r12_c13_p41_v02.request.json';d=read(rp);d['references'][0]['sha256']=sha(g)
prompt="""Use case: precise-object-edit. Restore the softened region of image 1 into the same complete 1254-square daylight hand-painted wood dock and boat crop. The LEFT 230 pixels, TOP 230 pixels, all sharp boat timbers on the right and all other sharp shapes are fixed at their exact coordinates. Last three references give layout, materials and painting style only.
Continue the exact sharp solid upper dock-edge beam from the LEFT strip through the softened region into the existing right-side gold boat rail. Its gold top face, shaded brown vertical face and underside must join continuously at their actual fixed endpoints. Do not shift the left beam or create two heights at the old paste boundary.
There is a SECOND separate slim gold wooden cross-rail entering from the fixed left around y800. Continue this real rail across turquoise water sloping UPWARD TO THE RIGHT, until it goes behind the boat near x800,y600. It is not a downward-right diagonal rail at the very bottom: eliminate that incorrect old lower rail within the softened area. No extra rails or posts.
Restore clear turquoise water and gentle caustics around the timber/supports. Preserve the empty wooden boat and benches, existing supports, wood color and painted grain. No floating timber ends, extra boats, oars, props, UI or text. One opaque square at exactly the same crop and scale."""
pp=Path(d['promptPath']);pp.write_text(prompt,encoding='utf-8');write(rp,d)
print(json.dumps({'guide':g.as_posix(),'sha256':sha(g)}))

