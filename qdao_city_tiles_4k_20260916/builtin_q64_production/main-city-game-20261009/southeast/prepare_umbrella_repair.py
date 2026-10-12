from pathlib import Path
import json,hashlib,datetime
from PIL import Image
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs';R.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
candidate=T/'candidate'/'r13_c13-4k-candidate.png'
target=R/'umbrella-left-v1-target.png';box=[2450,320,3704,1574]
im=Image.open(candidate);im.crop(box).save(target)
contract=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
refs=[contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference'],str(target)]
prompt="""Use case: precise-object-edit, native geometry repair of an existing game-map crop.
Images1/2/3 are ONLY approved layout, close-up material and style references. Image4, THE LAST IMAGE, is the only edit target. Return exactly1254x1254 pixels, opaque. Preserve the exact framing, magnification, object placements, edge pixels and rendering style.
Repair ONLY the broken bamboo ribs on the cream/red parasol in the last image. This is one single parasol seen from above. Its existing one brass/bamboo crown is near x1115 y660 inside this crop; keep that crown in exactly that position. Each bamboo rib must be a continuous straight tapered spoke running from that one crown toward its existing canopy-rim endpoint. Replace the disconnected, truncated and sharply zigzagging ribs across the left half of the cream canopy with coherent straight spokes. Keep only the existing intended radial rib count; no extra crown, no additional parasol, no floating loose sticks. Repair the red/cream canopy's broken decorative curves so every band describes a continuous smooth concentric ring around the same crown.
Keep the parasol's outer silhouette, the red rim, pavement, nearby wooden stools, feet and all small red paper scraps exactly where they already are. Preserve the outermost64 pixels of the crop, especially stone grout at the edges. Do not pan, rotate, enlarge, shrink, reframe or fit a whole parasol inside the crop. Do not blur, smooth away texture, make a new scene, add objects or change lighting. Retain the current bright rounded hand-painted Taoist chibi game style and native detail. No text, labels, borders or watermark."""
args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
(R/'umbrella-left-v1.prompt.txt').write_text(prompt,encoding='utf-8')
(R/'umbrella-left-v1.request.json').write_text(json.dumps(args,ensure_ascii=False,indent=2),encoding='utf-8')
meta={'id':'umbrella-left-v1','operation':'unscaled native crop for image_gen geometry repair','source':str(candidate),'sourceSha256':sha(candidate),'cropBoxIn4096':box,'width':1254,'height':1254,'resized':False,'target':str(target),'targetSha256':sha(target),'references':[{'path':p,'sha256':sha(p),'dimensions':list(Image.open(p).size),'role':r} for p,r in zip(refs,['approved layout','approved material','approved primary style','only edit target'])]}
(R/'umbrella-left-v1.target.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
progress=json.loads((B/'progress.json').read_text(encoding='utf-8-sig'))
progress.update(status='candidate_requires_geometry_repair',updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),generatedNativeCount=22,activeNativePatchCount=16,complete4kCandidateCount=1,formalAcceptedCount=0,internalQaPassed=False,currentPatch=None,nextStep='Repair parasol ribs and discontinuous ground geometry on native 1254 crops; then review all seam bands and outer edges.',candidateFile=str(candidate),candidateSha256=sha(candidate))
(B/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'target':str(target),'cropBox':box,'candidateSha256':sha(candidate)}))

