from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import sys,json,hashlib
B=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mode=sys.argv[1]
if mode=='anchor':
    tile,source_assembly=sys.argv[2:];assert tile in ['r15_c05','r16_c05'];a=read(source_assembly);source=Path(a['contextOutput']['file']);assert sha(source)==a['contextOutput']['sha256']
    im=Image.open(source).convert('RGB');assert im.size==(4326,4326)
    target=B/tile/'pipeline/anchors'/f'{a["tile"]}-bottom230.native.png';assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);crop=im.crop((0,4096,4326,4326));crop.save(target)
    write(Path(str(target)+'.derivation.json'),{'file':str(target),'sha256':sha(target),'source':a['contextOutput'],'sourceAssembly':{'file':source_assembly,'sha256':sha(source_assembly)},'sourceContextBox':[0,4096,4326,4326],'operation':'exact native crop only','sourceResampling':False,'gameArtNative':True,'sourceStatus':'provisional coverage with open QA; not accepted','formalAccepted':False})
    print(target)
else:
    assert mode=='policy';request=Path(sys.argv[2]);assert '/southwest/' in request.as_posix();r=read(request)
    assert not request.with_name(request.name+'.policy-before-20261013').exists()
    # Unsubmitted metadata annotation only; prompt/reference pixels remain unchanged.
    old=request.with_name(request.name+'.policy-before-20261013');old.write_bytes(request.read_bytes())
    policy=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md');ag=Path('D:/work/image/AGENTS.md')
    for p in [policy,ag]:p.read_text(encoding='utf-8-sig')
    r['currentModelPolicy']={'file':str(policy),'sha256':sha(policy),'rootInstructions':{'file':str(ag),'sha256':sha(ag)},'preference':'Free/included GPT Image2.5 preferred; existing builtin allowed with2.0 fallback; do not stall for unavailable selector/metadata','actualModel':None,'actualQuality':None,'paidApiAllowed':False,'readBeforeCallAtUtc':datetime.now(timezone.utc).isoformat(),'historicalTargetConfigNotActualModelEvidence':True}
    request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(request)
