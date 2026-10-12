"""Record a built-in foot-axis edit and export it with the established fixed transform."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
EV=ROOT/'provenance/foot-axis-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def stage(d,f,v,host,request,result,action="run"):
    assert action in ["run","hit","attack","cast"]
    assert f <= {"run":16,"hit":6,"attack":12,"cast":16}[action]
    assert d in ['N','NE','E','SE','S','SW','W','NW'] and 1<=f<=16 and v>=1
    tag=f'{d}{f:02d}-v{v}' if action=='run' else f'{action}-{d}{f:02d}-v{v}'
    sub=d if action=='run' else f'{action}/{d}'
    native=ROOT/f'staging/foot-axis-20261004/{sub}/{f:02d}-v{v}.native.png'
    out=ROOT/f'staging/foot-axis-20261004/{sub}/{f:02d}-v{v}.png'
    assert not native.exists() and not out.exists(), 'Never overwrite a candidate.'
    req=read(Path(request));reg=read(ROOT/'registration.json')
    old=read(ROOT/f'final/{action}/{d}/{f:02d}.png.generation.json')
    native.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(host,native)
    im=Image.open(native);im.load();assert im.size==(1254,1254) and im.mode=='RGBA'
    gfile=EV/f'{tag}.generation.json';prompt=EV/f'{tag}.prompt.txt'
    prompt.write_text(req['prompt'],encoding='utf-8')
    generation={'schemaVersion':1,'file':rel(native),'sha256':sha(native),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA','nativeFrameCount':1,'nativePerFrame':True,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(Path('D:/work/image/config/image-generation.json')),'submittedParameters':dict(req,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际模型/质量；未开放 model/quality 选择器。','prompt':rel(prompt),'references':[{'file':p,'sha256':sha(Path(p)),'role':'edit_target' if i==0 else 'supporting_reference','actuallySubmitted':True} for i,p in enumerate(req['referenced_image_paths'])],'evidence':{'request':rel(Path(request)),'result':rel(Path(result)),'hostOutputPath':str(host)},'editTargetFormalFile':f'final/{action}/{d}/{f:02d}.png','editTargetFormalSha256':sha(ROOT/f'final/{action}/{d}/{f:02d}.png'),'status':'pending_visual_review'}
    write(gfile,generation)
    scale=reg['globalScale'];sx,sy=reg['sequences'][action+'/'+d]['sourceRoot'];tx,ty=reg['targetRoot']
    matrix=(1/scale,0,sx-tx/scale,0,1/scale,sy-ty/scale)
    exported=im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA')
    a=exported.getchannel('A');border=max(a.crop(b).getextrema()[1] for b in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)])
    assert border==0;exported.save(out)
    meta={'operation':'uniform_resample_and_constant_sequence_registration','status':'pending_visual_review','file':rel(out),'sha256':sha(out),'width':1024,'height':1024,'mode':'RGBA','source':{'file':rel(native),'sha256':sha(native),'nativeSize':[1254,1254],'generationRecord':rel(gfile)},'actualModel':None,'actualQuality':None,'transform':{'globalScale':scale,'sourceRoot':[sx,sy],'targetRoot':[tx,ty],'inverseAffine':matrix,'registrationFile':'registration.json','perFrameNormalization':False},'edgeMaxAlpha':border,'finalVisualPassed':False,'clientValidated':False,'sourceGeneration':generation,'nativeSourceRecord':rel(gfile)}
    if action=='run':meta.update(stancePosition=old['stancePosition'],supportLeg=old['supportLeg'])
    write(Path(str(out)+'.generation.json'),meta)
    print(json.dumps({'direction':d,'frame':f,'version':v,'reviewFile':rel(out),'sha256':sha(out),'nativeSha256':sha(native),'previousSha256':generation['editTargetFormalSha256']}))
if __name__=='__main__':
    args=sys.argv[1:]
    action=args.pop(0) if args[0] in ['run','hit','attack','cast'] else 'run'
    stage(args[0],int(args[1]),int(args[2]),Path(args[3]),Path(args[4]),Path(args[5]),action)
