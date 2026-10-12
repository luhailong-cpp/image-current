"""r08_c06 native-only production helpers; no global progress mutation."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime,shutil
from PIL import Image
Z=Path(__file__).resolve().parents[1];TILE='r08_c06'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):return {'path':Path(p).as_posix(),'sha256':sha(p),'role':role,'dimensions':list(Image.open(p).size)}
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,x):assert not p.exists();p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def prepare(patch,version='v1'):
 contract=rd(Z.parent/'production-contract.json');plan=rd(Z/'coordinate-plan.json');tile=next(t for t in plan['tiles'] if t['tile']==TILE);p=next(t for t in tile['patches'] if t['id']==patch);stem=TILE+'_'+patch+'_'+version;box=p['globalContextBox'];layout=Path(contract['layoutReference']);scale=1254/57344
 guide=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,[v*scale for v in box],resample=Image.Resampling.NEAREST)
 layoutp=Z/'layout-only'/(stem+'_layout.png');assert not layoutp.exists();guide.save(layoutp);wr(Path(str(layoutp)+'.derivation.json'),{'file':ref(layoutp,'coordinate layout guidance only, NEVER final art'),'source':ref(layout,'approved map layout'),'globalContextBox':box,'sourceBoxFloat':[v*scale for v in box],'operation':'nearest coordinate crop enlarged ONLY as guidance'})
 candidates=[{'file':(Z/'qa/pair-r09c06-c07-final-v5-r09_c06-context-native.png').as_posix(),'sha256':'c598286f95bb347fd52cc8288b81c9cd0357d3c9998fc364469715b0a8aead94','box':[20365,32653,24691,36979],'trace':(Z/'qa/pair-r09c06-c07-final-v5-trace.json').as_posix()}]
 for rp in sorted((Z/'native').glob(TILE+'_p??_??_*.png.generation.json')):
  a=rd(rp)
  if a['status'] in ['rejected','superseded']:continue
  candidates.append({'file':a['file'],'sha256':a['sha256'],'box':a['coordinates']['globalContextBox'],'generationRecord':rp.as_posix()})
 sources=[]
 for a in candidates:
  b=a['box'];over=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
  if over[0]>=over[2] or over[1]>=over[3]:continue
  if over[2]-over[0]>230 and over[3]-over[1]>230:continue
  source=Path(a['file']);assert sha(source)==a['sha256'];native=Image.open(source).convert('RGB');crop=[over[0]-b[0],over[1]-b[1],over[2]-b[0],over[3]-b[1]];target=[over[0]-box[0],over[1]-box[1],over[2]-box[0],over[3]-box[1]];guide.paste(native.crop(crop),target[:2]);sources.append(dict(a,sourceCropBox=crop,targetBox=target,globalOverlapBox=over,nativePixelsResampled=False))
 gp=Z/'layout-only'/(stem+'_continuity.png');assert not gp.exists();guide.save(gp);wr(Path(str(gp)+'.derivation.json'),{'file':ref(gp,'mixed guidance: native strips protected; pixelated layout guides new painting only'),'baseGuide':ref(layoutp,'layout guidance only'),'nativeSources':sources,'operation':'integer crop/paste of native sources without scaling'})
 refs=[ref(gp,'exact-coordinate edit target; preserve detailed native overlap'),ref(layout,'approved full-map layout only'),ref(Path(contract['detailStyleReference']),'approved material close-up only'),ref(Path(contract['primaryStyleReference']),'approved rounded Q painterly style; no characters/UI/night')]
 prompt="Use case: precise-object-edit. Create ONE native 1254x1254 daylight game-art fragment for 五行奇谈. Image 1 is the exact target coordinate guide: preserve its detailed native overlap strips; replace ONLY pixelated layout guidance with freshly painted native detail. No zoom, rescaling, cropping or reframing. Image 2 is full-map layout only. Image 3 is independent material style, not a coordinate crop. Image 4 is approved rounded Q Daoist painterly style; do not copy UI, figures, night lighting or text. Keep exact object positions, silhouettes, perspective, scale and edge crossings from the guide. Most objects are intentionally cut by the image edges; never complete them into a standalone scene. Continue detailed geometry, wood grain, object contours and stone joints naturally from the preserved strips without a visible color or material boundary. Bright clean daylight, rounded full hand-painted objects, pale grey/blue-grey stone with quiet joints, soft warm wood/gold, no photo grit, plastic reflections or oversharp outlines. Fish-market stock must be fish inside existing trays/tubs, never folded cloth merchandise. No invented objects, people, living animals, captions, grid or watermark. Trees only in existing map positions; keep paths clear. Target "+TILE+" "+patch+". Native overlap boxes (x1,y1,x2,y2): "+str([s['targetBox'] for s in sources])+". Preserve those native strips exactly as the anchors; freshly paint the rest to match."
 pp=Z/'native'/(stem+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8');req={'stem':stem,'tile':TILE,'patch':patch,'tool':'image_gen__imagegen','route':'builtin','createdAt':now(),'prompt':pp.as_posix(),'coordinates':p,'references':refs,'overlaps':sources,'submittedParameters':{'transparent_background':False,'model':None,'quality':None,'referenced_image_paths':[r['path'] for r in refs]},'actualModel':None,'actualQuality':None};wr(Z/'native'/(stem+'.request.json'),req);print(json.dumps(req,ensure_ascii=False))
def save(stem,source):
 p=Z/'native'/(stem+'.png');src=Path(source);assert not p.exists();assert Image.open(src).size==(1254,1254);shutil.copyfile(src,p);req=rd(Z/'native'/(stem+'.request.json'));old=rd(Z/'native/r09_c07_p04_04_v1.png.generation.json');receipt=rd(Z/'native'/(stem+'.receipt.json'));rec={'file':p.as_posix(),'sha256':sha(p),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','configSnapshot':old['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':old['unverifiedReason'],'evidence':{'receipt':(Z/'native'/(stem+'.receipt.json')).as_posix(),'receiptFields':['result.output_hint'],'pngMetadataKeys':list(Image.open(p).info)},'prompt':req['prompt'],'references':req['references'],'coordinates':req['coordinates'],'status':'candidate_pending_seam_qa','nativePixelsResampled':False};wr(Path(str(p)+'.generation.json'),rec);print(json.dumps({'file':p.as_posix(),'sha256':sha(p),'dimensions':[1254,1254]}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(*sys.argv[2:])
 elif sys.argv[1]=='save':save(*sys.argv[2:])

