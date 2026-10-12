from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
now=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 p=Path(p);assert not p.exists();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
q=T/'qa/full-native-finish-20261013-v2';m=json.loads((q/'manifest.json').read_text())
bad=['p21--p31.png','p31--p32.png','cross-r2-c1.png','cross-r3-c1.png']
issues={'p21--p31.png':'Paving grain and diagonal joint changes abruptly at horizontal core boundary, improved v5 but still unaccepted','p31--p32.png':'Sharp vertical texture and joint endpoint discontinuity; needs native repair, not RGB concealment','cross-r2-c1.png':'Lower-left p31 stone grain inconsistent with other quadrants','cross-r3-c1.png':'p31 right material boundary and red attachment transition remain visible','p21--p22.png':'Paving sharpness/light intensity changes at seam; independent p22 native material repair requested'}
items=[]
for e in m['evidence']:
 p=Path(e['file']);assert sha(p)==e['sha256']
 items.append({'file':str(p),'sha256':e['sha256'],'viewedAtNativeScale':True,'geometryStatus':'pending_native_repair' if p.name in bad else 'passed_visual','materialStatus':'pending_native_repair' if p.name in issues else 'pending_final_color_review','note':issues.get(p.name,'Major object and grout contours continuous; final low-frequency color comparison not yet performed')})
write(q/'native-visual-review.json',{'tile':'r08_c09','createdAt':now,'all33ViewedAtNativeScale':len(items)==33,'evidence':items,'selectionSha256':sha(T/'selected-patches.json'),'internalReady':False,'formalAccepted':False,'materialPending':True,'reviewer':'/root/north_c09_finish_20261013','next':'Independent p22 material repair; p31 needs coordinated native joint repair after v6 geometry rejection'})
write(T/'p31-v6-rejection.json',{'createdAt':now,'source':str(T/'native/p31-v6.png'),'sha256':sha(T/'native/p31-v6.png'),'selected':False,'reason':'Copied adjacent p32 paving arrangement instead of preserving top/right/bottom seam endpoints. Foreground acceptable but paving geometry incompatible. Keep v5 selected and preserve v6 raw/provenance.','bestExisting':'native/p31-v5.png','furtherBlindFullPatchRetriesDeferred':True})
s=T/'layout-only/p22-true-core-conditioned-finish-20261013-v3.png'
prompt="""Use case: precise-object-edit. Precisely repair the bluegray PAVING MATERIAL only in this exact1254x1254 game-art patch. Preserve all stone slab shapes and grout positions and red-gold tassel pixel footprints. The stone currently has a rectangular center at x115..1138,y115..1138 whose material and light differ visibly from the surrounding115pixel frame. Remove every rectangular edge in texture and brightness by repainting the interior stone surface in the SAME fine crisp painterly mottling and soft DAYLIGHT as the surrounding native frame. Keep all outer frame stone endpoints exactly. Fix tiny grout steps where interior stone joints meet that frame, without changing the slab layout. Do not blur or feather the artwork, do not add a shadow to hide the join. Natural flat stone surface with consistent brush density across each boundary.
The exact red-gold tassel at x300..640 from top through y780 remains identical in size and position. The tiny clipped fish belly along top edge remains clipped. No new objects, no poles or lanterns or buildings, no scale shift, no reframe. Keep same orthographic camera and daylight Daoist Q hand-painted style. Exact1254x1254 RGB output; core115..1138. No transparent pixels, text, watermark, or border."""
d={'prompt':prompt,'referenced_image_paths':[str(s)],'transparent_background':False,'route':'builtin','tool':'image_gen__imagegen','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'createdAt':now,'referenceEvidence':[{'path':str(s),'sha256':sha(s),'role':'Exact target with all8 true-core neighboring frame pieces; geometry fixed, paving material repair'}]}
write(T/'p22-v3.request.json',d);p=T/'p22-v3.prompt.txt';assert not p.exists();p.write_text(prompt,encoding='utf-8')

