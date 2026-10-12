from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil,argparse
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=argparse.ArgumentParser();a.add_argument('direction');a.add_argument('slot');a.add_argument('returned');args=a.parse_args()
folder=R/'run-axis-revision-20261004'/args.direction/args.slot;folder.mkdir(parents=True,exist_ok=True)
req=json.loads((folder/'request.json').read_text(encoding='utf-8'))
src=Path(args.returned);dest=folder/'native.png';shutil.copy2(src,dest);im=Image.open(dest)
references=[]
for i,path in enumerate(req['referenced_image_paths']):
    p=Path(path);rec=Path(str(p)+'.generation.json');ref={'file':str(p),'sha256':sha(p),'purpose':'edit target' if i==0 else 'supporting reference'}
    if rec.exists():
        textcopy=folder/f'input-{i+1}-generation.json';shutil.copy2(rec,textcopy);ref['inputRecordSnapshot']=textcopy.relative_to(R).as_posix();ref['recordSHA256']=sha(textcopy)
    references.append(ref)
receipt={'tool':'image_gen.imagegen','returnedFile':str(src),'outputCopiedTo':dest.relative_to(R).as_posix(),'recordedAt':datetime.now(timezone.utc).isoformat(),'actualModel':None,'actualQuality':None}
write(folder/'receipt.json',receipt)
meta={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'generatedAt':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'returned file mtime after tool completion','width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':req['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露可核实型号与质量，无参数选择器。','evidence':{'receipt':(folder/'receipt.json').relative_to(R).as_posix(),'request':(folder/'request.json').relative_to(R).as_posix()},'prompt':(folder/'prompt.txt').relative_to(R).as_posix(),'references':references,'outputScalePolicy':'full-canvas-to1024-no-translation','status':'candidate-needs-current-contact-review'}
write(Path(str(dest)+'.generation.json'),meta)
print(json.dumps({'file':str(dest),'sha256':sha(dest),'size':im.size,'mode':im.mode}))
