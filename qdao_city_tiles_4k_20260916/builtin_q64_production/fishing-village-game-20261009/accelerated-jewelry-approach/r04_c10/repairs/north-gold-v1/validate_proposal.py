from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
d=Path(__file__).parent;root=d.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((d/'repair.request.json').read_text());receipt=json.loads((d/'repair.receipt.json').read_text());prop=json.loads((d/'proposal.json').read_text())
g={'file':str(d/'repair-native.png'),'sha256':sha(d/'repair-native.png'),'nativeDimensions':list(Image.open(d/'repair-native.png').size),'format':'PNG','nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'No verified model/quality metadata exposed by builtin tool','prompt':req['prompt'],'promptFile':str(d/'repair.prompt.txt'),'requestFile':str(d/'repair.request.json'),'references':[{'file':req['referenced_image_paths'][0],'sha256':sha(req['referenced_image_paths'][0]),'role':req['referenceRoles'][0]}],'receipt':receipt,'proposal':str(d/'proposal.json'),'status':'repair_ready_for_root_integration_only'}
(d/'repair-native.generation.json').write_text(json.dumps(g,indent=2)+'\n')
before=np.asarray(Image.open(d/'context-before-native.png').convert('RGB'))
after=np.asarray(Image.open(d/'context-after-proposal-native.png').convert('RGB'));alpha=np.asarray(Image.open(d/'contribution-mask-1254.png'))
assert np.array_equal(before[alpha==0],after[alpha==0])
mask_nonzero=int((alpha>0).sum())
v2=np.asarray(Image.open(root/'r03_c10/candidate/r03_c10-4096-candidate-v2.png').crop((0,3979,280,4096)))
v3=np.asarray(Image.open(root/'r03_c10/candidate/r03_c10-4096-candidate-v3.png').crop((0,3979,280,4096)))
qa={'reviewedAt':'2026-10-10','nativeDimensions':[1254,1254],'pixelScale':'1:1','goldCurlSharpness':'Blur removed; same curved gold silhouette with crisp groove and paint facets continues over shared seam','maskBoundaries':'No apparent hard transition in inspected before/after native 400x260 crop and full1254 context','nonzeroAlphaPixelCount':mask_nonzero,'outsideMaskIdenticalToBefore':True,'northV2V3ChangedPixelCountWithinProposedRoi':int(np.any(v2!=v3,axis=2).sum()),'nativePixelsResized':False,'appliedToCandidates':False,'readyForRootIntegration':True,'formalAccepted':False}
(d/'qa-review.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps(qa))

