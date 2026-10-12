from workflow import *
from PIL import Image
import shutil,sys
name='r09_c11_roof_color_upper_v01';src=Path(sys.argv[1]);dest=ROOT/'native'/f'{name}.png';assert not dest.exists();assert Image.open(src).size==(1254,1254);q=read(ROOT/'prompts'/f'{name}.request.json');receipt=read(ROOT/'receipts'/f'{name}.json');assert receipt['submittedArguments']['prompt']==Path(q['promptPath']).read_text(encoding='utf8');shutil.copy2(src,dest)
rec={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'width':1254,'height':1254,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'prompt':q['promptPath'],'promptSha256':q['promptSha256'],'references':q['references'],'nativeGlobalBox':q['nativeGlobalBox'],'originRelativeR09c11':q['originRelativeR09c11'],'evidence':{'toolReceipt':str(ROOT/'receipts'/f'{name}.json')},'resizedAfterGeneration':False,'status':'native_received_pending_assembly_QA'}
write(Path(str(dest)+'.generation.json'),rec)
p=ROOT/'continuation-round-20261011.json';d=read(p);d.update({'status':'new_builtin_output_verified_after_resume','firstActualOutput':{'file':str(dest),'sha256':sha(dest),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativeSize':[1254,1254],'recordedAt':now()},'nextStep':'Inspect repaired whole blue tiles, prepare overlapping lower native using this real anchor; continue adjacent missing cores.'});write(p,d);print(d['firstActualOutput'])

