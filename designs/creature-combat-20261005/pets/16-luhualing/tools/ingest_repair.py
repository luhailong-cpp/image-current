from pathlib import Path
import json,hashlib,sys
from PIL import Image
root=Path(__file__).resolve().parents[1]
action,direction,number=sys.argv[1:4]
prefix=root/f'records/{action}/{direction}/{number}'
record=Path(str(prefix)+'.generation.json')
old=Path(str(prefix)+'.rejected-01.generation.json')
receipt_path=root/sys.argv[4] if len(sys.argv)>4 else Path(str(prefix)+'.receipt.json')
receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
meta=json.loads(old.read_text(encoding='utf-8-sig'))
native=root/f'.work/{action}/{direction}/{number}.png'
with Image.open(native) as im:
    meta.update({'file':f'runtime/{action}/{direction}/{number}.png','sourceFile':native.relative_to(root).as_posix(),'sourceSha256':hashlib.sha256(native.read_bytes()).hexdigest(),'generatedAt':receipt['returnedAt'],'startedAt':receipt['startedAt'],'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'submittedParameters':receipt['request'],'references':receipt['references'],'prompt':receipt['promptPath'],'evidence':{'receipt':receipt_path.relative_to(root).as_posix()},'editTarget':receipt['editTarget'],'visualStatus':'repair_pending_review','visualReview':None,'exportStatus':'pending root unified export'})
    meta.pop('sha256',None)
record.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Saved corrected {action}/{direction}/{number} provenance.')
