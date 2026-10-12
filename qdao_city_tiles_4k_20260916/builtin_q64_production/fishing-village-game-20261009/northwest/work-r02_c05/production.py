from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,shutil,re
from datetime import datetime,timezone
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r02_c05'
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009')
REFS=[P/'donghai-natural-stone-clear-routes-v10.png',P/'donghai-natural-stone-detail-v1.png',P/'user-references-20261009/mail-daoist-style.jpg']
WEST=B/'work-r02_c04/resume-20261012-v02';read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
for d in ['native','guides','prompts','receipts','qa']:(W/d).mkdir(parents=True,exist_ok=True)
def name(r,c):return f'r02_c05_s{r:02d}_s{c:02d}_v01'
def box(r,c):
 x=16384+(c-1)*1024;y=4096+(r-1)*1024;return [x-115,y-115,x+1139,y+1139]
def native(r,c):
 p=W/'native'/(name(r,c)+'.png');return p if p.exists() else None
def initialize():
 plan={'tile':'r02_c05','origin':[16384,4096],'globalCoreBox':[16384,4096,20480,8192],'nativeSize':[1254,1254],'coreSize':1024,'halo':115,'rows':4,'columns':4,'order':[[r,c] for r in [4,3,2,1] for c in [1,2,3,4]],'westCandidate':str(WEST/'r02_c04.candidate.png'),'westCandidateSHA256':sha(WEST/'r02_c04.candidate.png'),'westAssembly':str(WEST/'r02_c04.assembly.json'),'westAssemblySHA256':sha(WEST/'r02_c04.assembly.json'),'assignedTo':'/root/sol_e3','formalAccepted':False,'status':'native-production-started'}
 if not (W/'plan.json').exists():write(W/'plan.json',plan)
 lay=Image.open(REFS[0]);b=[16384,4096,20480,8192];f=[v*lay.width/57344 for v in b];im=lay.transform((4096,4096),Image.Transform.EXTENT,f,Image.Resampling.BICUBIC);im.save(W/'guides/r02_c05.layout-only-guide.png');im.resize((1024,1024),Image.Resampling.LANCZOS).save(W/'qa/r02_c05.layout-preview-only.png')
 for r in range(1,5):
  b=[15245,3981+(r-1)*1024,16499,5235+(r-1)*1024];p=W/'guides'/f'west-r02_c04-s{r:02d}.native-context.png';Image.open(WEST/'joint.context.png').crop((3072,(r-1)*1024,4326,(r-1)*1024+1254)).save(p)
  write(str(p)+'.derivation.json',{'file':str(p),'sha256':sha(p),'globalNativeBox':b,'sourceCandidate':str(WEST/'r02_c04.candidate.png'),'sourceCandidateSHA256':sha(WEST/'r02_c04.candidate.png'),'sourceAssembly':str(WEST/'r02_c04.assembly.json'),'sourceAssemblySHA256':sha(WEST/'r02_c04.assembly.json'),'haloSourceJoint':str(WEST/'joint.context.png'),'haloSourceJointSHA256':sha(WEST/'joint.context.png'),'nativeScaleResampled':False,'guideOnly':True})
 print(json.dumps(plan))
