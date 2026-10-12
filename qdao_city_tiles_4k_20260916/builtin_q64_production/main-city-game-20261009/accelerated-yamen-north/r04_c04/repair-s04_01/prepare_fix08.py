from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix08';D.mkdir(parents=True,exist_ok=True)
source=B/'fix07/generated.png';south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
im=Image.open(source).convert('RGB');im.paste(Image.open(south).convert('RGB').crop((0,0,1254,230)),(0,1024))
ImageDraw.Draw(im).rectangle((625,0,815,1023),fill=(110,110,110))
target=D/'left-rail-edit-mask-context.png'
if target.exists():raise FileExistsError(target)
im.save(target)
band=B/'fix04/real-south-top230.png'
prompt='''Use case: precise-object-edit. Fill the narrow solid-grey EDIT MASK in image1. It covers only the missing LEFT portion of the existing long pale stone railing: the left dark silhouette, left bevel and left inset groove. Continue those lines straight and smoothly UP from their correct endpoints immediately below the mask. Match their exact positions, width and pale grey shading in the authentic bottom strip. Image2 is the same authentic native bottom230pixel strip as a separate reference. Do not shift that lower strip.
The railing's right half is now CORRECT. Preserve it exactly, including right outside edge near x1004 and right inset groove near x917. Keep all unmasked pixels, the large left pedestal stone slabs, green fragment at bottom, right stairs, framing and camera unchanged. The mask is x625..815,y0..1023; every other area is existing artwork. Restore only this missing narrow strip with the same clean gently rounded hand-painted pale stone in bright daylight. One continuous long inset through both image borders, with no end cap or ornament. The grey patch must disappear without a visible boundary, hue change, kink, or horizontal splice. Return a fully opaque1254x1254 original-scale image. No other changes, no objects, no text, no people/UI/watermark.'''
p={'prompt':prompt,'referenced_image_paths':[str(target),str(band)],'transparent_background':False}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
(D/'parameters.json').write_text(json.dumps(p,indent=2),encoding='utf-8');(D/'prompt.txt').write_text(prompt,encoding='utf-8')
(D/'preparation.json').write_text(json.dumps({'source':str(source),'sourceSha256':sha(source),'actualSouthSource':str(south),'actualSouthSha256':sha(south),
'southSourceCrop':[0,0,1254,230],'targetPaste':[0,1024,1254,1254],'editMaskRect':[625,0,816,1024],'maskOnly':True,
'operation':'Preparation guide only: exact native context crop/paste and visible neutral edit mask; no final artwork rendered by code',
'submittedTarget':str(target),'submittedTargetSha256':sha(target),'sourceResampled':False,'guideGameArt':False,'actualModel':None,'actualQuality':None},indent=2),encoding='utf-8')
