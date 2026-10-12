from workflow import *
from PIL import Image
from datetime import datetime,timezone
import shutil
name='r12_c12_deck_whole_joint_v01'
src=Path('C:/Users/luyua/.codex/generated_images/01a1216d-8b5f-7823-bf97-16e5128906cc/exec-f3197411-4262-4bfa-9a4c-0dfa8f557de8.png')
out=ROOT/'native'/f'{name}.png'
if out.exists():assert sha(out)==sha(src)
else:shutil.copy2(src,out)
req=read(ROOT/'prompts'/f'{name}.request.json');pf=Path(req['promptPath'])
with Image.open(out) as im:size=list(im.size);mode=im.mode
assert size==[1254,1254]
receipt=ROOT/'prompts'/f'{name}.recovery-receipt.json'
write(receipt,{'recoveredAtUtc':now(),'sourceOutputPath':str(src),'sha256':sha(src),'sourceFileModifiedUtc':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'originalTool':'image_gen.imagegen','originalExecCell':'117','originalRequestPath':str(ROOT/'prompts'/f'{name}.request.json'),'originalToolResponseUnavailable':True,'reason':'Task interruption cleared functions store and exec cell; one completed output found in this chat output directory after the recorded request. Image content matches complete deck junction and requested butt joints. This is recovered evidence, not a reconstructed tool response.','rootVisualInspection':'Whole native output observed; central image cut removed with complete wooden boards and short butt joints. Outer source joins have NOT been verified.','savedWithoutNewGeneration':True})
info={'file':str(out),'sha256':sha(out),'width':size[0],'height':size[1],'mode':mode,'recoveredAtUtc':now(),'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'prompt':str(pf),'promptSha256':sha(pf),'references':req['references'],'evidence':{'recoveryReceipt':str(receipt),'originalToolResponseUnavailable':True},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'tile':'r12_c12','tileRelativeOrigin':req['tileRelativeOrigin'],'resizedAfterGeneration':False,'status':'recovered_native_pending_outer_join_review_not_adopted'}
write(Path(str(out)+'.generation.json'),info)
print(json.dumps({'saved':str(out),'sha256':sha(out),'size':size,'activeRootImageRequests':0}))
