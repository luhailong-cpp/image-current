from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05')
D=B/'repairs-resume-20261012';T=D/'H3-3-blue-edge-gap-v01';T.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
v05=D/'blue-direct-control-left-v05';native=v05/'native.png'
write(v05/'disposition.json',{'native':{'file':str(native),'sha256':sha(native)},'explicitlyRejected':True,'reason':'Generated blue/cream line still moves left native anchor from y1080 to approximately y987 and moves the descending grout crossing. The original annotated control line is not honored. No pixels extracted or integrated; v10 retained.','actualModel':None,'actualQuality':None})
src=D/'integrated-local-v10/r12_c05.candidate.context.png';box=[1779,2700,3033,3954]
im=Image.open(src).convert('RGB').crop(box);im.save(T/'input.png')
qa=im.copy();dr=ImageDraw.Draw(qa);dr.rectangle((578,579,689,695),outline=(255,0,255),width=3);qa.save(T/'QA-ROI-guide-not-final.png')
prompt='''Use case: precise-object-edit. Repair a single tiny paving-border interruption in image1, a native1254x1254 crop of the approved Q-style Daoist city. Image2 is approved city layout, image3 approved natural stone detail, image4 Daoist style. Image5 marks the very small repair zone in magenta for guidance only; never put the rectangle in the output.
In the small rectangle x578..689 y579..695, the cream/blue diagonal paving boundary has a short blocky interruption. Restore its thin dark groove, cream bevel and cool blue lower lip as one straight seamless continuation, using the existing segments immediately on each side as fixed anchors. Restore only the missing approximately30px portion. Match the exact existing slope and width; do not straighten or move any surrounding geometry. Keep original cream above the boundary, blue below, original crossing joints, all endpoint coordinates, all other materials, textures, tonal variation, roof and native pixel scale.
Do not redraw the whole diagonal, recolor the blue field, move its edge, widen the band, or change any other line. Image1 should remain pixel-identical outside the small repair neighborhood. The tiny restored groove should look naturally continuous with the adjacent original groove. Preserve the clean orthographic crop. Return exactly1254x1254; no annotations, magenta, text, objects, perspective or rescaling.'''
(T/'prompt.txt').write_text(prompt,encoding='utf-8')
write(T/'input-derivation.json',{'source':{'file':str(src),'sha256':sha(src)},'cropContextBox':box,'annotationOnly':str(T/'QA-ROI-guide-not-final.png'),'maximumFeatherPixels':2,'nativeScalePreserved':True})
write(D/'24-seam-native-review-20261012.json',{'candidateAssembly':str(D/'integrated-local-v10/assembly.json'),'reviewedNativeSeams':24,'acceptedInternalSeams':False,'formalAccepted':False,'reviewEvidence':'All 12 vertical and 12 horizontal individual native crops viewed; V3-3/H2-4 viewed from v10, remaining unchanged v06 crops. No formal acceptance from resized contacts.','openIssues':['V3-3 large blue/cream notch and blue field tonal seam','H3-3 short cream/blue edge interruption','H3-4 visible roof tonal boundaries and blue pavement tonal boundary','small grout end gaps and cap offsets on V1/V2/V3 and H1','quiet irregular stone tonal islands across patches','upper gray/cream restored segment left cap kink about first20px'], 'updatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(str(T))
