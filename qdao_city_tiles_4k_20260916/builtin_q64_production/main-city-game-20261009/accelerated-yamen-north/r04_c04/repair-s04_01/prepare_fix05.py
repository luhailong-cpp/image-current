from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix05';D.mkdir(parents=True,exist_ok=True)
source=B/'fix04/generated.png';south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
im=Image.open(source).convert('RGB');im.paste(Image.open(south).crop((0,0,1254,230)),(0,1024))
target=D/'exact-south-context.png'
if target.exists():raise FileExistsError(target)
im.save(target)
prompt='''Use case: precise-object-edit. Inpaint only the wrongly aligned long pale stone railing ABOVE the horizontal splice near the bottom of this image. The correct railing is the one BELOW that splice. Continue that narrower lower railing straight UPWARD through the full height of the image. Repair all its long grooves, bevels and its right silhouette as one coherent straight object. The upper railing currently has its right edge too far right; move that upper edge LEFT by about32pixels to meet the lower edge exactly, expanding the adjacent stair area. Do not average the two widths. The lower railing and every pixel in the bottom230rows are fixed reference and must stay exactly where they are.
The target contains actual neighboring native pixels in those bottom230rows, not an arbitrary overlay: the finished artwork must join them continuously. Do not move, rescale or repaint that bottom reference. Keep the image edges, camera, green panel fragment and large left pedestal faces unchanged. Maintain one long uncapped vertical inset on the railing with no new decorative panels. Match the right stair lines to the fixed reference at the splice. Same softly painted pale stone in bright daylight. No text, objects, figures, frame or watermark. Output the edited image at its original1254x1254 size, opaque.'''
p={'prompt':prompt,'referenced_image_paths':[str(target)],'transparent_background':False}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
(D/'parameters.json').write_text(json.dumps(p,indent=2),encoding='utf-8');(D/'prompt.txt').write_text(prompt,encoding='utf-8')
(D/'preparation.json').write_text(json.dumps({'source':str(source),'sourceSha256':sha(source),'actualSouthSource':str(south),'actualSouthSha256':sha(south),
'southSourceCrop':[0,0,1254,230],'targetPaste':[0,1024,1254,1254],'submittedTarget':str(target),'submittedTargetSha256':sha(target),'sourceResampled':False,
'guideGameArt':False,'actualModel':None,'actualQuality':None},indent=2),encoding='utf-8')
