from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image
name='r06_c11_counterwest-lowerclosure-v2';gb=[42381,22413,43635,23667];b=[450,600,1100,1130]
items={}
for p in ['r06_c11_p22','r06_c11_p23','r06_c11_p32','r06_c11_p33']:
 path=w.Z/f'native/{p}-junction-r2c2-v1-west_sol.png';co=w.coords(p);items[p]=dict(**w.ref(path),coordinates=co,provenance=w.evidence(path))
im=Image.new('RGB',(1254,1254));con=[]
for p,e in items.items():
 nb=e['coordinates']['nativeGlobalBox'];cb=e['coordinates']['coreGlobalBox']
 cb=[cb[0],cb[1],cb[2],nb[3] if '_p3' in p else cb[3]]
 t=[max(gb[0],cb[0]),max(gb[1],cb[1]),min(gb[2],cb[2]),min(gb[3],cb[3])]
 if t[0]>=t[2] or t[1]>=t[3]:continue
 sc=[t[0]-nb[0],t[1]-nb[1],t[2]-nb[0],t[3]-nb[1]];at=[t[0]-gb[0],t[1]-gb[1]]
 im.paste(Image.open(e['path']).crop(sc),at);con.append(dict(patch=p,source=e,sourceCropBox=sc,targetPasteAt=at))
base=w.Z/f'guides/{name}.unmasked-native-target.png';im.save(base)
masked=im.copy();masked.paste((208,205,203),b);guide=w.Z/f'guides/{name}.hole-guide.png';masked.save(guide)
refs=w.mandatory()+[w.ref(guide,'fixed native 1:1 original with nonfinal rectangular hole'),w.ref(base,'original target at exact same coordinate frame')]
prompt="""Image editing. Return exactly native1254x1254. Attachments1-3 are the approved village layout/material/Q Daoist painterly style. Attachment4 is exact fixed-coordinate native art with one neutral edit hole [450,600,1100,1130]. Attachment5 is its unmasked native original context at the identical scale. Worldbox [42381,22413,43635,23667]. Preserve all original outside-hole geometry, proportions, crop, colors and light. Fill the hole only with coherent native art. No zoom, no new whole scene.
The EXISTING rear counter west end post and gold foot above the hole are already complete, leave that upright unchanged. Its dark timber wall ends above the stone ground at the visible base line. The horizontal old dark timber stripe across grey stone inside the hole at y742 is an artificial splice from the prior source, not real geometry: REMOVE that stray stripe and continue the stone pavement and the rear counter coherent lower outline. The real orange wood beam and dark vertical timber panel on the upper-right continue unchanged at their original scale and end with the same existing solid gold-foot support. Cleanly resolve the stone ground immediately below that rear counter, retaining the original slab joint contours from outside the hole. The separate blue-and-ivory cloth display in the foreground at bottom-right is already real: preserve its original diagonally cropped orange timber frame, corner, blue patterned cloth, ivory cloth, red tassel and gold decoration at the same positions. Do not move either counter, extend timber across the open road, invent a new post, duplicate a foot, or turn the ground into a new wood panel. The left half remains broad open grey stone route. No added props, furniture, people, text or UI. Bright warm daylight upper-left, crisp rounded hand-painted facets and clean edges, same Q Daoist style as the existing native source. Repair all contour and shading discontinuities in the edit hole with no horizontal stripe or rectangle."""
pp=w.R/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8');args=w.R/f'{name}.actual-arguments.json';w.write(args,dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{name}.plan.json',dict(schemaVersion=1,name=name,nativeGlobalBox=gb,expectedSize=[1254,1254],holeBox=b,proposedContributionBox=b,references=refs,base=w.ref(base),guide=w.ref(guide),originalQuadrants=con,prompt=w.ref(pp),actualModel=None,actualQuality=None,formalAccepted=False,operation='nonfinal guide only; exact integer native crop/paste plus neutral hole'))
print(str(args))

