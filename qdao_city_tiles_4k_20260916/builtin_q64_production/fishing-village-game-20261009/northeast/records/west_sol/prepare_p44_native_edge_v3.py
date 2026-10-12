from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import west_sol as w
from PIL import Image,ImageDraw
p='r06_c11_p44';v='v3';base=w.Z/'native/r06_c11_p44-v2-west_sol.png'
plan=w.read(w.R/'r06_c11_p44-v2.plan.json')
im=Image.open(base).convert('RGB')
for e in plan['nativeEdgeSources']:im.paste(Image.open(e['path']).convert('RGB').crop(e['sourceCropBox']),tuple(e['targetPasteAt']))
target=w.Z/'guides/r06_c11_p44-v3-west_sol-native-target.png';hole=w.Z/'guides/r06_c11_p44-v3-west_sol-native-hole.png'
assert not target.exists() and not hole.exists()
im.save(target);ImageDraw.Draw(im).rectangle((750,230,1119,1253),fill=(255,0,255));im.save(hole)
refs=w.mandatory()+[w.ref(hole,'native edit guide with magenta request-only repair area; not final'),w.ref(target,'unmasked native target preserving real adopted right230 and top230 anchors')]
prompt='Use case: precise image edit. Produce the same1254 by1254 native coordinate frame. Attachments1,2,3 are mandatory approved layout/daylight materials/rounded painterly Q Daoist style; ignore people/UI/text/night. Attachment4 is an exact native edit guide, with ONLY the magenta repair area requiring repaint. Attachment5 is its unmasked target for native scale and surrounding composition. Rebuild only the marked RIGHT transition into crisp native painting matching the real fixed right edge x1120..1254 and top y0..230. The sharp right area is the adopted neighbor in its real world location and cannot be redesigned. Existing fish bodies, ice, warm timber diagonal frame, lower stretchers, legs and stone paving must each continue smoothly from it into the missing transition, with native contour positions. The original left counter front currently ends wrongly near the right edge: resolve it into the existing open fish-display bays and timber supporting structure shown in the right native anchor instead of extending a solid wood panel across the existing fish. Match the upper-right fish body and diagonal rim, the middle fish bay and orange frame, the warm open lower support/stretcher and the floor strip, and the lower existing fish-display rim. Keep the entire left artwork and existing large top counter rim/foot unchanged. Do not add a new stall or fish rows, shrink the scene, move posts, change camera, duplicate edge objects, or leave magenta/blur/splice stripe. Daylight fine faceted brushwork and continuous contours. Exact core[115,115,1139,1139] world native[43917,23437,45171,24691].'
(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
new=dict(plan);new.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(hole),base=w.ref(base),editTarget=w.ref(target),requestedHoleBox=[750,230,1120,1254],formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',new)
w.write(w.R/f'{p}-v2.rejection.json',dict(native=w.ref(base),reason='Native RIGHT seam blocking mismatch: generated solid counter front replaces adopted neighbor fish bay and supporting stretcher. TOP seam passes; preserve candidate and repaint native right transition.',formalAccepted=False))
# exact four-core junction evidence
paths=[base,w.Z/'native/r06_c12_p41-v1.png',w.Z/'native/r06_c11_p34-v2-west_sol.png',w.Z/'native/r06_c12_p31-v1.png']
out=Image.new('RGB',(256,256))
for path,box,at in [(paths[2],[1011,1011,1139,1139],[0,0]),(paths[3],[115,1011,243,1139],[128,0]),(paths[0],[1011,115,1139,243],[0,128]),(paths[1],[115,115,243,243],[128,128])]:out.paste(Image.open(path).convert('RGB').crop(box),tuple(at))
qp=w.Z/'qa/west_sol/r06_c11_p44-v2/junction.ne-right.native-1to1.png';out.save(qp)
print(json.dumps({'guide':str(hole),'target':str(target),'junction':str(qp)}))
