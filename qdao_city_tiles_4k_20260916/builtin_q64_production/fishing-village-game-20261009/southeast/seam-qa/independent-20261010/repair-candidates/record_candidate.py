import sys,json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
stem=sys.argv[1] if len(sys.argv)>1 else 'east-deck-joint-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((HERE/(stem+'.request.json')).read_text())
if 'referenced_image_paths' not in req:
 req['referenced_image_paths']=req['toolInput']['referenced_image_paths']
receipt=HERE/(stem+'.receipt.json');image=HERE/(stem+'.png');prompt=HERE/(stem+'.prompt.txt')
record={'file':str(image),'sha256':sha(image),'createdAtUtc':datetime.now(timezone.utc).isoformat(),'actualNativeDimensions':list(Image.open(image).size),'globalBox':req['globalBox'],'configTarget':req['configTarget'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'evidenceStatus':'builtin host managed; model and quality not disclosed','tool':'image_gen__imagegen','route':'builtin','prompt':{'file':str(prompt),'sha256':sha(prompt)},'request':{'file':str(HERE/(stem+'.request.json')),'sha256':sha(HERE/(stem+'.request.json'))},'receipt':{'file':str(receipt),'sha256':sha(receipt)},'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'selected':False,'formalAccepted':False,'resamplingApplied':False,'initialVisualReview':{'interior':'continuous planks and lighting; original x568 seam removed','boundaryWarning':'right-edge plank endpoints moved relative to original native crop. Do not adopt full rectangular crop without perimeter checking/repair. Left anchors and stone/rail object silhouettes largely preserved.'}}
record['initialVisualReview']={'status':'pending_native_candidate_and_adoption_boundary_review'}
(HERE/(stem+'.png.generation.json')).write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'file':str(image),'dimensions':record['actualNativeDimensions'],'sha256':record['sha256']}))
