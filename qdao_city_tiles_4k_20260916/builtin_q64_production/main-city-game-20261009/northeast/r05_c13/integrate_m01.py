from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=T/'native/m01.png'
if not raw.exists():shutil.copy2('C:/Users/luyua/.codex/generated_images/01a12075-ff24-76d0-ac68-97861111ddb0/exec-ac931a0b-8aed-46a2-8262-b9427521e29a.png',raw)
repair=Image.open(raw).convert('RGB')
assert repair.size==(1254,1254)
baseline=T/'qa/core-baseline/4b1ca7ac3c334e15ab79/r05_c13-core-baseline.candidate.png'
original=Image.open(baseline).convert('RGB')
target=T/'qa/repairs/m01-input.png'
inp=json.loads(Path(str(target)+'.generation.json').read_text(encoding='utf-8'))
inp['derivedFrom']={'file':str(baseline),'sha256':sha(baseline)}
save(str(target)+'.generation.json',inp)
req=json.loads((T/'prompts/m01.request.json').read_text(encoding='utf-8'))
cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
record={'file':str(raw),'sha256':sha(raw),'generatedAt':datetime.now(timezone.utc).isoformat(),'nativeSize':[1254,1254],'width':1254,'height':1254,'format':'PNG','tool':'image_gen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed image_gen returned image_url and output_hint only.','prompt':str(T/'prompts/m01.prompt.txt'),'request':str(T/'prompts/m01.request.json'),'evidence':str(T/'receipts/m01.receipt.json'),'references':[{'file':p,'sha256':sha(p),'role':role} for p,role in zip(req['referenced_image_paths'],req['referenceRoles'])],'tileCropBox':[680,600,1934,1854],'resized':False,'status':'native texture-seam repair; geometry preserved'}
save(str(raw)+'.generation.json',record)
mask=Image.new('L',(1254,1254),0)
pix=mask.load()
# The structure is already continuous; this is a bounded texture/color transition only.
# Full AI repair covers local y400..470, with gradual taper to unchanged stone.
for y in range(280,631):
    wy=min(1.0,(y-280)/120,(630-y)/160)
    for x in range(1254):
        wx=min(1.0,x/24,(1253-x)/24)
        pix[x,y]=round(255*max(0,min(wx,wy)))
maskpath=T/'qa/repairs/m01-integration-mask.png';mask.save(maskpath)
out=original.copy();out.paste(repair,(680,600),mask)
dest=T/'candidates/r05_c13.candidate.png';out.save(dest)
operation={'type':'AI repainted native local patch, integer paste with bounded texture-only transition','baseline':str(baseline),'baselineSha256':sha(baseline),'repair':str(raw),'repairSha256':sha(raw),'pasteOrigin':[680,600],'mask':str(maskpath),'maskSha256':sha(maskpath),'maskNonzeroTileBox':[681,881,1933,1230],'sourceResampling':False,'geometryWarp':False,'blurUsed':False,'maskReason':'Only material/color discontinuity M01; no misaligned geometry is concealed.'}
save(T/'qa/repairs/m01-integration.json',operation)
save(str(dest)+'.generation.json',{'file':str(dest),'sha256':sha(dest),'width':4096,'height':4096,'format':'PNG','assetRole':'complete4kCandidate; not formal accepted','derivedFrom':[{'file':str(baseline),'sha256':sha(baseline),'assembly':str(baseline.parent/'assembly.json')},{'file':str(raw),'sha256':sha(raw),'generationRecord':str(raw)+'.generation.json'}],'operation':operation,'actualModel':None,'actualQuality':None,'unverifiedReason':'Per-source built-in tool evidence does not disclose actual model/quality.','formalAccepted':False,'clientMappingValidated':False,'capacity5000Validated':False})
original.crop((600,820,2000,1280)).save(T/'qa/repairs/m01-before-100pct.png')
out.crop((600,820,2000,1280)).save(T/'qa/repairs/m01-after-100pct.png')
print(json.dumps({'candidate':str(dest),'sha256':sha(dest),'nativeRepairSize':repair.size,'finalSize':out.size}))
