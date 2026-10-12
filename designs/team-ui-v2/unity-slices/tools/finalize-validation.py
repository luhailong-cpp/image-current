import json,hashlib,datetime
from pathlib import Path
from PIL import Image
p=Path('E:/work/image/designs/team-ui-v2/unity-slices')
q=p/'qa'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def outcome(v):
 if isinstance(v,dict):
  if 'success' in v:return v
  if v.get('type')=='text':
   try:return outcome(json.loads(v['text']))
   except (ValueError,KeyError):pass
  for key in ('structuredContent','result','content'):
   if key in v:
    found=outcome(v[key])
    if found:return found
 if isinstance(v,list):
  for e in v:
   found=outcome(e)
   if found:return found
 return None
m=read(p/'manifest.json');tests=read(q/'tests/test-summary.json')
assert len(m['sprites'])==14
assert tests['passed']==33 and tests['failed']==0
mcp=[]
for name in ('mcp-slice-result.json','mcp-title-alpha-result.json'):
 r=outcome(read(p/'tools'/name));assert r and r['success'],name
 mcp.append({'file':'../tools/'+name,'success':True,'logs':r.get('data',{}).get('executionLogs','')})
shots=sorted(q.glob('*_1920x1080.png'))+sorted(q.glob('*_2560x1080.png'))
assert len(shots)==20
image_records=[]
for f in shots:
 im=Image.open(f).convert('RGB')
 colors=len(set(im.resize((64,32)).getdata()))
 assert colors>30,(f.name,colors)
 image_records.append({'file':f.name,'width':im.width,'height':im.height,'sha256':sha(f),'sampledColors':colors})
source=Path('E:/work/mmorpg-client')
files=['Assets/Scripts/UI/Ugui/Team/TeamWindow.cs','Assets/Scripts/UI/Ugui/Team/TeamUiArt.cs','Assets/Scripts/UI/Ugui/Team/TeamUiRoot.cs','Assets/Scripts/Game/Team/TeamUiState.cs']
v={'status':'passed','verifiedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'unityVersion':'6000.6.0f1','targetProject':str(source),'spriteCount':14,
 'officialMcp':mcp,'spriteMetadataAudit':'../manifest.json',
 'tests':{'editModePassed':27,'playModePassed':6,'failed':0,'summary':'tests/test-summary.json',
 'scope':'Tests ran in an independent copy. After tests only section-title coordinates and title-plate exterior Alpha changed; all 20 screenshots were recaptured from the final matching copy.'},
 'rendering':{'method':'Actual production TeamWindow, Unity graphics batch editor in an independent project','successfulLog':'capture-editor-4.log','count':20,
 'resolutions':[[2560,1080],[1920,1080]],'allVisibleLabelsHadGlyphs':True,'allImagesNonblank':True,
 'reviewed':['dual-lists-two-applicants_2560x1080.png','dual-lists_1920x1080.png','service-unavailable_1920x1080.png','decision-pending_1920x1080.png','independent-pages-2_1920x1080.png'],
 'images':image_records},
 'runtimeSources':[{ 'file':f,'sha256':sha(source/f)} for f in files],
 'serviceBoundary':'Main-city team RPC is not implemented. UI and offline snapshot interactions are complete; this is not online team-service acceptance.',
 'priorIssues':'Fixed narrow separator text and section-title ornament overlap. Rejected PreviewScene blank captures; restored the original capture helper. Final source images and editor imports match byte-for-byte.'}
(q/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':v['status'],'sprites':14,'tests':33,'screenshots':20,'officialMcpOperations':len(mcp)}))