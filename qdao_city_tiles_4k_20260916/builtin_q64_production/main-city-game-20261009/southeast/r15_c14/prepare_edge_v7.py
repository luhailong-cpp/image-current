from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');Z=T.parent;R=T/'repairs/edge-continuity-v7-20261012';R.mkdir()
def read(p):return json.loads(Path(p).read_text())
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
base=T/'candidate/r15_c14-4k-external-partial-v6-20261012.png';refs=read(T/'records/p01_01_v20261012T135016_73f165cf.request.json')['referenced_image_paths'][:3]
cfg={'W2':{'edge':'west','start':600,'apply':[0,1080,90,1400],'instruction':'Only repair the exposed LEFT END of the short blue-inlay section around local y540..740. Continue the pale border from immutable left half into the right with a thin natural beveled grout closure, so the blue inset ends as complete closed stone rather than a clipped vertical blue edge. Match the incoming old grout at each endpoint. Preserve the blue inset width beyond this tiny left cap and the lower angled continuation. Do not move or redraw the general paving grid.'},
'WL':{'edge':'west','start':2842,'apply':[0,2842,180,4096],'instruction':'Only repair the straight texture/value discontinuity at x627 on the RIGHT side: continue the LEFT side stone cladding and pale paving material and natural daylight tone into the first180 right pixels, naturally merging into the untouched right-side finish. Preserve every wall ledge, grout outline, bevel, shadow position and slab shape exactly. Paint the texture transition inside this strip so there is no vertical rectangular texture edge at either boundary. Do not alter any geometry or create a line, new stone, object or lettering.'},
'N4':{'edge':'north','start':2842,'apply':[2940,0,4096,180],'instruction':'Only repair the straight texture/value discontinuity at y627 on the LOWER side: continue the upper-side pale stone painterly microtexture and light into the first180 lower pixels, naturally merging into the untouched bottom-side finish. Preserve EVERY visible grout outline and slab corner exactly, including the blue inset end at far left; do not reroute or invent joints. Paint texture transition inside this strip so neither edge looks like a rectangular patch. Do not move geometry, recolor the entire image or add anything.'}}
for id,c in cfg.items():
 d=R/id;d.mkdir();edge=c['edge'];s=c['start'];neighbor=read(Z/('r15_c13' if edge=='west' else 'r14_c14')/'candidate/latest-assembly.json');npth=Path(neighbor['candidate']['path']);assert rec(npth)['sha256']==neighbor['candidate']['sha256'];target=Image.new('RGB',(1254,1254))
 if edge=='west':
  piece1=[3469,s,4096,s+1254];piece2=[0,s,627,s+1254];paste2=[627,0];origin=[-627,s]
 else:
  piece1=[s,3469,s+1254,4096];piece2=[s,0,s+1254,627];paste2=[0,627];origin=[s,-627]
 target.paste(Image.open(npth).crop(piece1),(0,0));target.paste(Image.open(base).crop(piece2),tuple(paste2));tp=d/'target-native-1254.png';target.save(tp)
 x0,y0,x1,y1=c['apply'];cx,cy=origin;mask=np.zeros((1254,1254),dtype='uint8');mask[y0-cy:y1-cy,x0-cx:x1-cx]=255;mp=d/'edit-mask-1254.png';Image.fromarray(mask).save(mp)
 prompt='Use case: precise-object-edit. LAST image is actual native1254x1254 close crop of adjoining map cores. '+('LEFT627 columns are immutable neighbor; RIGHT627 columns are new tile.' if edge=='west' else 'TOP627 rows are immutable neighbor; BOTTOM627 rows are new tile.')+' Second-last image marks the only editable white strip; BLACK must stay unchanged. First3 are approved material references only; exact target geometry overrides them. '+c['instruction']+' This is a highly localized native repair. No zoom, resize, warp, camera shift, reframe or whole-image recoloring. Return1254x1254 native PNG.'
 req={'prompt':prompt,'referenced_image_paths':refs+[str(mp),str(tp)],'transparent_background':False};(d/'request.json').write_text(json.dumps(req,indent=2));(d/'prompt.txt').write_text(prompt);(d/'preparation.json').write_text(json.dumps({'id':id,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(T/'candidate/r15_c14-context-4326-external-partial-v6-20261012.png'),'neighborSelection':neighbor,'sourcePieces':[{'source':rec(npth),'crop':piece1,'paste':[0,0]},{'source':rec(base),'crop':piece2,'paste':paste2}],'origin':origin,'apply':c['apply'],'references':[rec(p) for p in req['referenced_image_paths']],'request':rec(d/'request.json'),'nativeSize':[1254,1254],'noResize':True,'noHalo':True,'neighborPixelsImmutable':True},indent=2))
print(str(R))

