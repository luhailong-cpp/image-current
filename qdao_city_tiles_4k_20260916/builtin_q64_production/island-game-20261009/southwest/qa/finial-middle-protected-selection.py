"""Transfer an existing native binary selection and protect existing right background.

No image pixels are synthesized, filtered, displaced, blended, or recolored.
The erosion below applies only to a binary source-selection guard.
"""
import sys, json, copy
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import native_multi_tile_repair as m
from production import dump, now

PREFIX = 'finial-middle-protected-v01'
BASE_PREFIX = 'finial-upper-stable-v01'
STEM = 'r10_c03_c04_finial_middle_join_v01'
BOX = [11660, 38320, 12914, 39574]
bases = [m.read_base([ROOT/'qa'/f'{BASE_PREFIX}-{tile}{suffix}' for suffix in
    ['-candidate-4096.png', '-source-id-mask.png', '-report.json']]) for tile in ['r10_c03', 'r10_c04']]
template = m.load(ROOT/'qa'/'finialmiddle-trial-v02-r10_c03-report.json')
source = copy.deepcopy(next(s for s in template['inputs'] if s['stem'] == STEM))
native = np.asarray(Image.open(source['path']).convert('RGB'))
mask_path = ROOT/'qa'/'finialmiddle-trial-v02-repair-local-selection-mask.png'
selected = np.asarray(Image.open(mask_path).convert('L')) == 255
base_canvas = m.canvas_crop(bases, BOX)[:,:,:3]
rgb = base_canvas.astype(np.int16)
# Existing gold object only; pastel wall/floor remain the baseline source.
gold = (rgb[:,:,0] - rgb[:,:,2] > 35) & (rgb[:,:,0] > rgb[:,:,1] * 1.13)
inside = np.asarray(Image.fromarray((gold*255).astype(np.uint8)).filter(ImageFilter.MinFilter(17))) == 255
guard = np.zeros((1254,1254), dtype=bool)
guard[:510,1000:] = ~inside[:510,1000:]
selected[guard] = False
assert selected[185:1185,545:705].all()
local_mask_path = ROOT/'qa'/f'{PREFIX}-repair-local-selection-mask.png'
guard_path = ROOT/'qa'/f'{PREFIX}-baseline-background-guard.png'
Image.fromarray((selected*255).astype(np.uint8)).save(local_mask_path)
Image.fromarray((guard*255).astype(np.uint8)).save(guard_path)
manifest = {'createdAtUtc':now(), 'status':'native candidate pending visual review', 'repair':STEM,
    'sourceMask':{'path':str(mask_path),'sha256':m.sha(mask_path)},
    'localSelectionMask':{'path':str(local_mask_path),'sha256':m.sha(local_mask_path)},
    'backgroundGuard':{'path':str(guard_path),'sha256':m.sha(guard_path)},
    'algorithm':'Exact native binary selection; original DP mask with baseline background/outline guard on repair-local x>=1000,y<510.',
    'guardParameters':{'redMinusBlueGreaterThan':35,'redGreaterThanGreenFactor':1.13,'binaryMaskErosionWidth':17},
    'tiles':[]}
for b in bases:
    arr=b['base'].copy(); ids=b['ids'].copy(); inputs=copy.deepcopy(b['inputs'])
    sid=max(s['sourceId'] for s in inputs)+1; entry=copy.deepcopy(source);entry['sourceId']=sid;inputs.append(entry)
    tx0,ty0,tx1,ty1=b['box']; gx0=max(BOX[0],tx0);gy0=max(BOX[1],ty0);gx1=min(BOX[2],tx1);gy1=min(BOX[3],ty1)
    local=selected[gy0-BOX[1]:gy1-BOX[1],gx0-BOX[0]:gx1-BOX[0]]
    target=arr[gy0-ty0:gy1-ty0,gx0-tx0:gx1-tx0]
    pixels=native[gy0-BOX[1]:gy1-BOX[1],gx0-BOX[0]:gx1-BOX[0]]
    target[local]=pixels[local]
    ids[gy0-ty0:gy1-ty0,gx0-tx0:gx1-tx0][local]=sid
    validation=m.validate_pixels(arr,ids,inputs,b['box'])
    tile_prefix=PREFIX+'-'+b['tile']
    cp=ROOT/'qa'/f'{tile_prefix}-candidate-4096.png';mp=ROOT/'qa'/f'{tile_prefix}-source-id-mask.png';rp=ROOT/'qa'/f'{tile_prefix}-report.json'
    assert not cp.exists() and not mp.exists() and not rp.exists()
    Image.fromarray(arr).save(cp);Image.fromarray(ids).save(mp)
    validation.update({'unchangedOutsideRepairSelection':True,'repairPixelCount':int(local.sum()),'mandatoryTargetsUseRepairOnly':True,
        'diskRoundtripExact':np.array_equal(np.asarray(Image.open(cp)),arr)})
    report={'createdAtUtc':now(),'tile':b['tile'],'status':'QA native protected selection; pending visual review',
        'algorithm':manifest['algorithm'],'candidateGlobalBox':b['box'],'repairGlobalBox':BOX,'repairSourceId':sid,
        'inputs':inputs,'outputs':[{'path':str(p),'sha256':m.sha(p),'dimensions':[4096,4096]} for p in [cp,mp]],
        'baseCandidate':{'path':str(b['paths'][0]),'sha256':b['hashes'][0]},
        'baseSourceIdMask':{'path':str(b['paths'][1]),'sha256':b['hashes'][1]},
        'baseReport':{'path':str(b['paths'][2]),'sha256':b['hashes'][2]},
        'baseValidation':b['baseValidation'],'validation':validation,
        'selectionDerivation':{k:manifest[k] for k in ['sourceMask','localSelectionMask','backgroundGuard','guardParameters']},
        'sourceIdPixelFormula':'(tile-local x + candidateGlobalBox.x0 - source.nativeGlobalBox.x0, tile-local y + candidateGlobalBox.y0 - source.nativeGlobalBox.y0)',
        'script':{'path':str(Path(__file__)),'sha256':m.sha(Path(__file__))}}
    dump(rp,report);manifest['tiles'].append({'tile':b['tile'],'prefix':tile_prefix,'candidate':report['outputs'][0],'validation':validation})
dump(ROOT/'qa'/f'{PREFIX}-manifest.json',manifest)
print(json.dumps({'prefix':PREFIX,'guardPixels':int(guard.sum()),'selectedPixels':int(selected.sum())}))
