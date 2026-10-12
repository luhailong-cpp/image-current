from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
b=Path(r'undefined');d=b/'r05_c10/repairs/east-stone-halo-v1';d.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p1=b/'r05_c10/candidate/r05_c10-4096-candidate-v2.png'
p2=b/'r05_c11/candidate/r05_c11-4096-candidate-v2.png'
canvas=Image.new('RGB',(8192,4096));canvas.paste(Image.open(p1),(0,0));canvas.paste(Image.open(p2),(4096,0))
box=[3354,950,4608,2204];im=canvas.crop(box);im.save(d/'target-native.png')
im=im.convert('RGBA');im.paste((0,0,0,0),(607,30,647,870));im.save(d/'target-inpaint-native.png')
der={'tile':'r05_c10','tileLocalBox':box,'globalPixelBox':[36864+box[0],16384+box[1],36864+box[2],16384+box[3]],'sources':[{'file':str(p),'sha256':sha(p)} for p in [p1,p2]],'operation':'Two native candidates pasted1:1; native1254 crop; only missing strip alpha knockout for builtin inpainting','transparentHoleNativeBox':[607,30,647,870],'nativePixelsResized':False}
(d/'target-derivation.json').write_text(json.dumps(der,indent=2)+'\n',encoding='utf-8')
checkpoint={'updatedAt':datetime.now(timezone.utc).isoformat(),'status':'all_six_cores_complete_final_seam_repair_and_region_QA_remaining','assignedCoordinates':['r03_c10','r03_c11','r04_c10','r04_c11','r05_c10','r05_c11'],'selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'completeCandidateCount':6,'formalAcceptedCount':0,'remainingCoreCoordinates':[],'remainingWork':['c10east internal stone halo localized repair','c11sand repair final adoption','six region native seam review and final delivery'], 'newlySavedLocalArtifact':str(d/'target-native.png'),'newlySavedLocalArtifactSha256':sha(d/'target-native.png'),'interruptedBuiltinOutputsChecked':'All successful root results through ground-halo-v6 saved; previous audit verifies45new raw receipts and cache-source copies. No successful root result left unsaved.','currentNetworkFailure':None,'historicalErrorNotCurrent':'09:28Z denial predates multiple later builtin successes; not treated as current failure','gitOperationsByThisTask':False}
(b/'continuation-status-20261011-evening.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(d/'target-inpaint-native.png'))