def prepare(r,c):
 n=name(r,c);b=box(r,c);lay=Image.open(REFS[0]);frac=[v*lay.width/57344 for v in b];im=lay.transform((1254,1254),Image.Transform.EXTENT,frac,Image.Resampling.BICUBIC);neighbors=[]
 for rr,cc in [(r+1,c),(r,c-1)]:
  p=native(rr,cc) if 1<=rr<=4 and 1<=cc<=4 else None
  if p:
   nb=box(rr,cc);inter=[max(b[0],nb[0]),max(b[1],nb[1]),min(b[2],nb[2]),min(b[3],nb[3])];crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-b[0],inter[1]-b[1]];im.paste(Image.open(p).crop(crop),dest);neighbors.append({'file':str(p),'sha256':sha(p),'globalNativeBox':nb,'crop':crop,'destination':dest,'role':'actual unscaled current native neighbor'})
 if c==1:
  p=W/'guides'/f'west-r02_c04-s{r:02d}.native-context.png';im.paste(Image.open(p).crop((1024,0,1254,1254)),(0,0));neighbors.append({'file':str(p),'sha256':sha(p),'globalNativeBox':[15245,3981+(r-1)*1024,16499,5235+(r-1)*1024],'crop':[1024,0,1254,1254],'destination':[0,0],'role':'fixed r02_c04 western edge/native continuation'})
 target=W/'guides'/(n+'.guide.png');im.save(target);write(str(target)+'.derivation.json',{'file':str(target),'sha256':sha(target),'globalNativeBox':b,'layout':{'file':str(REFS[0]),'sha256':sha(REFS[0]),'fractionalBox':frac,'resizedGuideOnly':True},'neighbors':neighbors,'nativeOutputResampled':False,'guideOnly':True})
 if neighbors:
  sheet=Image.new('RGB',(1254*len(neighbors),1254));
  for i,z in enumerate(neighbors):sheet.paste(Image.open(z['file']),(i*1254,0))
  supporting=W/'guides'/(n+'.native-neighbors-reference.png');sheet.save(supporting);write(str(supporting)+'.derivation.json',{'file':str(supporting),'sha256':sha(supporting),'guideOnly':True,'nativeScaleResampled':False,'panes':neighbors})
 else:
  supporting=W/'guides'/f'west-r02_c04-s{r:02d}.native-context.png'
 refs=[target,supporting]+REFS;roles=['edit target: approved-layout crop guide with exact current native-neighbor overlap pixels','supporting exact native neighbors, one1254px pane each; geometry/detail/continuity only','mandatory full-map layout and placement reference','mandatory natural stone/material/detail reference','PRIMARY Q-style Daoist art reference, exclude interface/text']
 locked=[]
 if c==1:locked.append('left230px match fixed west scene exactly, including any wood rails, rocks and leaves')
 if r<4:locked.append('bottom230px match actual generated south neighbor exactly')
 if c>1:locked.append('left230px match actual generated west neighbor exactly')
 prompt=f'''Use case: stylized-concept. Produce one opaque native1254x1254 game-map patch at original pixel scale; no resampling. Tile r02_c05, subcell s{r:02d}s{c:02d}, globalNativeBox {b} on a57344-square14x14 map, 4096px tiles,1024px core+115px halo. Image1 is the exact framing/layout target guide, already containing unscaled neighboring overlap pixels. Image2 is an unscaled reference sheet of current native neighbors, each pane1254px wide; use it for matched geometry, leaf/rock/wood scale and seamless daylight continuity. Images3/4 give the approved full layout and natural stone/material details. Image5 is PRIMARY Daoist Q-style game art style; exclude UI and all text.
Render the specific terrain and features shown in image1 at polished native detail, expanding the established west r02_c04 hillside into the next tile. Preserve the approved full-map locations, isometric camera angle and zoom; rocks and trees should have varied natural forms. Match current neighboring painting, sun direction, gray/cyan natural stone and warm wood materials. Keep the hillside organic and coherent, with only the existing layout's rail/walkway/rock/water features; do not invent buildings, props or vegetation that is absent in the target. Paths remain connected and walkable where present. Match and continue any truncated rail, post, rock or branch at the exact target-edge coordinates. Locked overlap constraints: {'; '.join(locked) if locked else 'retain the reference frame and isometric scale'}. Avoid hard seams, grid artifacts, pasted borders, isolated potted plants, characters, UI, text, watermarks, added objects, overall red ground or nighttime. One target scene alone, no reference collage. Native1254x1254 exact registered frame.'''
 pf=W/'prompts'/(n+'.prompt.txt');pf.write_text(prompt,encoding='utf8');req={'id':n,'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'globalNativeBox':b,'coreBox':[b[0]+115,b[1]+115,b[2]-115,b[3]-115],'referenced_image_paths':[str(p) for p in refs],'referenceRoles':roles,'references':[{'file':str(p),'sha256':sha(p),'role':r} for p,r in zip(refs,roles)],'prompt':prompt,'promptFile':str(pf),'promptSHA256':sha(pf),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'route':'builtin','tool':'image_gen.imagegen','transparent_background':False};write(W/'receipts'/(n+'.request.json'),req);print(json.dumps(req,ensure_ascii=False))
def save(n):
 req=read(W/'receipts'/(n+'.request.json'));rec=read(W/'receipts'/(n+'.receipt.json'));original=Path(re.search(r' as (C:\\[^\n]+?\.png) by default',rec['output_hint']).group(1));p=W/'native'/(n+'.png');assert not p.exists();shutil.copy2(original,p);im=Image.open(p);assert im.size==(1254,1254)
 g={'file':str(p),'sha256':sha(p),'generatedAt':rec['returnedAtUtc'],'width':im.width,'height':im.height,'format':'PNG','route':'builtin','tool':'image_gen.imagegen','submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin exposes no actual model/quality metadata.','globalNativeBox':req['globalNativeBox'],'globalCoreBox':req['coreBox'],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'prompt':req['promptFile'],'promptSHA256':req['promptSHA256'],'references':req['references'],'evidence':{'request':str(W/'receipts'/(n+'.request.json')),'requestSHA256':sha(W/'receipts'/(n+'.request.json')),'receipt':str(W/'receipts'/(n+'.receipt.json')),'receiptSHA256':sha(W/'receipts'/(n+'.receipt.json'))},'toolOriginal':{'file':str(original),'sha256':sha(original)},'status':'native-candidate-pending-grid-and-visual-QA'};write(str(p)+'.generation.json',g);print(json.dumps({'file':str(p),'sha256':g['sha256'],'dimensions':im.size}))
if __name__=='__main__':
 if sys.argv[1]=='initialize':initialize()
 elif sys.argv[1]=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
 elif sys.argv[1]=='save':save(sys.argv[2])
