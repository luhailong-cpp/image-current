from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repairs/roof-local-details-20261013-v1';P=D/'composed-A-B-C';J=D/'D-right-rib-connection';J.mkdir(exist_ok=False)
def info(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
C=P/'candidate-4096.png';X=P/'context-4326.png';crop=[1550,1450,2804,2704];box=[2180,1610,2780,2420];target=J/'edit-target-native-1254.png'
Image.open(C).convert('RGB').crop(crop).save(target)
prompt='Use case: precise-object-edit. Edit this existing native 1254 x 1254 Taoist chibi game map roof detail; preserve the exact crop and scale. The thin gold rib on the LEFT already connects correctly from the central peak above to the lower curved band. KEEP that left rib unchanged. Fix ONLY the RIGHT thicker gold diagonal rib: it currently stops under an inappropriate blue semicircular tile cap near local (950,710), disconnected from the main roof ridge above. Remove that small blue cap and continue the same right gold rib upward-left to join the underside of the central gold peak at local (738,238), making a continuous symmetric structural gold rib from peak to the existing bottom-right gold end. Preserve its lower visible part, width transition and shading. Preserve the entire surrounding roof, both large upper gold curves, existing gold ridge collars, blue tile spacing, left rib, water and shadows. Do not add another bar, ornament, tier, cap or clasp. Output only the same opaque native 1254 square; no reframing, whole-scene repainting, labels or blur.'
req={'prompt':prompt,'referenced_image_paths':[str(target)],'transparent_background':False};write(J/'request.json',req);(J/'prompt.txt').write_text(prompt,encoding='utf-8')
write(J/'preparation.json',{'tile':T.name,'id':J.name,'sourceCandidate':info(C),'sourceContext':info(X),'sourceAssembly':info(P/'composition.json'),'target':info(target),'cropBox':crop,'pasteBox':box,'request':info(J/'request.json'),'actualModel':None,'actualQuality':None,'formalAccepted':False})
print(json.dumps({'target':str(target),'request':str(J/'request.json')}))
