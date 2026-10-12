from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent
basepath=D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png'
base=Image.open(basepath).convert('RGBA');guide=Image.new('RGBA',(1254,1254),(0,0,0,0))
rect=[350,280,950,830];strips=[[0,0,1254,280],[0,830,1254,1254],[0,280,350,830],[950,280,1254,830]]
for box in strips:guide.paste(base.crop(box),box[:2])
outside=np.ones((1254,1254),dtype=bool);outside[280:830,350:950]=False
assert np.array_equal(np.asarray(guide)[outside],np.asarray(base)[outside])
path=D/'r12c08-wall-rock-conditioned-v6-cross-cutout-guide-native1254.png';assert not path.exists();guide.save(path)
prompt='''Complete ONLY the rectangular transparent opening in this1254x1254 native map guide. All opaque pixels around it are exact final current pixels. This is a local joint repair in isometric painterly Q-style daylight game art. Return the same frame and native scale, fully opaque1254x1254.

The missing opening is x350..949,y280..829. Reconstruct a connected gray/cyan stone coping course, lower masonry course, natural green crevice leaves and rounded foreground rocks inside this opening. Join the exact existing stone edges, dark gaps, plants and rock outlines entering from ALL FOUR opaque boundaries. Those outer pixels must stay in their supplied positions. Use each edge silhouette as a hard boundary condition. All existing wood and rails are outside the repair and remain unchanged.

Connect the stone wall as one believable masonry structure with coherent isometric block courses and a natural foreground boulder group. Use a stone joint or short coping return inside the opening as necessary to connect neighboring courses at their original fixed positions; no abrupt level jumps, rectangular splices or truncated leaves. The vertical line x618 passes THROUGH the repair; there must be no straight vertical discontinuity there. The bottom boundary y830 is exact selected lower-rock and wall context; upper rocks and leaves must meet it without a horizontal cut or notch. Do not draw a new outline over the opaque bottom rock.

At the left x350 and top y280 boundaries, continue the current coping and foreground boulder contours exactly where they enter the opening. At the right x950 boundary, connect to the current coping-block upper face, front face, lower wall course and dark joints exactly where they enter the opening. Keep the distinctive block corners and wall gaps at these fixed endpoints. No moving the outer stone course or extending the repair outside the opening.

Preserve natural gray/cyan stone, its crisp rounded edges and painterly texture, green leaf scale, daylight colors, camera and perspective. No new architecture, props, posts, rails, characters, UI or text. No blur, rescale, crop, global recolor, haze or feathering. Do not redraw the opaque surroundings. The opening is a guide hole only; fill it with native connected art, no transparency in the final.'''
req=json.loads((D/'r12c08-wall-rock-conditioned-v2.request.json').read_text(encoding='utf-8'))
req.update(preparedAtUtc=datetime.now(timezone.utc).isoformat(),status='prepared_for_actual_builtin_v6',
           referenceRoles=['sole edit target: exact current native surroundings with unfilled local joint region'],
           subagentGenerationPermission='Root authorized minimum necessary cross-seam provisional repair on c09/p24; canonical selections remain root-owned.')
req['toolInput']={'prompt':prompt,'referenced_image_paths':[str(path)],'transparent_background':False}
req['editRegions']=[{'id':'G4_G5_joint','worldBox':[32500,45530,33100,46080],'guideBox':rect,'affectedNativeCores':['r12_c08/p14','r12_c09/p11'],'southFixedBoundaryWorldY':46080}]
for suffix,data in [('.prompt.txt',prompt+'\n'),('.request.json',json.dumps(req,indent=2,ensure_ascii=False)+'\n')]:
    (D/('r12c08-wall-rock-conditioned-v6'+suffix)).write_text(data,encoding='utf-8')
record={'schemaVersion':1,'guide':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'source':str(basepath),'sourceSha256':hashlib.sha256(basepath.read_bytes()).hexdigest(),
        'unfilledGuideBox':rect,'worldBox':[32500,45530,33100,46080],'dimensions':[1254,1254],
        'exactNativeCropPieces':strips,'outsideNativeReplayExact':True,
        'operation':'Paste exact native crops, leave joint opening unfilled; no synthetic geometric repair.',
        'resampling':False,'sourceArtModified':False,'canonicalModified':False,'formalAccepted':False}
(D/'r12c08-wall-rock-conditioned-v6.guide-provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guide':str(path),'request':str(D/'r12c08-wall-rock-conditioned-v6.request.json')}))
