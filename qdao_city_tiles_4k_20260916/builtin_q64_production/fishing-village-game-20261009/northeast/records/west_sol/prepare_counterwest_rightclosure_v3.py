from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image
name='r06_c11_counterwest-rightclosure-v3';gb=[43008,22413,44262,23667];b=[300,770,800,1230]
spec=[('r06_c11_p23','junction-r2c2-v1'),('r06_c11_p24','v2'),('r06_c11_p33','lowerclosure-v2'),('r06_c11_p34','v2'),('r06_c11_p43','v2'),('r06_c11_p44','v6')]
im=Image.new('RGB',(1254,1254));con=[]
for p,v in spec:
 path=w.Z/f'native/{p}-{v}-west_sol.png';co=w.coords(p);cb=co['coreGlobalBox'];nb=co['nativeGlobalBox'];e=dict(**w.ref(path),coordinates=co,provenance=w.evidence(path))
 t=[max(gb[0],cb[0]),max(gb[1],cb[1]),min(gb[2],cb[2]),min(gb[3],cb[3])]
 if t[0]>=t[2] or t[1]>=t[3]:continue
 sc=[t[0]-nb[0],t[1]-nb[1],t[2]-nb[0],t[3]-nb[1]];at=[t[0]-gb[0],t[1]-gb[1]]
 im.paste(Image.open(path).crop(sc),at);con.append(dict(patch=p,source=e,sourceCropBox=sc,targetPasteAt=at))
base=w.Z/f'guides/{name}.unmasked-native-target.png';im.save(base)
masked=im.copy();masked.paste((208,205,203),b);guide=w.Z/f'guides/{name}.hole-guide.png';masked.save(guide)
refs=w.mandatory()+[w.ref(guide,'fixed native coordinate source with nonfinal hole'),w.ref(base,'identical scale unmasked actual junction')]
prompt="""Image editing. Exactly native1254x1254 square fixed-coordinate patch. Attachment4 is exact native art with an edit hole [300,770,800,1230], attachment5 is the unmasked original at the identical scale. Attachments1-3 are only the approved layout/daylight materials/Q Daoist style. Native worldbox [43008,22413,44262,23667]. Keep the same camera, crop, scale, geometry and daylight. Preserve all artwork outside the hole at its original pixel position. Rebuild only the neutral hole, no recompose, no zoom.
Repair the tiny native contribution splice in the existing rear wooden counter lower outline: around x473,y990 the dark timber plane and grey stone ground have an artificial rectangular step. Continue the counter lower boundary coherently between the floor outline on the WEST edge of the hole and the actual counter base/gold foot and floor on the EAST and BOTTOM edges. The floor is the same grey-blue stone route. Remove any isolated dark wood stripe over stone and any straight rectangular artificial cutoff, but retain the original dark timber wall ABOVE its physical lower edge. The panel, diagonal orange beam, existing square post, existing gold foot and foreground blue/ivory cloth display must keep their original positions and scale. The foreground cloth cabinet diagonal top beam crossing the hole is real: preserve its continuous exact original contour, blue cloth rolls, ivory cloth, ropes and timber frame. Do not add a new post/foot or move any architecture. No extra cabinet, lantern, jars, props, people, text or UI. Match existing fine hand-painted rounded material facets, warm upper-left daylight and grey-blue natural slab joints. The hole must meet all original edge contours with no artificial color stripe or geometric step."""
pp=w.R/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8');w.write(w.R/f'{name}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{name}.plan.json',dict(schemaVersion=1,name=name,nativeGlobalBox=gb,expectedSize=[1254,1254],holeBox=b,proposedContributionBox=b,references=refs,base=w.ref(base),guide=w.ref(guide),originalQuadrants=con,prompt=w.ref(pp),actualModel=None,actualQuality=None,formalAccepted=False,operation='nonfinal guide only; exact integer native core crop/paste with neutral edit hole'))
print(name)

