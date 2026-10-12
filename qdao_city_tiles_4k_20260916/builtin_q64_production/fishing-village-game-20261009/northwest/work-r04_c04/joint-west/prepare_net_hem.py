from pathlib import Path
from PIL import Image
import json,hashlib
import numpy as np
D=Path(__file__).resolve().parent;R=D.parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old='r04_c03_c04_lower_net_transition_bridge_v01';name='r04_c03_c04_net_hem_bridge_v01';box=[11648,15950,12902,17204]
q=read(D/(old+'.request.json'));layout=Path(q['referenced_image_paths'][0]);im=Image.open(layout).transform((1254,1254),Image.Transform.EXTENT,tuple(x*1254/57344 for x in box),resample=Image.Resampling.BICUBIC);ids=np.zeros((1254,1254),np.uint8)
p=R/'native'/ (old+'.png');im.paste(Image.open(p).crop([0,250,1254,880]),(0,0));ids[:630]=1
p2=R/'native/r05_c03_s01_s04_v03.png';im.paste(Image.open(p2).crop([499,311,1254,935]),(0,630));ids[630:,:755]=2
# Preserve newly drawn right net/pole out to lower transition end, no guide pixel final.
im.paste(Image.open(p).crop([755,880,1254,1254]),(755,630));ids[630:1004,755:]=1
gp=D/(name+'.guide.png');ip=D/(name+'.guide-source-id.png');im.save(gp);Image.fromarray(ids).save(ip)
sources=[{'id':1,'file':str(p),'sha256':sha(p),'globalNativeBox':read(str(p)+'.generation.json')['globalNativeBox']},{'id':2,'file':str(p2),'sha256':sha(p2),'globalNativeBox':read(str(p2)+'.generation.json')['globalNativeBox']}]
for s in sources:
 yy,xx=np.nonzero(ids==s['id']);a=np.asarray(Image.open(s['file']));bb=s['globalNativeBox'];assert np.array_equal(np.asarray(im)[yy,xx],a[yy+box[1]-bb[1],xx+box[0]-bb[0]])
write(D/(name+'.plan.json'),{'globalNativeBox':box,'globalCoreBox':[11763,16065,12787,17089],'guide':str(gp),'sha256':sha(gp),'sourceIdMap':str(ip),'sources':sources,'layoutOnlyPixels':int((ids==0).sum()),'reason':'Include whole existing southern rounded blue-net hem and clean sand below so hardcut can avoid all mesh strands; previous lower-v1 south failed.'})
prompt='''Use case: precise-object-edit / compositing. Render one 1254x1254 native patch for a Q painterly fishing village map, no resizing or reframing.
Images1,2,3 are whole-map layout and mandatory independent detail/mail painting style references. Image4 is the ONLY edit/framing target. Match its exact square close-up global [11648,15950,12902,17204].
Repair the bottom half of this hanging slate-blue fishing net, including its COMPLETE rounded lower hem and the warm clean sand just below. Image4 has a hard source join around y630 where the upper corrected net meets an existing southern net. Reconnect all ropes through that join naturally; eliminate abrupt clipped mesh and duplicate/floating rope ends. Preserve the net's visible lower rounded silhouette from the bottom-left existing native region: it curves down near y1100 and finishes with thick rope and shadow, leaving clean sand beneath. Do not keep extending this left net out through bottom edge; its hem is already visible in the target.
LOCK THE FRAME and precise native connections: top230px (all mesh knots and lines) remain unchanged. The left115px visible fold and sand edge remain unchanged. Existing correct right net/pole x1139..1254,y0..1004 stays aligned. Bottom left755px last100px are clean existing sand, match them with no invented ropes or props. Do not move the lower-left outer folded border. The internal central mesh can be redrawn to clean enclosed quadrilateral holes with ropes tying into real knots. Every thin rope meets the thick hem, no loose T-end or clipping at y630. Prefer a continuous draping contour rather than a flat straight lower cut.
Lower-right x755..1254,y1004..1254 is still fuzzy layout guidance only: finish with newly painted native-detail sand/right post/right net where required by the preceding upper pixels, keeping objects cropped naturally at the right frame. Do not reproduce blur or a rectangular block. No added large props, stones, cracks, plants, characters, letters, grids or interface. Same gentle daylight, dark-blue grey twisted rope, bright sand paint, rounded polished Q treatment. Preserve the upper and left geometry exactly; repair internal transition and complete the blue net hem.'''
pf=D/(name+'.prompt.txt');pf.write_text(prompt,encoding='utf-8');q.update(name=name,prompt=prompt,promptFile=str(pf),globalNativeBox=box,globalCoreBox=[11763,16065,12787,17089]);q['referenced_image_paths'][-1]=str(gp);q['references'][-1]={'file':str(gp),'sha256':sha(gp),'role':'edit target; complete net hem with exact old and new native anchors and lower-right layout-only pixels'}
write(D/(name+'.request.json'),q);print(json.dumps({'name':name,'guide':str(gp),'box':box,'guideOnlyPixels':int((ids==0).sum())}))

