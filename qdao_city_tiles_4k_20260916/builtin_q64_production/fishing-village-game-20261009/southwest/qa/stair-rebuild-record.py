import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

Z=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stem=sys.argv[1]
d=Z/'stair-rebuild'
d.mkdir(exist_ok=True)
if sys.argv[2]=='request':
    refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
    inputs=[{'path':(Z/'qa/r10_c04-six-step-structure-layout-1254.png').as_posix(),'role':'edit target: complete staircase coordinate-layout-only guidance; replace pixelated guidance with clean six-nose structure'},refs[1],refs[2],{'path':(Z/'native/r09_c04_p04_04_v2.png').as_posix(),'role':'existing native stone upper anchor and lantern material style; preserve position at mapped coordinate, not whole-image layout'}]
    for r in inputs: r['sha256']=sha(r['path'])
    obj={'stem':stem,'tile':'r10_c04','role':'complete six-step structure reference only; not final native game tile and never enlarge as final pixels','globalBox':[12544,36096,16640,40192],'expectedDimensions':[1254,1254],'references':inputs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'preparedAtUtc':datetime.now(timezone.utc).isoformat()}
    write(d/(stem+'.request.json'),obj)
    print(json.dumps(obj,ensure_ascii=False))
elif sys.argv[2]=='record':
    p=d/(stem+'.png')
    req=json.loads((d/(stem+'.request.json')).read_text(encoding='utf-8-sig'))
    rec=json.loads((d/(stem+'.receipt.json')).read_text(encoding='utf-8-sig'))
    with Image.open(p) as im: dim=list(im.size); meta=list(im.info.keys())
    out={**req,'file':p.as_posix(),'sha256':sha(p),'dimensions':dim,'generatedAtUtc':rec['finishedAtUtc'],'route':'builtin','tool':'image_gen__imagegen','actualModel':None,'actualQuality':None,'unverifiedReason':'Host tool exposes neither model nor quality selector nor returned version evidence.','prompt':(d/(stem+'.prompt.txt')).as_posix(),'receipt':(d/(stem+'.receipt.json')).as_posix(),'metadataKeys':meta,'status':'candidate_pending_structure_qa','nativePixelsResampled':False}
    write(d/(stem+'.png.generation.json'),out)
    print(json.dumps(out,ensure_ascii=False))
