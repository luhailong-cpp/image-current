from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image
name='r06_c11_junction_r2_c2-v1'
gb=[42381,21901,43635,23155]
items={}
for p,v in [('r06_c11_p22','v2'),('r06_c11_p23','v1'),('r06_c11_p32','v1'),('r06_c11_p33','v2')]:
 path=w.Z/f'native/{p}-{v}-west_sol.png';co=w.coords(p);items[p]=dict(**w.ref(path),coordinates=co,provenance=w.evidence(path))
im=Image.new('RGB',(1254,1254))
con=[]
for p,e in items.items():
 cb=e['coordinates']['coreGlobalBox'];nb=e['coordinates']['nativeGlobalBox']
 b=[max(gb[0],cb[0]),max(gb[1],cb[1]),min(gb[2],cb[2]),min(gb[3],cb[3])]
 crop=[b[0]-nb[0],b[1]-nb[1],b[2]-nb[0],b[3]-nb[1]];at=[b[0]-gb[0],b[1]-gb[1]]
 im.paste(Image.open(e['path']).crop(crop),at);con.append(dict(patch=p,source=e,sourceCropBox=crop,targetPasteAt=at))
base=w.Z/f'guides/{name}.unmasked-native-target.png';im.save(base)
hole=[450,510,810,1254]
masked=im.copy();masked.paste((208,205,203),hole);gp=w.Z/f'guides/{name}.hole-guide.png';masked.save(gp)
refs=w.mandatory()+[w.ref(gp,'native 1:1 coordinate junction with nonfinal neutral edit hole'),w.ref(base,'unmasked native original junction for geometry context')]
prompt="""Use case: image editing. Produce one exact 1254x1254 native patch. Attachments1-3 are approved village layout/material/Q Daoist painterly style. Attachment4 is a fixed native-coordinate junction of FOUR adjoining images, with a neutral rectangular edit hole at [450,510,810,1254]. Attachment5 is the exact unmasked original target at the same scale, for existing contours only. Replace the neutral hole in attachment4 with coherent native painting. Preserve all geometry, camera, scale, illumination and objects outside the hole pixel-position exactly. Native world box [42381,21901,43635,23155]. No zoom, no resizing, no composition change.
Repair the existing back counter west termination in this small hole: the original diagonal golden-orange timber beam and dark timber face on the RIGHT are real and must continue smoothly to a natural finished west end, with its original square wooden support and gold-toned foot, within the hole around x500..600. The truncated flat wood plane at x512,y742 is a rectangular guide splice, not a real vertical cabinet edge. Replace that artificial sharp rectangular cut with a coherent solid timber end-post and continuous short diagonal top beam, matching the exact beam and dark panel at the hole RIGHT edge. Use the unmasked target to retain the original beam angle and thick warm timber profile. The timber should end naturally on the WEST in this small hole; the entire area left of x450 stays unobstructed grey stone paving. Continue the exact existing blue-grey slab joints behind and below the wood, daylight from upper left. No new stall, whole cabinet, roof, wall, jars, cloth, fishing net, rope, lantern or freestanding unrelated furniture. The blue cloth table already at lower-right remains in its existing place. No horizontal or vertical exposure stripe across any original quadrant seam. Painterly rounded Q Daoist materials with crisp facets, clean edges and subtle wood grain, same style and scale as existing. Ignore UI/text/people/night of style attachment3."""
pp=w.R/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
args=w.R/f'{name}.actual-arguments.json';w.write(args,dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{name}.plan.json',dict(schemaVersion=1,name=name,nativeGlobalBox=gb,expectedSize=[1254,1254],holeBox=hole,proposedContributionBox=hole,references=refs,base=w.ref(base),guide=w.ref(gp),originalQuadrants=con,prompt=w.ref(pp),actualModel=None,actualQuality=None,formalAccepted=False,operation='nonfinal guide only; exact core-native crop/paste; neutral edit hole is not final pixels'))
print(str(args))

