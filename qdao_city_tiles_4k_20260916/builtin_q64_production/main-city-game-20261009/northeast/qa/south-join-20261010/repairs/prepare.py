"""Read-only production pixels -> exact repair contexts and submitted prompts."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ZONE = HERE.parents[2]
spec = importlib.util.spec_from_file_location('assembly', ZONE/'assemble.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
contract = m.read_json(ZONE.parent/'production-contract.json')
for subdir in ('crops', 'prompts', 'source', 'receipts', 'records'):
    (HERE/subdir).mkdir(exist_ok=True)

cases = [
    {'id':'south-01-flowers-v1','origin':[49536,19936],
     'editWorldBox':[49980,20365,50360,20630],
     'object':'the few visibly soft, blurred pink blossoms at the top edge of the large cherry blossom cluster, around the middle of image 1',
     'instruction':'Redraw those soft petals with clean, gently rounded petal contours and distinct small orange stamens, matching the already sharp blossoms below. Preserve exactly the branch positions, blossom cluster silhouette and existing pink/white palette. Keep all existing crisp flowers unchanged. Do not invent additional clusters, branches or flowers.'},
    {'id':'south-02-gold-ridge-v1','origin':[51520,19872],
     'editWorldBox':[52020,20370,52280,20580],
     'object':'the short visibly blurred gold diagonal roof ridge segment near the center of image 1, above the sharp small gold curl and adjacent blue roof tiles',
     'instruction':'Redraw only this soft portion of the gold ridge with a clean precise gold silhouette, narrow warm highlight and smooth rounded Q-style bevel, matching the already crisp parts of the same ridge. Preserve exactly the existing gold ridge angle, width, curve, small gold curl and blue tile grooves. Keep all sharp roof detail unchanged.'}
]
sources = []
for tile_id in ('r05_c13','r06_c13'):
    tile, plan = m.load_plan(tile_id)
    imgs, evidence, missing, invalid = m.inspect_sources(tile, plan)
    assert not invalid
    evidence = {e['id']:e for e in evidence}
    for item in plan['patches']:
        if item['id'] in imgs:
            sources.append((imgs[item['id']], item, evidence[item['id']]))

for case in cases:
    x,y=case['origin']; world=[x,y,x+1254,y+1254]
    canvas=Image.new('RGB',(1254,1254)); alpha=Image.new('L',(1254,1254))
    used=[]
    for image,item,evidence in sources:
        a,b,c,d=item['coreWorldBox']
        box=[max(x,a),max(y,b),min(x+1254,c),min(y+1254,d)]
        if box[0]>=box[2] or box[1]>=box[3]: continue
        crop=[box[0]-a+115,box[1]-b+115,box[2]-a+115,box[3]-b+115]
        dest=[box[0]-x,box[1]-y]
        canvas.paste(image.crop(crop),dest)
        alpha.paste(255,(dest[0],dest[1],dest[0]+box[2]-box[0],dest[1]+box[3]-box[1]))
        used.append({'native':evidence['file'],'sha256':evidence['sha256'],'sourceCrop':crop,'destination':dest,'worldBox':box,'generationRecord':evidence['generationRecord']})
    assert alpha.getextrema()==(255,255)
    path=HERE/'crops'/f"{case['id']}-context.png"
    assert not path.exists(), 'Do not overwrite an existing repair context'
    canvas.save(path)
    ex=case['editWorldBox']; local=[ex[0]-x,ex[1]-y,ex[2]-x,ex[3]-y]
    refs=[str(path),contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference']]
    roles=['edit target: existing native-pixel stitched context; exact framing and scale must stay fixed','approved complete city layout; context only, never enlarge or replace target','approved near-view materials and lighting','approved Daoist Q-style illustration; style only']
    prompt=f'''Use case: precise-object-edit.
Asset type: small original-pixel repair in a continuous hand-painted Daoist Q-style game city map.
Input image 1 is the ONLY edit target: a 1254 by 1254 crop assembled from existing native painted pixels, not a thumbnail. Input 2 is approved city-layout context only. Input 3 is the approved close-view material and lighting. Input 4 is the approved Daoist Q art-style reference only.
Return image 1 at identical 1254 by 1254 framing, size, scale and perspective. Repair {case['object']}.
The intended edit rectangle in image-1 pixel coordinates is {local}; alter only the existing object inside that small rectangle. {case['instruction']}
Preserve every other pixel region, including stone pavement geometry, thin grout lines, pale grey/blue-grey natural colors, painted stone texture, existing shadows, and all image borders. Keep the daytime clean bright lighting and rounded polished illustrative finish. Do not rotate, zoom, crop, reframe, stretch or redraw the entire scene. Do not add any items, text, watermark, lens depth of field or bokeh. Do not blur, feather or soften neighboring sharp pixels to hide transitions. This is a local painted-detail correction, not a sharpening filter and not a style change.'''
    req={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
    (HERE/'prompts'/f"{case['id']}.prompt.txt").write_text(prompt,encoding='utf-8')
    (HERE/'prompts'/f"{case['id']}.request.json").write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    record={'id':case['id'],'createdAtUtc':datetime.now(timezone.utc).isoformat(),'contextWorldBox':world,'editWorldBox':ex,'editContextBox':local,'context':m.file_evidence(path),'references':[dict(m.file_evidence(p),role=r) for p,r in zip(refs,roles)],'sourceComposition':used,'operation':'exact integer crop and paste; no resizing, filtering, blending, or production asset modification','plannedReturnSize':[1254,1254],'actualModel':None,'actualQuality':None}
    (HERE/'records'/f"{case['id']}.input.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'id':case['id'],'context':str(path),'localEdit':local}))
