from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix15_centered';D.mkdir(exist_ok=False)
source=B/'fix12_centered/centered-native-context.png';target=D/'centered-native-context.png';target.write_bytes(source.read_bytes())
prompt='''Use case: precise-object-edit. Repair only the stone rail near the horizontal stitch at y512 in this image. The lower part, from y512 to the bottom, is the CORRECT original rail and must remain unchanged. Its exact cross-section is the target. The upper part's left edge, gray bevel and left inset groove are too far LEFT. Correct those three upper lines independently so they meet the existing lower lines exactly: move the gray left bevel and its bright ridge about 12 pixels to the RIGHT near y512; move the upper left inner groove about 6 pixels to the RIGHT near y512. Taper these small adjustments gradually upward into the existing top. Match the cooler, darker gray value of the lower left bevel, not the lighter warm gray above. Keep the right outside edge and existing right groove at their current positions. There must be no sideways step, jagged edge or color band at y512. This is a small structural alignment repair, not a new straightened railing. Preserve the established slant, widths, wall, coping and stairs. Do not alter the lower correct rail to match the wrong upper one. Same 1254x1254 opaque native framing, no new objects or ornaments.'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
params={'prompt':prompt,'referenced_image_paths':[str(target)],'transparent_background':False}
rec={'worldBox':[12173,15757,13427,17011],'formalSeamLocalY':627,'sourceJoinLocalY':512,'width':1254,'height':1254,'baseFile':str(source),'baseSha256':sha(source),'baseProvenance':str(B/'fix12_centered/preparation.json'),'guideFile':str(target),'guideSha256':sha(target),'operation':'Byte-identical native contextual guide, targeted geometry correction requested only via imagegen','actualModel':None,'actualQuality':None}
for name,data in [('parameters.json',params),('preparation.json',rec)]: (D/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(str(D))
