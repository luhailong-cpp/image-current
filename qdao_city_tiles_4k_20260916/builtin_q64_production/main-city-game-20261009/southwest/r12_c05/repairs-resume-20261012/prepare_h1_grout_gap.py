from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012');T=D/'H1-4-grout-gap-v01';T.mkdir(exist_ok=True)
src=D/'integrated-local-v11/r12_c05.candidate.context.png';box=[2655,606,3909,1860];im=Image.open(src).convert('RGB').crop(box);im.save(T/'input.png')
qa=im.copy();dr=ImageDraw.Draw(qa);dr.rectangle((590,578,690,676),outline=(255,0,255),width=3);qa.save(T/'QA-ROI-guide-not-final.png')
prompt='''Use case: precise-object-edit. Repair one tiny grout-line gap in the native1254x1254 edit target, image1. Image2 approved city layout, image3 natural stone detail, image4 approved Daoist style, image5 marks only the small repair neighborhood in magenta.
Inside the small rectangle x590..690 y578..676, the dark diagonal descending paving joint has a short disconnected cap just before it reaches an X intersection. Reconnect that tiny gap and align the cap flush with both immediately adjacent line segments. Preserve the X intersection and all original joint endpoints, straight slopes, groove width, stone bevel and native scale. Keep the original surrounding quiet cream/gray stone, blue material, all other lines, highlights and texture exactly as image1. Only the small missing cap/gap can change, not the whole stone slabs or whole diagonal. Use the original groove shade and line weight, avoiding a new darker stretch.
Return exactly1254x1254 with only the tiny gap repaired. No magenta/annotation, red, text, added objects, new topology, shifted geometry or scaling.'''
(T/'prompt.txt').write_text(prompt,encoding='utf-8')
(T/'input-derivation.json').write_text(json.dumps({'source':{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()},'cropContextBox':box,'annotationOnly':str(T/'QA-ROI-guide-not-final.png'),'nativeScalePreserved':True,'maximumFeatherPixels':2},ensure_ascii=False,indent=2),encoding='utf-8')
print(str(T))
