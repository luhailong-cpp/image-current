"""Apply reviewed south-border native repairs to r05_c13, preserving M01.
All placements are integer pixel crops. Existing provenance is retained as data.
"""
from pathlib import Path
from PIL import Image, ImageChops
import json, hashlib
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ZONE = HERE.parents[2]
TILE = ZONE/'r05_c13'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,data): Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
target = TILE/'candidates/r05_c13.candidate.png'
record_file = Path(str(target)+'.generation.json')
prior_file = HERE/'records/r05_c13-pre-south-generation.json'
if not prior_file.exists(): save(prior_file, read(record_file))
prior = read(prior_file)
op=prior['operation']
for key, hashkey in [('baseline','baselineSha256'),('repair','repairSha256'),('mask','maskSha256')]:
    assert sha(op[key]) == op[hashkey], key
base=Image.open(op['baseline']).convert('RGB')
base.paste(Image.open(op['repair']).convert('RGB'),tuple(op['pasteOrigin']),Image.open(op['mask']).convert('L'))
base_hash_pixels=hashlib.sha256(base.tobytes()).hexdigest()
original=base.copy()
review=read(HERE/'repair-review.json')
applied=[]
union=Image.new('L',base.size,0)
for repair in review['repairs']:
    prop=read(HERE/repair['proposal'])
    assert sha(prop['generatedSource']['file']) == prop['generatedSource']['sha256']
    for part in prop['sourceComposition']:
        assert sha(part['native']) == part['sha256']
    source=Image.open(prop['generatedSource']['file']).convert('RGB')
    mask=None
    if 'binaryMask' in prop:
        assert sha(prop['binaryMask']['file']) == prop['binaryMask']['sha256']
        mask=Image.open(prop['binaryMask']['file']).convert('L')
        assert set(mask.getdata()) <= {0,255}
    item=next(o for o in repair['integerTileOperations'] if o['tile']=='r05_c13')
    cropped=source.crop(item['sourceCrop'])
    m=mask.crop(item['maskCrop']) if mask else Image.new('L',cropped.size,255)
    base.paste(cropped,tuple(item['destinationTileXY']),m)
    union.paste(m,tuple(item['destinationTileXY']))
    applied.append({'id':repair['id'],'source':prop['generatedSource'],'proposal':str(HERE/repair['proposal']),'operation':item,'mask':prop.get('binaryMask')})
outside=Image.composite(original,base,union)
assert ImageChops.difference(original,outside).getbbox() is None
base.save(target)
record={**prior,'sha256':sha(target),'updatedAt':datetime.now(timezone.utc).isoformat(),
    'operation':{'type':'replay prior native-core/M01 recipe then apply two integer border repair crops','priorRecipe':prior['operation'],'priorRecipeRecord':str(prior_file),'southBorderRepairs':applied,'sourceResampling':False,'blurUsed':False},
    'derivedFrom':prior['derivedFrom']+[{'file':a['source']['file'],'sha256':a['source']['sha256'],'generationRecord':str(HERE/'records'/f"{a['id']}.generation.json")} for a in applied],
    'formalAccepted':False,'southBorderReview':'two local P2 clarity fixes integrated; full shared seam final review pending'}
save(record_file,record)
save(HERE/'records/r05_c13-south-integration.json',{'file':str(target),'sha256':sha(target),'width':base.width,'height':base.height,'replayedPriorPixelsSha256':base_hash_pixels,'outsideMaskPixelIdentical':True,'operations':applied,'noResampling':True,'formalAccepted':False})
print(json.dumps({'candidate':str(target),'sha256':sha(target),'outsideMaskPixelIdentical':True}))
