from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent
source=D/'r12c08-wall-rock-conditioned-v6-cross-bounded-preview.png'
base=Image.open(source).convert('RGBA');guide=Image.new('RGBA',(1254,1254),(0,0,0,0))
kept=[[0,0,1254,280],[0,830,1254,1254],[0,280,350,830],[950,280,1254,830],[414,344,886,766]]
ring=[[350,280,950,344],[350,766,950,830],[350,344,414,766],[886,344,950,766]]
for box in kept:guide.paste(base.crop(box),box[:2])
path=D/'r12c08-wall-rock-conditioned-v7-border-guide-native1254.png';assert not path.exists();guide.save(path)
prompt='''Fill only the narrow transparent rectangular BORDER in this native1254x1254 map guide. The repaired center and original surrounding pixels are opaque and fixed. Return the same frame and pixel scale, opaque1254x1254.

The four missing border strips are TOP x350..949,y280..343; BOTTOM x350..949,y766..829; LEFT x350..413,y344..765; RIGHT x886..949,y344..765. Reconstruct only those strips so they match the exact opaque contours and colors on BOTH sides of each strip. Keep the central rectangle x414..885,y344..765 unchanged and keep all surrounding opaque pixels unchanged.

On the left outer edge x350, remove the truncated crevice plant and join its original neighboring leaves naturally; keep the coping/front-face and next-course edges at their existing endpoint positions. Along top y280, join the exact stone top faces, dark diagonal gaps and small leaves without cut tips or material steps. Along right x950, keep the existing stone corners, course lines and gaps at their original coordinates; no masonry level shift. Along bottom y830, join the existing rounded boulder and crevice foliage silhouettes to the fixed native rocks and leaves below. Remove any horizontal cutoff of green leaves, dark plant gaps or rock texture. Do not replace a cut with a different displaced outline. At every inner edge, connect to the existing repaired center in its original positions.

The center already has coherent wall geometry and the corrected G4/G5 junction: preserve it. Keep all wood, rails and posts unchanged. Crisp rounded painterly Q-style daylight game art, same gray/cyan stone and green leaves. No new props, structures, rails, posts, text or UI. No blur, haze, crop, rescale, feathering or global recolor. Fill the guide's transparent border only; final complete frame must be opaque.'''
req=json.loads((D/'r12c08-wall-rock-conditioned-v6.request.json').read_text(encoding='utf-8'))
req.update(preparedAtUtc=datetime.now(timezone.utc).isoformat(),status='prepared_for_actual_builtin_v7',referenceRoles=['sole edit target: exact v6 repaired center and exact original outer native context; mechanical unfilled border guide'])
req['toolInput']={'prompt':prompt,'referenced_image_paths':[str(path)],'transparent_background':False}
req['editRegions']=[{'id':'outer_border','guideBoxes':ring,'worldBoxes':[[x0+32150,y0+45250,x1+32150,y1+45250] for x0,y0,x1,y1 in ring]}]
(D/'r12c08-wall-rock-conditioned-v7.request.json').write_text(json.dumps(req,indent=2)+'\n',encoding='utf-8')
(D/'r12c08-wall-rock-conditioned-v7.prompt.txt').write_text(prompt+'\n',encoding='utf-8')
mask=np.zeros((1254,1254),bool)
for x0,y0,x1,y1 in ring:mask[y0:y1,x0:x1]=True
assert np.array_equal(np.asarray(base)[~mask],np.asarray(guide)[~mask])
record={'schemaVersion':1,'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'guide':str(path),'guideSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'keptNativeCrops':kept,'unfilledRing':ring,
        'outsideMissingRingPixelReplayExact':True,'operation':'Mechanical exact crop composition, leave border strips unfilled; no synthetic repair art.',
        'resampling':False,'canonicalModified':False,'formalAccepted':False}
(D/'r12c08-wall-rock-conditioned-v7.guide-provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guide':str(path),'request':str(D/'r12c08-wall-rock-conditioned-v7.request.json')}))
