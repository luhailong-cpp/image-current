"""Read pixels/metadata, hash inputs and write provenance; never modifies images."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
asset=(ROOT/sys.argv[1]).resolve()
if ROOT not in asset.parents:raise ValueError('outside character root')
request_path=(ROOT/sys.argv[2]).resolve(); result_path=(ROOT/sys.argv[3]).resolve()
request=read(request_path);result=read(result_path);args=request['parameters']
with Image.open(asset) as im:
    im.load();size=im.size;mode=im.mode
    alpha=im.getchannel('A').getextrema() if mode=='RGBA' else None
refs=[{'file':p,'sha256':sha(Path(p)),'actuallyViewed':True,'actuallySubmitted':True} for p in args['referenced_image_paths']]
record={'schemaVersion':1,'file':asset.relative_to(ROOT).as_posix(),'sha256':sha(asset),'generatedAt':result.get('completedAt'),'width':size[0],'height':size[1],'format':'PNG','mode':mode,'alphaExtrema':alpha,'nativeFrameCount':1,'nativePerFrame':list(size),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(WORK/'config/image-generation.json'),'submittedParameters':dict(args,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际模型/质量，未开放 model/quality 选择器。','references':refs,'evidence':{'request':request_path.relative_to(ROOT).as_posix(),'result':result_path.relative_to(ROOT).as_posix()},'status':'candidate_needs_visual_review','visualReview':sys.argv[4] if len(sys.argv)>4 else 'pending','operations':'byte_exact_copy_from_host_output'}
destination=(ROOT/sys.argv[5]).resolve() if len(sys.argv)>5 else Path(str(asset)+'.generation.json')
if ROOT not in destination.parents:raise ValueError('record outside character root')
destination.parent.mkdir(parents=True,exist_ok=True)
destination.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(asset),'size':size,'mode':mode,'alpha':alpha,'sha256':record['sha256']},ensure_ascii=False))
