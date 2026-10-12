"""Mechanical native conditioning guide with an unfilled region; not repaired art."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent
basepath=D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png'
base=Image.open(basepath).convert('RGBA')
guide=Image.new('RGBA',(1254,1254),(0,0,0,0))
rect=[350,280,618,830]
strips=[[0,0,1254,280],[0,830,1254,1254],[0,280,350,830],[618,280,1254,830]]
for crop in strips: guide.paste(base.crop(crop),crop[:2])
outside=np.ones((1254,1254),dtype=bool);outside[280:830,350:618]=False
assert np.array_equal(np.asarray(guide)[outside],np.asarray(base)[outside])
assert guide.getchannel('A').crop(rect).getextrema()==(0,0)
path=D/'r12c08-wall-rock-conditioned-v5-cutout-guide-native1254.png'
assert not path.exists();guide.save(path)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prompt='''Fill ONLY the transparent rectangular missing region in this1254x1254 image. It is a native crop assembly with exact final pixels around all four sides. Produce the same opaque1254x1254 frame with the missing local masonry/rock area completed. Do not reconstruct, move or redesign the surrounding opaque pixels.

The missing rectangle is exactly x350..617,y280..829. Copy every opaque surrounding pixel unchanged. In the empty rectangle, draw the LEFT continuation of the existing RIGHT coping block, lower wall course, crevice plants and rounded foreground boulder. The right x618 boundary is fixed; the bottom y830 boundary is fixed; the left x350 and top y280 are fixed too. Continue the actual edges entering from those boundaries, using their exact positions.

At right edge x618, the existing coping top/front break is around y410 and its front face underside/dark joint is around y535. Draw the missing left portion of that coping slab to meet those two exact right endpoints. Do not deepen the fixed right slab. Continue the actual second-course silhouette and plant gaps entering from the right. The missing slab can have a natural rounded masonry joint or short return as needed to connect the fixed left and right courses, but no abrupt rectangular cut.

At the lower right corner of the missing region, continue the fixed small foreground boulder's rounded upper outline from the right at x618,y740 toward the bottom at x503,y830. It must be a single rounded boulder, with natural green gaps; no vertical cliff at x618 and no flat horizontal ledge along y830. Join the exact existing bottom outline.

Maintain the native scale and crisp painterly Q-style daylight stone texture/color of the surrounding pixels. Keep all wood and the approved rails exactly unchanged. No added architecture, props, post, rails, characters, text or UI. No blur, crop, scale change, haze, global recolor, feathering or repaint of opaque areas. The transparent region is only an unfilled guide area, not a transparent final asset. Final image is fully opaque.'''
req=json.loads((D/'r12c08-wall-rock-conditioned-v2.request.json').read_text(encoding='utf-8'))
req.update(preparedAtUtc=datetime.now(timezone.utc).isoformat(),status='prepared_for_actual_builtin_v5',
           referenceRoles=['sole edit target: mechanically assembled exact native opaque surrounding strips; transparent hole is unfilled conditioning only'],
           subagentGenerationPermission='Root explicitly authorized actual built-in imagegen in this directory after successful current tool check.')
req['toolInput']={'prompt':prompt,'referenced_image_paths':[str(path)],'transparent_background':False}
(D/'r12c08-wall-rock-conditioned-v5.prompt.txt').write_text(prompt+'\n',encoding='utf-8')
(D/'r12c08-wall-rock-conditioned-v5.request.json').write_text(json.dumps(req,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
record={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'guide_only_not_repaired_art','guide':str(path),'guideSha256':sha(path),
        'base':str(basepath),'baseSha256':sha(basepath),'dimensions':[1254,1254],
        'unfilledRectangle':rect,'sourceNativeStrips':strips,'outsideNativePixelReplayExact':True,
        'operation':'Paste four exact native crops into an RGBA guide canvas; leave faulty region unfilled. No replacement geometric art drawn.',
        'resamplingApplied':False,'syntheticRepairApplied':False,'canonicalModified':False}
(D/'r12c08-wall-rock-conditioned-v5.guide-provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guide':str(path),'request':str(D/'r12c08-wall-rock-conditioned-v5.request.json')}))
