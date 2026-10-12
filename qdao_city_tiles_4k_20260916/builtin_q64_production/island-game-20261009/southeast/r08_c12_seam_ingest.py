from pathlib import Path
from PIL import Image
import hashlib,json,sys,os,shutil
from datetime import datetime,timezone
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid,source=sys.argv[1:];source=Path(source);dest=R/'native'/f'{pid}.png';assert not dest.exists();shutil.copyfile(source,dest)
assert Image.open(dest).size==(1254,1254)
q=read(R/'prompts'/f'{pid}.request.json');template=read(R/'native/r08_c12_p14_v01.png.generation.json');box=q['nativeTileBox'];x,y=box[:2]
template.update(file=str(dest),sha256=sha(dest),generatedAt=datetime.now(timezone.utc).isoformat(),sourceOutputPath=str(source),sourceOutputSha256=sha(source),prompt=q['promptPath'],promptSha256=sha(q['promptPath']),references=q['references'],coordinate={'id':pid,'nativeTileBox':box,'nativeGlobalBox':[45056+x,28672+y,45056+x+1254,28672+y+1254],'coreTileBox':[x+115,y+115,x+1139,y+1139]},evidence={'toolReceipt':'receipts/'+pid+'.json','returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},baseCandidate=q['baseCandidate'],baseCandidateSha256=q['baseCandidateSha256'],status='repair_candidate_pending_native_boundary_review')
write(Path(str(dest)+'.generation.json'),template)
p=read(R/'progress-r08_c12.json');p.update(status='internal_repair',generatedNativeCount=len(list((R/'native').glob('r08_c12*.generation.json'))),currentPatch=pid,nextStep='Inspect native repair and its hard overlay perimeter');write(R/'progress-r08_c12.json',p)
print(json.dumps({'file':str(dest),'sha256':sha(dest),'size':[1254,1254]}))

