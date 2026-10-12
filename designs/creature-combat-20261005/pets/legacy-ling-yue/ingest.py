"""Record an actual built-in result, with optional uniform canvas resampling only."""
from pathlib import Path
from PIL import Image
import json, hashlib, sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(sys.argv[1]); rel=sys.argv[2]; prompt=sys.argv[3]; receipt=sys.argv[4]
refs=json.loads(sys.argv[5])
dest=ROOT/rel; dest.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(source)
native={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'sha256':sha(source),'toolOutputPath':str(source)}
runtime=rel.startswith('runtime/')
operation='copy original bytes'
if runtime:
    if im.size!=(1254,1254) and im.size!=(1024,1024): raise ValueError(f'Unexpected native dimensions {im.size}; review uniform transform')
    if im.mode!='RGBA': raise ValueError('Output lacks native RGBA; do not fake transparency')
    source_size=list(im.size)
    resized=im.resize((980,980),Image.Resampling.LANCZOS)
    im=Image.new('RGBA',(1024,1024),(0,0,0,0))
    im.paste(resized,(22,0))
    operation={'type':'sourceNormalizedTo980Square','sourceSize':source_size,'resize':[980,980],'offset':[22,0],'canvas':[1024,1024],'perFrameAlignment':False,'resample':'LANCZOS'}
    im.save(dest)
else:
    dest.write_bytes(source.read_bytes())
cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
record={'file':rel,'sha256':sha(dest),'generatedAt':datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),'recordedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[r['path'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未开放model/quality选择器，结果未披露可核实的实际型号和质量。','evidence':{'receipt':receipt,'outputHintField':'output_hint'},'prompt':prompt,'references':refs,'native':native,'operation':operation,'derivedFrom':{'file':str(source),'sha256':native['sha256'],'generationReceipt':receipt},'visualStatus':'pending-frame-review','clientIntegration':'not-performed'}
record['derivedFrom']['path']=str(source)
record['derivedFrom']['generationRecord']=receipt
(Path(str(dest)+'.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':rel,'native':[native['width'],native['height']],'output':[im.width,im.height],'alpha':im.getchannel('A').getextrema(),'sha256':record['sha256']},ensure_ascii=False))
