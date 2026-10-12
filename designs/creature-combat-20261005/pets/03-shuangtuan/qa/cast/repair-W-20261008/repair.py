import json, hashlib, shutil, sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw

B=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
R=B/'records/cast/W'; S=B/'source/cast/W/repair-20261008'; Q=B/'qa/cast/repair-W-20261008'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare(n, phase, support='04', attempt=1, basis=None):
    f=f'{int(n):02d}'; a=f'{f}.repair-20261008-a{attempt}'
    refs=[str(B/f'runtime/cast/W/{f}.png'),str(B/f'runtime/cast/W/{support}.png'),'D:/work/image/designs/pets-xianling-20260924/source/03-shuangtuan-E.png','D:/work/image/designs/pets-xianling-20260924/source/03-shuangtuan-W.png','D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png']
    prompt=f'''Use case: precise-object-edit. Edit image 1 only, one transparent 1024x1024 square game animation frame of the EXISTING Shuangtuan marten. Frame cast W {f}/16. Image 1 is exact EDIT TARGET. Image 2 is support/adjacent-frame continuity reference only. Image 3 E and image 4 W lock existing character identity. Image 5 is the primary approved painting/material style reference, not content to copy.
MINIMAL LOCAL ANATOMICAL ANIMATION REPAIR: {phase}
All coordinates refer to a 1024 square with top-left origin. Keep the entire animal in the exact same canvas/framing and scale. This is an original-place cast, no movement. The two weight-bearing hind toe-contact areas should remain approximately near-side (445,900), far-side (710,945); preserve each leg's anatomical attachment to its respective haunch. Do not slide planted toes; ankle/hock and hip can bend to accommodate the torso. Natural marten crouch/rise; short rounded animal paws, never humanoid hands. Keep two hind legs, exactly two front legs, exactly two round ears and exactly ONE pale-jade thick curled tail. W is TRUE rear three-quarter facing upper-left: preserve rear head, spine/back and rear hind feet, no face or chest toward viewer.
Preserve the edit target's head identity, pearl-grey fur, approved silk-like wide tail, ivory/pale celadon scarf, gold flower-and-crescent-jade ornament, red knot and droplet pendant, scarf streamers and tail attachment. Ornament belongs to scarf, no handheld object. Only adjust joints and connected torso needed for the specified pose; do not invent additional accessories, swap legs, redesign, mirror, crop, translate or rescale the sprite. Do not add floor, shadows, labels, grid, border or multiple frames. One complete full-body animal only. Transparent background with clean alpha. Preserve high-definition warm bright clean rounded hand-painted Q-style fur and materials of references. Target user-requested GPT Image 2.5/max visual completion; tool-managed model/quality not asserted.'''
    if basis: refs[0]=str(B/f'runtime/cast/W/{basis}.png')
    P=B/f'prompts/cast/W/{a}.txt';P.parent.mkdir(parents=True,exist_ok=True);P.write_text(prompt,encoding='utf-8')
    request={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True}
    (R/f'{a}.request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
    inputs={'references':[{'path':p,'sha256':sha(p),'purpose':['edit target','support or neighbor continuity reference','E identity','W identity','primary approved painting style'][i]} for i,p in enumerate(refs)],'previousRuntimeSha256':sha(B/f'runtime/cast/W/{f}.png')}
    (R/f'{a}.inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8')
    old=R/f'{f}.before-repair-20261008.generation.json'
    if not old.exists(): shutil.copy2(R/f'{f}.generation.json',old)
    print(str(R/f'{a}.request.json'))
def save(n,native_path,attempt=1):
    f=f'{int(n):02d}'; a=f'{f}.repair-20261008-a{attempt}';S.mkdir(parents=True,exist_ok=True)
    native=S/f'{f}-a{attempt}.png'; shutil.copy2(native_path,native); im=Image.open(native)
    assert im.mode=='RGBA' and im.width==im.height,(im.mode,im.size)
    assert im.getchannel('A').getextrema()[0]==0
    candidate=S/f'{f}-a{attempt}-1024.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(candidate)
    req=json.loads((R/f'{a}.request.json').read_text(encoding='utf-8'));inputs=json.loads((R/f'{a}.inputs.json').read_text(encoding='utf-8'))
    r={'file':candidate.relative_to(B).as_posix(),'sha256':sha(candidate),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'referenced_image_paths':req['referenced_image_paths'],'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露model/quality，目标不等于实际选择器。','prompt':f'prompts/cast/W/{a}.txt','references':inputs['references'],'evidence':{'receipt':f'records/cast/W/{a}.receipt.json'},'native':{'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA'},'derivedFrom':{'file':native.relative_to(B).as_posix(),'sha256':sha(native),'deleted':False},'editHistory':{'previousGenerationRecord':f'records/cast/W/{f}.before-repair-20261008.generation.json','previousRuntimeSha256':inputs['previousRuntimeSha256']},'operation':'Uniform whole-canvas Lanczos resize to 1024; no pose synthesis, crop, flip, translation, interpolation or per-foot alignment.','direction':'W','action':'cast','frame':int(n),'durationMs':45,'pivot':[0.5,0.08],'event':None,'visualStatus':'candidate pending actual inspection'}
    (R/f'{a}.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidate':str(candidate),'nativeSize':im.size,'sha256':sha(candidate)}))
def accept(n,attempt=1):
    f=f'{int(n):02d}';rp=R/f'{f}.repair-20261008-a{attempt}.generation.json';r=json.loads(rp.read_text(encoding='utf-8'));c=B/r['file'];dest=B/f'runtime/cast/W/{f}.png'
    assert sha(c)==r['sha256'];shutil.copy2(c,dest);r['file']=dest.relative_to(B).as_posix();r['visualStatus']='Actual full-frame inspection passed for rear-view identity, anatomy, support and requested phase; final adjacent-chain review pending.'
    for p in [rp,R/f'{f}.generation.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print('accepted '+f+' '+sha(dest))
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else '04',int(sys.argv[5]) if len(sys.argv)>5 else 1,sys.argv[6] if len(sys.argv)>6 else None)
    elif mode=='save':save(sys.argv[2],sys.argv[3],int(sys.argv[4]) if len(sys.argv)>4 else 1)
    elif mode=='accept':accept(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1)
