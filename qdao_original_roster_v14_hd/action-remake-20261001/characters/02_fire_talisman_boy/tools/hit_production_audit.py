from pathlib import Path
from PIL import Image
import json
root = Path(__file__).resolve().parent.parent
inventory = json.loads((root / 'inventory-hit.json').read_text(encoding='utf-8-sig'))
results = []
for entry in inventory['frames']:
    p = root / entry['path']
    with Image.open(p) as im:
        alpha = im.getchannel('A')
        hist = alpha.histogram()
        bbox = alpha.point(lambda a:255 if a>8 else 0).getbbox()
        results.append(dict(action=entry['action'], direction=entry['direction'], frame=entry['frame'], path=entry['path'], dimensions=list(im.size), mode=im.mode, bbox_alpha_gt8=bbox, transparent_pixels=hist[0], opaque_pixels=hist[255], semitransparent_pixels=sum(hist[1:255]), floor_difference_diagnostic=(bbox[3]-1-920 if bbox else None), note='bbox is diagnostic only; no alignment correction, rescaling or pixel mutation performed'))
report = {'root_anchor':[512,920], 'frames':results, 'visual_acceptance':'requires actual pose/camera/ground and full-sequence review'}
(root/'records/hit-technical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
