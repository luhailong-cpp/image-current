from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
d=Path(__file__).parent;q=d/'qa/final-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
candidate=d/'candidate/r05_c10-4096-candidate-v2.png'
mp=candidate.with_suffix('.manifest.json');m=json.loads(mp.read_text())
reassembled=Image.new('RGB',(4096,4096))
checks=[]
for i,s in enumerate(m['sources']):
 p=Path(s['file']);g=json.loads(Path(s['generationRecord']).read_text());im=Image.open(p).convert('RGB')
 assert im.size==(1254,1254) and sha(p)==s['sha256']==g['sha256']
 assert g['nativePixelsResized']==False and g['route']=='builtin'
 assert Path(g['promptFile']).is_file() and g['receipt']['output_hint']
 for ref in g['references']:assert sha(ref['file'])==ref['sha256']
 stem=p.stem
 for ext in ['prompt.txt','request.json','receipt.json']:assert (d/'records'/f'{stem}.{ext}').is_file()
 row=int(stem[1])-1;col=int(stem[2])-1
 reassembled.paste(im.crop((115,115,1139,1139)),(col*1024,row*1024))
 checks.append({'file':str(p),'sha256':sha(p),'dimensions':[1254,1254],'referencesHashVerified':True,'requestPromptReceiptPresent':True})
assert np.array_equal(np.asarray(reassembled),np.asarray(Image.open(d/'candidate/r05_c10-4096-candidate-v1.png').convert('RGB')))
assert Image.open(candidate).size==(4096,4096) and sha(candidate)==m['sha256']
qa_sources=json.loads((q/'qa-sources.json').read_text())
assert len(qa_sources['files'])==28
for f in qa_sources['files']:assert Image.open(f).size in [(256,1024),(1024,256)]
validation={'checkedAt':now,'selectedSources':checks,'sourceCount':16,'native1254Count':16,'baseV1EqualsExact16CenterCrops':True,'finalDimensions':[4096,4096],'finalSha256':sha(candidate),'finalNativePixelsResized':False,'finalDerivedFromBaseThroughDocumentedNativeAlpha':True,'repairRecord':str(d/'repairs/post-net-connection-v1/repair-native.generation.json'),'actualModel':None,'actualQuality':None,'qaSeamFiles':28,'formalAccepted':False}
(q/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
findings={'reviewedAt':now,'reviewer':'south_native','candidate':str(candidate),'sha256':sha(candidate),'reviewScale':'native 1:1 pixels; 24 strips packed without resizing into six 1024x1024 atlases, plus four north 1024x256 strips; preview used for composition only','nativeSeamsReviewed':28,'internalSeams':24,'northSeams':4,'northNeighbor':'r04_c10 candidate v2','blockingFindings':[],'overall':'No visible object discontinuity, hard color step or ghosting in reviewed native joins. Stone road, wood, blue net, beige rope, red lantern and tassels continue across core boundaries.','repairedFindings':[{'issue':'Floating foreground net top rope detached from post coil','resolution':'Builtin local edit added short continuous beige rope from coil to first net knot without moving either object; original-size alpha applied.','status':'resolved'},{'issue':'Rectangular soft sand below shield near x2048','resolution':'Same builtin local edit restores sharp sand and pebble texture inside narrow native alpha mask.','status':'resolved'}],'notes':['Small painterly wood/sand texture variations remain natural; no blocking seam line seen.','The repair leaves first 115 north rows and east edge byte-identical to v1.','Exterior west and south neighbors and final east neighbor composite are outside this review; root performs region joins.'],'seams':[{'file':f,'status':'no_blocking_issue'} for f in qa_sources['files']],'formalAccepted':False,'formalAcceptanceReason':'Region outer neighbor images are not all checked.'}
(q/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
m['seamReview']='passed_internal24_and_north4_native_visual_review';m['qaReport']=str(q/'findings.json');m['validationReport']=str(q/'validation.json');m['formalAccepted']=False
mp.write_text(json.dumps(m,indent=2)+'\n')
pr=d/'progress.json';progress=json.loads(pr.read_text());progress.update({'updatedAt':now,'status':'candidate_complete_internal_and_north_QA_passed','candidate':str(candidate),'candidateSha256':sha(candidate),'nativeCoreCount':16,'requiredNativeCoreCount':16,'internalSeamsReviewed':24,'northSeamsReviewed':4,'blockingFindings':0,'qaReport':str(q/'findings.json'),'validationReport':str(q/'validation.json'),'formalAccepted':False,'formalAcceptanceReason':'Region outer neighbors are not all checked.','repairCount':1})
pr.write_text(json.dumps(progress,indent=2)+'\n')
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'cores':16,'qaPass':28,'formalAccepted':False}))

