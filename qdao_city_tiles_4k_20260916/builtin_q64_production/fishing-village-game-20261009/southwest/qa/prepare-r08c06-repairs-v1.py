import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json, hashlib, datetime
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
base=Z/'qa/full-tile-r08_c06-context-native.png'
assembly=Z/'qa/full-tile-r08_c06-assembly.json'
specs=[
('a_lantern',[2550,100,3804,1354],'Repair the broken red lantern as ONE coherent object: remove the duplicated red paper fragment and doubled gold lower rim near y=800..1000, continue exactly one smoothly rounded red body with continuous gold ribs, ONE gold bottom cap and ONE red tassel, naturally occluded by the blue canopy. Also remove the horizontal blue canopy-tip offset directly to the lantern left and connect that sloping hem cleanly. Preserve the lantern upper attachment and all overall object positions and sizes. Preserve the existing stone slab joints and blue canopy folds; unify the small background paving transition without blur. Do not change the tall wooden post at right.'),
('b_rightsign',[2957,400,4211,1654],'Repair ONLY the obvious horizontal cut running across the red ornamental sign and adjacent brown wooden post at local y approximately 630. Reconnect the red plaque silhouette and gold motif as a single continuous carved plaque; remove the small sideways step on its left edge. Preserve its upper and lower colors as fixed anchors and bridge the join smoothly without a horizontal band. Match the original wood tone and grain above and below across the same band on the tall post. No new ornaments, no redesign, no moving the plaque, lantern or canopy.'),
('c_canopyleft',[1520,1550,2774,2804],'Repair the angular brightness and texture collage seams in the blue canopy only. Continue one softly shaded woven blue fabric sheet through the middle, with a coherent fine diagonal weave and smoothly changing light. The darker upper blue and lighter lower blue near the hem are fixed color anchors: transition naturally between them; do not recolor the entire canopy to one flat color. Keep the exact canopy outline, diagonal thick folded hem and stitch line in place, smoothing any small discontinuity in the hem. Preserve all fish, tub, wooden tabletop and stone surroundings. No new folds, no objects or ornaments.'),
('d_canopyright',[2544,1550,3798,2804],'Repair the angular brightness and texture collage seams in the blue canopy only. Continue one softly shaded woven blue fabric sheet through the middle, with a coherent fine diagonal weave and smoothly changing light. The darker upper blue and lighter lower blue near the hem are fixed color anchors: transition naturally between them; do not recolor the entire canopy to one flat color. Keep the exact canopy outline, diagonal thick folded hem and stitch line in place, smoothing any small discontinuity in the hem. Preserve wooden structure and pale golden platform around it. No new folds, no objects or ornaments.'),
('e_frontcanopy',[350,2842,1604,4096],'Repair ONLY the stepped break in the diagonal upper edge of the blue canopy near local x=560,y=980. The hem must be ONE smooth continuous diagonal line across this location, with coherent woven blue fabric and tiny stitching. Fill the tiny rectangular notch with continuous blue fabric and preserve the wood and pale stone background immediately above. Preserve the red and gold sign, wooden ornamented crossbar and all paving. Do not move, resize or reframe any object.'),
('f_goldedge',[2450,2450,3704,3704],'Repair ONLY the tiny offset and material seam across the long diagonal pale-golden platform front edge near image center-right. Connect the thin highlight line and carved front fascia profile smoothly and precisely, including the small inset gold bracket and nearby panel grain. Preserve the exact original diagonal platform silhouette and bracket shape; retain the light upper platform tone and dark fascia tone. Do not change the blue canopy, columns or background.'),
('g_woodplane',[1450,2320,2704,3574],'Repair ONLY the mild vertical material and lighting seam across the brown wooden tabletop at local x around 450..750. Continue the existing warm wood grain and gradual shadow smoothly, retaining its diagonal plank direction and rounded front edge. Preserve the exact fish tub, its shadow, blue canopy and structural posts. No added objects, no recoloring the whole tabletop, no straight transition boundaries.')
]
out=[]
im=Image.open(base).convert('RGB')
for rid,b,p in specs:
 stem='r08_c06_repair_'+rid+'_v1'
 src=Z/'qa'/('repair-r08_c06-'+rid+'-source-1254.png')
 assert not src.exists()
 cb=[v+115 for v in b];im.crop(tuple(cb)).save(src)
 prompt='Use case: precise-object-edit. Edit image 1, an exact native 1254x1254 crop of our daylight hand-painted Q game map. Output exactly 1254x1254, preserve composition, scale and framing. '+p+' Preserve all unaffected source pixels, particularly a 100px outer border. Smoothly reconnect the target interior to original light and texture near all four edges. No blur, no resampling, no text, no grid, no watermark. This is a surgical seam repair, not a redesign.'
 pp=Z/'native'/(stem+'.prompt.txt');pp.write_text(prompt+'\n',encoding='utf-8')
 j={'stem':stem,'tile':'r08_c06','tool':'image_gen__imagegen','route':'builtin','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':{'tileContextBox':b,'contextBox':cb,'sourceContext':{'path':base.as_posix(),'sha256':sha(base)}},'references':[{'path':src.as_posix(),'sha256':sha(src),'dimensions':[1254,1254],'role':'exact native crop; edit target'}],'submittedParameters':{'transparent_background':False,'referenced_image_paths':[src.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None}
 (Z/'native'/(stem+'.request.json')).write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8');out.append({'id':rid,'stem':stem,'source':j['references'][0],'tileContextBox':b})
audit={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r08_c06','status':'initial_internal_qa_complete_repairs_required','baseAssembly':{'path':assembly.as_posix(),'sha256':sha(assembly)},'viewedAtOriginal':39,'qaFiles':rd(assembly)['qaFiles'] if 'qaFiles' in rd(assembly) else None,'findings':out,'notes':['Red sign support foot and h3072 stone paving are continuous; no repair needed.','Main lantern duplication and canopy collage bands block acceptance.','Northwest cliff foliage and plaza geometry passed visual inspection.'],'formalAccepted':False}
(Z/'qa/repair-r08_c06-initial-qa.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))

