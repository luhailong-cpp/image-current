from pathlib import Path
import hashlib,json,sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]); direction=sys.argv[2]; number=int(sys.argv[3]); stem=f'hit-{direction}-{number:02d}'
dest=ROOT/'runtime'/'hit'/direction/f'{number:02d}.png'; dest.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(source); native={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode}
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
im=im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS); im.save(dest)
receipt=json.loads((ROOT/'receipts'/f'{stem}.json').read_text(encoding='utf-8'))
refs=receipt['submittedParameters']['referenced_image_paths']
record={'file':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'generatedAt':receipt['returnedAt'],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':receipt['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号或质量，无可核实元数据。','native':native,'width':1024,'height':1024,'format':'PNG','mode':'RGBA','evidence':f'receipts/{stem}.json','prompt':f'prompts/{stem}.txt','references':[{'path':r,'purpose':['original E identity','original W identity','primary approved painterly style','same direction previous frame continuity'][min(i,3)]} for i,r in enumerate(refs)],'derivedFrom':{'path':str(source),'sha256':source_sha,'native':native},'operation':'Whole native canvas resized uniformly to 1024x1024 with Lanczos. No crop, per-frame registration, mirror, shift or interpolation.','visualStatus':'generated; pending sequence review'}
dest.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'native':native,'alpha':im.getchannel('A').getextrema(),'bbox':im.getbbox(),'sha256':record['sha256']}))
