"""Keep all blue-tile interior pixels: a binary integer polygon selects gold only."""
import json
import hashlib
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def file(p): return {'file':str(p),'sha256':sha(p)}
def write(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base='south-02-gold-ridge-v1'
inp=read(HERE/'records'/f'{base}.input.json')
raw=Image.open(HERE/'source'/f'{base}.png').convert('RGB')
orig=Image.open(inp['context']['file']).convert('RGB')
# These integer points follow the gold ridge plus its narrow antialiased silhouette.
# They stay inside the approved [500,498,760,708] context-local edit box.
polygon=[[500,608],[540,592],[580,576],[620,558],[660,541],[700,522],[740,504],[759,498],
         [759,563],[740,573],[720,582],[700,592],[680,602],[660,610],[640,618],
         [620,626],[600,634],[580,642],[560,650],[540,658],[520,665],[500,673]]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon([tuple(p) for p in polygon],fill=255)
hist=mask.histogram()
assert hist[0]>0 and hist[255]>0 and sum(hist[1:255])==0
assert mask.getbbox()[0]>=500 and mask.getbbox()[1]>=498 and mask.getbbox()[2]<=760 and mask.getbbox()[3]<=708
proposal=orig.copy();proposal.paste(raw,(0,0),mask)
outside=ImageChops.difference(orig,proposal);outside.paste((0,0,0),(0,0),mask)
assert outside.getbbox() is None
exports={}
for name,img in [('object-proposal-context',proposal),('object-paste-mask',mask),
                 ('object-after-edge-review',proposal.crop((436,434,824,772)))]:
    p=HERE/'crops'/f'{base}-{name}.png';img.save(p);exports[name]=file(p)
proposal_record=read(HERE/f'{base}.integration-proposal.json')
proposal_record.update({'status':'object-mask-proposal-not-applied-to-production',
    'preferredIntegration':True,'supersedesRectangularProposal':'Rectangular version exposes a hard horizontal color step in neighboring blue tiles; do not integrate it.',
    'sourceCrop':[0,0,1254,1254],'binaryMask':exports['object-paste-mask'],'maskPolygonContextPixels':polygon,
    'maskWorldBox':[inp['contextWorldBox'][0]+500,inp['contextWorldBox'][1]+498,inp['contextWorldBox'][0]+760,inp['contextWorldBox'][1]+674],
    'maskContainsOnly0And255':True,'outsideMaskPixelIdentical':True,
    'operation':'Integer pixel paste with a binary hard polygon selecting only gold ridge and its narrow silhouette; no feathering, blur, resampling, sharpening, alpha blending, or color change.',
    'exports':exports,'visualStatus':'pending-object-mask-edge-review',
    'applicationRecipe':'Recreate sourceComposition, then paste generatedSource with the provided 1254x1254 binaryMask at contextWorldBox origin. For each 4096 tile, crop source and mask by tile intersection using integer coordinates. Leave every pixel where mask=0 untouched.'})
write(HERE/f'{base}.object-integration-proposal.json',proposal_record)
print(json.dumps({'maskBox':mask.getbbox(),'outsideMaskPixelIdentical':True,'exports':exports},ensure_ascii=False,indent=2))
