from pathlib import Path
from datetime import datetime, timezone
import sys, json
from PIL import Image, ImageDraw
T = Path(__file__).resolve().parent
Z = T.parent
sys.path.insert(0, str(Z))
import production_v2 as p
D = T / 'bridges/shared-east-lower-02'
D.mkdir(exist_ok=False)
base = T / 'bridges/shared-east-lower-01/edit-target.png'
im = Image.open(base).convert('RGB')
assert im.size == (1254, 1254)
draw = ImageDraw.Draw(im)
draw.line([(627, 502), (627, 552)], fill=(0, 210, 255), width=4)
for x, y in [(627, 502), (627, 552)]:
    draw.ellipse((x-10, y-10, x+10, y+10), outline=(240, 0, 180), width=2)
locator = D / 'layout-locator-only.png'
im.save(locator)
prompt = '''Use case: precise-object-edit.
Edit image 1, keeping its EXACT 1254 by 1254 pixel framing, scale, tile pattern, all diamond corners and all existing grout paths. Image 2 is a layout locator only, with a cyan short vertical stroke and two magenta endpoint circles. It is NOT final art.
Make precisely one local repair: convert the cyan stroke at x627, y502 through y552 into the same thin recessed brown grout line with ivory bevel as the surrounding stone. Join the existing upper-left diagonal tip at (627,502) to the existing lower-right diagonal tip at (627,552) using this short VERTICAL jog. The two diagonal edges remain in their original positions. Do not move either endpoint or nearby gold corner. Keep the intentionally staggered diamond layout; do NOT regularize the grid or move the central gold node. The two endpoint circles and cyan guide must not appear in final art.
Match the existing hand-painted warm ivory stone texture and the existing thin brown groove, especially local width and light. Preserve every existing object and pattern outside the narrow repair x615..640, y495..560; preserve the outer 200 pixels exactly. The result is the same original map patch with only this tiny connecting stone joint completed. No new objects, no labels, no outlines, no whole-surface redraw, no blur. Return a 1254x1254 native image.'''
args = {'prompt': prompt, 'referenced_image_paths': [str(base), str(locator)], 'transparent_background': False}
(D/'prompt.txt').write_text(prompt, encoding='utf-8')
p.write_json(D/'parameters.json', args, replace=False)
p.write_json(D/'request.json', {'id':'shared-east-lower-02', 'createdAtUtc':datetime.now(timezone.utc).isoformat(), 'route':'builtin_image_gen', 'parameters':args, 'actualModel':None, 'actualQuality':None, 'imageModelPreference':'free included 2.5 preferred, built-in 2.0 fallback allowed; no paid API', 'referenceRoles':[{'file':str(base),'sha256':p.sha(base),'role':'exact native edit target, no resampling'}, {'file':str(locator),'sha256':p.sha(locator),'role':'layout-only annotation, not production pixels'}], 'worldBox':[19853,26776,21107,28030], 'tileOrigins':{'r07_c05':[3469,2200],'r07_c06':[-627,2200]}, 'nativePixels':[1254,1254], 'scopeExclusionManifest':{'file':str(Z.parents[3]/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'sha256':p.sha(Z.parents[3]/'docs/MAP_PARALLEL_SPLIT_20261013.json')}, 'productionImageEditedByCode':False}, replace=False)
print(D)
