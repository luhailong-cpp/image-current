from pathlib import Path
from PIL import Image
import json, hashlib, datetime
D=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((D/'request.json').read_text(encoding='utf-8-sig')); receipt=json.loads((D/'receipt.json').read_text(encoding='utf-8-sig'))
p=D/'native-result.png'; im=Image.open(p)
record={'file':str(p),'sha256':sha(p),'nativeDimensions':list(im.size),'format':im.format,'nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin tool receipt exposes no verified model or quality metadata.','sourcePath':receipt['originalFile'],'sourceSha256':sha(receipt['originalFile']),'prompt':req['prompt'],'promptFile':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'references':[{'file':f,'sha256':sha(f),'role':req['referenceRoles'][i]} for i,f in enumerate(req['referenced_image_paths'])],'requestFile':str(D/'request.json'),'requestSha256':sha(D/'request.json'),'receiptFile':str(D/'receipt.json'),'receiptSha256':sha(D/'receipt.json'),'requestedAt':receipt['requestedAt'],'receivedAt':receipt['receivedAt'],'status':'native_repair_generated_local_transition_needs_followup','formalAccepted':False}
(D/'native-result.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=D/'qa';q.mkdir(exist_ok=True)
box=(96,128,576,400)
for n in ['target-native','native-result']: Image.open(D/(n+'.png')).crop(box).save(q/(n+'-y230-native.png'))
findings={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'nativePixelsResized':False,'overall':'Repair correctly puts hanging net in front of timber, replacing the erroneous upward bare post.','unresolvedDefect':{'nativeY':230,'nativeXApprox':[120,420],'type':'true horizontal geometry discontinuity','description':'Across the original context-strip boundary, several grey mesh strands and vertical golden cord shift slightly; a ruler-straight horizontal change is visible through the wood/net background.'},'alphaAssessment':'Ordinary native alpha compositing between target and repair cannot remove this geometrical jump: both sources contain the same inherited upper230 edge while the target below it is bare timber. A broad feather would duplicate net strands or reveal bare wood. Do not mark an alpha proposal accepted.','recommendation':'One additional builtin local edit on the already improved repair, focused x100..480,y175..300, retaining exact original top115 and all wood/net below approximately y520. Inspect before alpha composition.','selectionChanged':False,'candidateChanged':False,'additionalBuiltinCallMade':False}
(q/'findings.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'record':str(D/'native-result.generation.json'),'qa':str(q/'findings.json'),'size':im.size}))
