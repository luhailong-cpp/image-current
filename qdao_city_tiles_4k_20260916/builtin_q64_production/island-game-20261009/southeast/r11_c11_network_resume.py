from workflow import ROOT,read,write,sha,now
from pathlib import Path
errors={'21':'application network permission was revoked','33':'http 401 Unauthorized: Missing bearer or basic authentication in header','44':'http 401 Unauthorized: Missing bearer or basic authentication in header'}
for rc,msg in errors.items():
 f=ROOT/'receipts'/f'r11_c11_p{rc}_v01-attempt-1-error.json'
 if not f.exists():write(f,{'tool':'image_gen.imagegen','recordedAt':now(),'status':'failed_no_output','error':msg,'prompt':str(ROOT/'prompts'/f'r11_c11_p{rc}_v01.prompt.txt'),'request':str(ROOT/'prompts'/f'r11_c11_p{rc}_v01.request.json')})
files=[{'file':str(f),'sha256':sha(f),'hasGenerationRecord':Path(str(f)+'.generation.json').exists()} for f in sorted((ROOT/'native').glob('r11_c11_*.png'))]
p=read(ROOT/'progress-r11_c11.json');p.update({'generatedNativeCount':len(files),'selectedCoordinateCount':8,'status':'restored_authorization_pending_first_output','nativeInventory':files,'networkInterruption':errors,'resumeAuthorization':'parent relayed explicit user permission restoration','updatedAt':now(),'nextStep':'Retry failed p21 once through same builtin imagegen after checking no saved output; stop retrying if network fails again.'});write(ROOT/'progress-r11_c11.json',p)
print({'natives':len(files),'failedOutputsExist':{rc:(ROOT/'native'/f'r11_c11_p{rc}_v01.png').exists() for rc in errors}})
