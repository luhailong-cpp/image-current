from pathlib import Path
import json,hashlib,shutil
from PIL import Image
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Z=T.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
name='post-local-v20261013'
receipt=read(T/'receipts'/(name+'.receipt.json'));src=Path(receipt['sourceOutputPath'])
dst=T/'native/repairs'/(name+'.png');dst.parent.mkdir(exist_ok=True);assert not dst.exists();shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
request=T/'prompts'/(name+'.request.json');payload=read(request)
record={'file':str(dst),'sha256':sha(dst),'nativeSize':[1254,1254],'generatedAt':receipt['receivedAt'],'tool':'image_gen','route':'builtin','sourceOutputPath':str(src),'actualModel':None,'actualQuality':None,'resized':False,'assetRole':'local native repair, not new tile core','prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(request),'evidence':str(T/'receipts'/(name+'.receipt.json')),'references':[{'file':p,'sha256':sha(p)} for p in payload['referenced_image_paths']]}
save(Path(str(dst)+'.generation.json'),record)
baseline=T/'qa/core-baseline/4310c2993aead148fef7/r07_c15-core-baseline.candidate.png'
can=Image.open(baseline).convert('RGB');roi=[610,180,980,880]
can.paste(im.crop(roi),(2450+roi[0],300+roi[1]))
out=T/'candidates/r07_c15.post-local-v20261013.png';assert not out.exists();can.save(out)
qa=T/'qa/local-repair-20261013'
review=qa/'post-composed-review-v1.png';assert not review.exists();can.crop((2450,300,3704,1554)).save(review)
save(qa/'post-composition-v1.json',{'baseCandidate':str(baseline),'baseSha256':sha(baseline),'nativeRepair':str(dst),'nativeRepairSha256':sha(dst),'targetTileBox':[2450,300,3704,1554],'repairCrop':roi,'pasteOrigin':[2450+roi[0],300+roi[1]],'operation':'integer crop and paste of generated pixels only; no resizing, feathering or hand painting','candidate':str(out),'candidateSha256':sha(out),'reviewImage':str(review),'status':'visual_review_pending'})
block=read(Z/'network-block-20261013.json')
block.update({'status':'superseded_by_successful_builtin_call_after_user_resume','resolvedAtUtc':datetime.now(timezone.utc).isoformat(),'successEvidence':str(T/'receipts'/(name+'.receipt.json')),'newGenerationAttemptedAfterError':True,'attemptAuthority':'Latest user instruction to continue relayed by controller; one genuine pending repair call succeeded','networkBypassAttempted':False})
save(Z/'network-block-20261013.json',block)
for f in ['progress.json','production-resume-20261012.json','current-adopted-index-20261012.json']:
    j=read(Z/f);j.update({'generationStopped':False,'newArtworkGenerationAllowed':True,'status':'native_production_resumed_after_successful_builtin_call','updatedAtUtc':datetime.now(timezone.utc).isoformat()});save(Z/f,j)
hp=Z/'HANDOFF.md';hp.write_text('# 当前继续制作：内置调用已成功（2026-10-13）\n\n用户再次要求继续后，post-local-v20261013原生修复调用已成功返回并保存。此前网络撤销记录保留为历史证据，当前解除阻塞，按原分工继续；没有改网络权限、凭据或付费路线。\n\n---\n\n'+hp.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'native':str(dst),'sha256':sha(dst),'candidate':str(out),'review':str(review)}))
