"""Native-scale repair inputs only. Does not paint, resize, or modify source art."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

Z = Path(__file__).resolve().parent.parent
QA = Z / 'qa'

def ref(p):
    p = Path(p)
    return {'path': p.as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

def save_json(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    assembly_path = QA / 'full-tile-r09_c06-assembly.json'
    assembly = json.loads(assembly_path.read_text(encoding='utf-8-sig'))
    source_ref = assembly['context']
    assert ref(source_ref['path'])['sha256'] == source_ref['sha256']
    assert source_ref['sha256'] == '65e22c3a13c2c3cf0825f7cd808e0454b760e452d3c56de498c6c183350b2435'
    context = Image.open(source_ref['path']).convert('RGB')
    assert context.size == (4326, 4326)
    groups = [
        {
            'id': 'a-fish-leftwood', 'tileBox': [485, 885, 1739, 2139],
            'priority': 1,
            'brief': 'Reconnect silver fish bodies/fins where cut at x~1024. Smooth the two nearby upper wood bands and lower left post band, retaining every fish position, tray geometry and post silhouette.',
            'regions': [
                {'id': 'a-upper-left-post', 'finding': 'F04.1', 'tileBounds': [575, 965, 845, 1185], 'margin': 45},
                {'id': 'a-upper-rail-face', 'finding': 'F04.2', 'tileBounds': [855, 935, 1040, 1090], 'margin': 35},
                {'id': 'a-silver-fish', 'finding': 'F01', 'tileBounds': [895, 1280, 1235, 1815], 'margin': 50},
                {'id': 'a-lower-left-post', 'finding': 'F05.1', 'tileBounds': [810, 1900, 1130, 2085], 'margin': 40},
            ],
        },
        {
            'id': 'b-centerwood', 'tileBox': [1240, 960, 2494, 2214],
            'priority': 2,
            'brief': 'Smooth the central post upper and lower material bands and the small front counter-corner band. Retain wood grain direction, highlights, silhouettes, tray rims and all fish.',
            'regions': [
                {'id': 'b-upper-center-post', 'finding': 'F04.3', 'tileBounds': [1840, 980, 2155, 1140], 'margin': 35},
                {'id': 'b-lower-center-post', 'finding': 'F05.3', 'tileBounds': [1740, 1880, 2160, 2080], 'margin': 45},
                {'id': 'b-counter-corner', 'finding': 'F05.2', 'tileBounds': [1310, 2035, 1530, 2205], 'margin': 40},
            ],
        },
        {
            'id': 'c-rail-redtray', 'tileBox': [2500, 630, 3754, 1884],
            'priority': 3,
            'brief': 'Straighten the small 15-20px upper rail edge step and 10-15px rear red-fish tray rim step. Preserve the two separate diagonal angles, fish bodies and all neighboring geometry.',
            'regions': [
                {'id': 'c-upper-rail', 'finding': 'F02', 'tileBounds': [2975, 995, 3310, 1210], 'margin': 45},
                {'id': 'c-redtray-rim', 'finding': 'F03', 'tileBounds': [2975, 1330, 3165, 1530], 'margin': 40},
            ],
        },
        {
            'id': 'd-frontpost-paving', 'tileBox': [2460, 2520, 3714, 3774],
            'priority': 4,
            'brief': 'Smooth the horizontal wood-color band above the front post foot. Repair two small offsets in the diagonal paving joints below it. Preserve the already corrected bare wooden foot, basket, net shelf and ground contact shadow.',
            'regions': [
                {'id': 'd-front-post-band', 'finding': 'F06', 'tileBounds': [2870, 2890, 3210, 3105], 'margin': 45},
                {'id': 'd-paving-joint', 'finding': 'F09', 'tileBounds': [2900, 3445, 3160, 3740], 'margin': 45},
            ],
        },
    ]
    all_bounds = []
    for group in groups:
        l, t, r, b = group['tileBox']
        assert r-l == b-t == 1254
        box = [l+115, t+115, r+115, b+115]
        assert 0 <= box[0] < box[2] <= 4326 and 0 <= box[1] < box[3] <= 4326
        p = QA / ('repair-r09_c06-' + group['id'] + '-source-native.png')
        assert not p.exists(), p
        crop = context.crop(box)
        crop.save(p)
        assert np.array_equal(np.array(Image.open(p)), np.array(context)[box[1]:box[3], box[0]:box[2]])
        group['source'] = {**ref(p), 'size': [1254, 1254]}
        group['contextBox'] = box
        group['globalContextBox'] = [20480+l, 32768+t, 20480+r, 32768+b]
        for region in group['regions']:
            x1,y1,x2,y2=region['tileBounds']
            region['repairBounds']=[x1-l,y1-t,x2-l,y2-t]
            assert l<=x1<x2<=r and t<=y1<y2<=b
            assert x2-x1 > 2*region['margin'] and y2-y1 > 2*region['margin']
            all_bounds.append((region['id'], region['tileBounds']))
        save_json(Path(str(p)+'.derivation.json'), {'source':source_ref, 'assembly':ref(assembly_path), 'output':group['source'], 'contextBox':box, 'tileBox':group['tileBox'], 'globalBox':group['globalContextBox'], 'operation':'integer crop only, exact native RGB pixels', 'noResize':True, 'noDrawing':True})
    for i,(aid,a) in enumerate(all_bounds):
        for bid,b in all_bounds[i+1:]:
            assert min(a[2],b[2])<=max(a[0],b[0]) or min(a[3],b[3])<=max(a[1],b[1]), (aid,bid)
    result={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(), 'status':'native_repair_inputs_ready_no_generation_performed','tile':'r09_c06','baseAssembly':ref(assembly_path),'baseContext':source_ref,'expectedBaseCandidateSha256':assembly['output']['sha256'],'groups':groups,'compositingNote':'Multiple disjoint localized masks may select from the same generated 1254 image. Suggested bounds enclose findings with surrounding margin; keep all pixels outside the union on the original base. Source crop rectangles overlap only as reference context; every proposed editable bounds rectangle is pairwise disjoint.','deferred':'F08 right-halo post band needs joint context with r09_c07; do not edit against the current right image edge without neighboring source context.','scope':'Mechanical native crops and records only. No source art, gate snapshot or shared progress modified.'}
    p=QA/'repair-r09_c06-local-plan-v1.json'
    assert not p.exists(),p
    save_json(p,result)
    print(json.dumps({'plan':ref(p),'groups':[{'id':g['id'],'source':g['source'],'regionCount':len(g['regions'])} for g in groups]}))

if __name__=='__main__':
    main()
