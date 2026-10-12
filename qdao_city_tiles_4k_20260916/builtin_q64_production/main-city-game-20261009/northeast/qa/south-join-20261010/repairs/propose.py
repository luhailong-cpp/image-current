"""Propose local integer paste only; never write outside this repair directory."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def file(p): return {'file':str(p),'sha256':sha(p)}
def write(p, obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def diff(a,b):
    d=ImageChops.difference(a,b)
    return {'meanAbsoluteRgbDifference':sum(ImageStat.Stat(d).mean)/3,'changedBoundingBox':d.getbbox()}

parser=argparse.ArgumentParser(); parser.add_argument('repair'); parser.add_argument('tool_output'); args=parser.parse_args()
base=args.repair
inp=read(HERE/'records'/f'{base}.input.json')
rawpath=HERE/'source'/f'{base}.png'
raw=Image.open(rawpath); raw.load()
assert raw.format=='PNG' and raw.size==(1254,1254), 'No resizing permitted'
if raw.mode=='RGBA': assert raw.getextrema()[3]==(255,255)
raw=raw.convert('RGB'); orig=Image.open(inp['context']['file']).convert('RGB')
assert sha(args.tool_output)==sha(rawpath), 'Copy must match raw tool output'
assert sha(inp['context']['file'])==inp['context']['sha256']
rect=inp['editContextBox']
proposal=orig.copy(); proposal.paste(raw.crop(rect),tuple(rect[:2]))
mask=Image.new('L',orig.size); mask.paste(255,rect)
outside=ImageChops.difference(proposal,orig)
outside.paste((0,0,0),rect)
assert outside.getbbox() is None
exports={}
for name,img in [('proposal-context',proposal),('paste-mask',mask),('before-edit',orig.crop(rect)),('after-edit',proposal.crop(rect))]:
    p=HERE/'crops'/f'{base}-{name}.png'; img.save(p); exports[name]=file(p)
# Wider edge review, still exact original pixels; no resizing or filtering.
margin=64
review=[max(0,rect[0]-margin),max(0,rect[1]-margin),min(1254,rect[2]+margin),min(1254,rect[3]+margin)]
for name,img in [('before-edge-review',orig.crop(review)),('after-edge-review',proposal.crop(review))]:
    p=HERE/'crops'/f'{base}-{name}.png'; img.save(p); exports[name]=file(p)
boundary={}
for name,box in [('top',[rect[0],rect[1],rect[2],rect[1]+3]),('bottom',[rect[0],rect[3]-3,rect[2],rect[3]]),('left',[rect[0],rect[1],rect[0]+3,rect[3]]),('right',[rect[2]-3,rect[1],rect[2],rect[3]])]:
    boundary[name]={'box':box,**diff(orig.crop(box),raw.crop(box))}
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'id':base,'file':str(rawpath),'sha256':sha(rawpath),'nativeSize':[1254,1254],'route':'builtin','actualModel':None,'actualQuality':None,'configTargetSnapshot':read(Path('D:/work/image/config/image-generation.json')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'unverifiedReason':'Host-managed image_gen return exposed image_url and output_hint only; no model/quality metadata was disclosed.','sourceOutputPath':args.tool_output,'sourceOutputByteIdentical':True,'resized':False,'request':file(HERE/'prompts'/f'{base}.request.json'),'prompt':file(HERE/'prompts'/f'{base}.prompt.txt'),'receipt':file(HERE/'receipts'/f'{base}.receipt.json'),'inputRecord':file(HERE/'records'/f'{base}.input.json'),'references':inp['references'],'contextWorldBox':inp['contextWorldBox'],'editWorldBox':inp['editWorldBox'],'editContextBox':rect,'status':'repair-candidate-awaiting-edge-review'}
write(HERE/'records'/f'{base}.generation.json',record)
integration={'id':base,'status':'proposal-not-applied-to-production','generatedSource':file(rawpath),'originalContext':inp['context'],'sourceComposition':inp['sourceComposition'],'contextWorldBox':inp['contextWorldBox'],'editWorldBox':inp['editWorldBox'],'sourceCrop':rect,'operation':'Direct rectangular integer crop/paste of generated pixels into existing context. No blur, resampling, sharpening, feathering, alpha blending or color matching. All pixels outside rectangle remain exactly original.','outsideRectPixelIdentical':True,'rawGeneratorMayAlterOutsideRect':diff(orig,raw),'boundaryDiagnosticsNotAcceptance':boundary,'exports':exports,'visualStatus':'pending','formalAcceptedCount':0,'applicationRecipe':'Recreate base pixels from sourceComposition, then paste generatedSource.crop(sourceCrop) at editWorldBox origin; when applying per 4096 tile, intersect editWorldBox with tile world box and adjust source crop by the same integer offset. No production images changed here.'}
write(HERE/f'{base}.integration-proposal.json',integration)
print(json.dumps({'id':base,'rawSize':[1254,1254],'outsideRectPixelIdentical':True,'boundary':boundary,'exports':exports},ensure_ascii=False,indent=2))
