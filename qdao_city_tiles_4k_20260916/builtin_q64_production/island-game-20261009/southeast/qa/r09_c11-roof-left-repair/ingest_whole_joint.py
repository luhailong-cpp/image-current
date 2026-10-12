from pathlib import Path
from PIL import Image
import os,json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid='r09_c11_roof_whole_joint_v01';req=json.loads((R/'prompts'/f'{pid}.request.json').read_text());source=Path(r'C:\Users\luyua\.codex\generated_images\01a1216e-02a9-7dc3-a3ef-c1e18e776463\exec-33313fb9-409d-48b3-964d-b119bcc46d94.png');out=R/'native'/f'{pid}.png'
assert source.is_file() and not out.exists();shutil.copy2(source,out);assert sh(source)==sh(out);im=Image.open(out);assert im.size==(1254,1254)
old=json.loads((R/'native/r09_c11_roof_color_lower_v01.png.generation.json').read_text())
receipt=R/'receipts'/f'{pid}.json'
record={'file':str(out),'sha256':sh(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(source),'sourceOutputSha256':sh(source),'configSnapshotTargetOnly':old['configSnapshotTargetOnly'],'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'nativeGlobalBox':req['nativeGlobalBox'],'originRelativeR09c11':req['originRelativeR09c11'],'request':str(R/'prompts'/f'{pid}.request.json'),'requestSha256':sh(R/'prompts'/f'{pid}.request.json'),'evidence':{'toolReceipt':str(receipt),'toolReceiptSha256':sh(receipt)},'resizedAfterGeneration':False,'status':'native_received_pending_geometry_QA'}
Path(str(out)+'.generation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sh(out),'nativeSize':list(im.size),'receipt':str(receipt)},indent=2))
