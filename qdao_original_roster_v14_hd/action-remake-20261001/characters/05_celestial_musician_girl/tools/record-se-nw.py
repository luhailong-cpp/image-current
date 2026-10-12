from pathlib import Path
import sys,json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
stem=ROOT/sys.argv[1]
req=read(Path(str(stem)+'.request.json'))
res=read(Path(str(stem)+'.result.json'))
asset=ROOT/req['asset']
args=req['parameters']
with Image.open(asset) as im:
 im.load();size=im.size;mode=im.mode;alpha=im.getchannel('A').getextrema() if mode=='RGBA' else None
refs=[{'file':p,'sha256':sha(Path(p)),'actuallyViewed':True,'actuallySubmitted':True,'role':(['identity','direction_and_scale','style']+['previous_phase'])[min(i,3)]} for i,p in enumerate(args['referenced_image_paths'])]
record={'schemaVersion':1,'file':asset.relative_to(ROOT).as_posix(),'sha256':sha(asset),'generatedAt':res['completedAt'],'width':size[0],'height':size[1],'format':'PNG','mode':mode,'alphaExtrema':alpha,'nativeFrameCount':1,'nativePerFrame':list(size),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT.parents[3]/'config/image-generation.json'),'submittedParameters':dict(args,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际模型/质量，未开放 model/quality 选择器。','references':refs,'prompt':str(stem.relative_to(ROOT))+'.prompt.txt','evidence':{'request':str(stem.relative_to(ROOT))+'.request.json','result':str(stem.relative_to(ROOT))+'.result.json'},'status':'candidate_needs_visual_review','visualReview':'pending','operations':'byte_exact_copy_from_host_output','intendedAnchor':{'canvas':[1024,1024],'virtualGroundRoot':[512,942],'scaleMode':'fixed_global_canvas_not_bbox_fit'},'dynamicReview':'pending'}
Path(str(stem)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(asset),'size':size,'mode':mode,'alpha':alpha,'sha256':record['sha256']},ensure_ascii=False))
