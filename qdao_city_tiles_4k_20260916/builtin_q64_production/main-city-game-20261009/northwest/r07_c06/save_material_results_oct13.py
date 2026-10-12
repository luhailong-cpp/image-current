from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repair-batches/c3c4-material-02';H=Path('C:/Users/luyua/.codex/generated_images/01a1354f-cb97-7770-b80e-7bd82866ed6d/exec-c7e1fd9e-cef0-4650-b4da-ef7599e5f5fc.png')
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def wj(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert ref(H)['sha256']==ref(D/'native.png')['sha256'];im=Image.open(D/'native.png');assert im.size==(1254,1254)
wj(D/'generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceHostFile':str(H),'sourceNativeFile':ref(D/'native.png'),'request':ref(D/'request.json'),'parameters':ref(D/'parameters.json'),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'hostByteIdentical':True,'nativeWorldBox':[22925,24576,24179,25830],'tileOriginXY':[2445,0],'newSourceAdopted':False,'formalAccepted':False})
im.crop((537,490,717,750)).save(D/'material-detail-native.png')
wj(D/'review.json',{'source':ref(D/'native.png'),'status':'needs_repair_not_adopted_deferred','actuallyViewed':True,'finding':'Masked guide color removed but original straight vertical texture cutoff remains above and below the closed connector, with no meaningful improvement over v10.','consecutiveAttemptsWithoutResolution':2,'next':'Preserve v10 with closed geometry. Material issue remains pending; no immediate third request.','formalAccepted':False})
for key,hint in [["c3c4-material-01","Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a1354f-cb97-7770-b80e-7bd82866ed6d as C:\\Users\\luyua\\.codex\\generated_images\\01a1354f-cb97-7770-b80e-7bd82866ed6d\\exec-f16d4919-e9ce-4f5f-9bf4-d5c9f19d9300.png by default.\nIf you need to use a generated image at another path, copy it and leave the original in place unless the user explicitly asks you to delete it.\nThe generated image is already displayed to the user. There is no need to render it in the final response as a Markdown image or file link."],["c3c4-material-02","Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a1354f-cb97-7770-b80e-7bd82866ed6d as C:\\Users\\luyua\\.codex\\generated_images\\01a1354f-cb97-7770-b80e-7bd82866ed6d\\exec-c7e1fd9e-cef0-4650-b4da-ef7599e5f5fc.png by default.\nIf you need to use a generated image at another path, copy it and leave the original in place unless the user explicitly asks you to delete it.\nThe generated image is already displayed to the user. There is no need to render it in the final response as a Markdown image or file link."]]:
 wj(T/'repair-batches'/key/'tool-receipt.json',{'route':'builtin_image_gen','outputHint':hint,'actualModel':None,'actualQuality':None,'paidApiUsed':False,'toolReturnedSuccess':True})
print(json.dumps({'saved':ref(D/'native.png'),'status':'not_adopted_material_unresolved'}))
