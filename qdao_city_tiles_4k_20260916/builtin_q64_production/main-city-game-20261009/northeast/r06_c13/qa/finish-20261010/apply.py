"""Replay selected native cores and recorded local repair layers, never resize."""
from pathlib import Path
import argparse,json,hashlib,sys
from datetime import datetime,timezone
from PIL import Image,ImageChops
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1];ZONE=TILE.parent
sys.path.insert(0,str(ZONE));import assemble
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify_file(p,h):
    assert Path(p).is_file(),f'Missing {p}'
    assert sha(p)==h,f'Changed {p}'
def evidence_path(value):
    if isinstance(value,dict):verify_file(value['file'],value['sha256']);return value['file']
    assert Path(value).is_file();return value
def verify_generation(path,source,sourcehash):
    r=read(path);assert Path(r['file']).resolve()==Path(source).resolve();assert r['sha256']==sourcehash
    assert r['route']=='builtin' and r['nativeSize']==[1254,1254] and r['resized'] is False
    assert r['actualModel'] is None and r['actualQuality'] is None
    prompt=evidence_path(r['prompt']);request=evidence_path(r['request']);receipt=evidence_path(r['receipt'])
    q=read(request);t=Path(prompt).read_text(encoding='utf-8-sig');assert t in (q['prompt'],q['prompt']+'\n');read(receipt)
    assert [Path(v).resolve() for v in q['referenced_image_paths']]==[Path(v['file']).resolve() for v in r['references']]
    for ref in r['references']:verify_file(ref['file'],ref['sha256'])
    assert r['sourceOutputByteIdentical']
    verify_file(r['sourceOutputPath'],sourcehash)
    return {'file':str(path),'sha256':sha(path),'allReferencesCurrentlyVerified':True}
def operation(canvas,op):
    verify_file(op['source'],op['sha256']);raw=Image.open(op['source']);assert raw.size==(1254,1254)
    if raw.mode=='RGBA':assert raw.getextrema()[3]==(255,255)
    assert all(type(v) is int for v in op['sourceCrop']+op['destinationTileXY'])
    x0,y0,x1,y1=op['sourceCrop'];x,y=op['destinationTileXY'];assert 0<=x0<x1<=1254 and 0<=y0<y1<=1254
    assert 0<=x and 0<=y and x+x1-x0<=4096 and y+y1-y0<=4096
    mask=None
    if op.get('mask'):
        verify_file(op['mask'],op['maskSha256']);m=Image.open(op['mask']);assert m.size==(1254,1254) and m.mode=='L'
        assert op['maskCrop']==op['sourceCrop'];mask=m.crop(op['maskCrop'])
    canvas.paste(raw.convert('RGB').crop(op['sourceCrop']),(x,y),mask)
    if op.get('generationRecord'):return verify_generation(op['generationRecord'],op['source'],op['sha256'])
    return None
def run(recipe,check):
    spec=read(recipe);tile,plan=assemble.load_plan('r06_c13');sources,evidence,missing,invalid=assemble.inspect_sources(tile,plan)
    assert not missing and not invalid,(missing,invalid)
    canvas=assemble.compose(plan,sources).convert('RGB');assert len(sources)==16
    base=read(HERE/'records/base-replay.json');verify_file(base['baseline'],base['baselineSha256'])
    assert ImageChops.difference(canvas,Image.open(base['baseline']).convert('RGB')).getbbox() is None
    records=[]
    for op in spec['operations']:
        ev=operation(canvas,op)
        if ev:records.append(ev)
    output=Path(spec['output'])
    if check:
        verify_file(output,spec['outputSha256'])
        assert ImageChops.difference(canvas,Image.open(output).convert('RGB')).getbbox() is None
        print(json.dumps({'pixelReplayIdentical':True,'sha256':sha(output),'validSelectedNativeCount':16,'repairLayerCount':len(spec['operations']),'verifiedGenerationRecords':len(records),'formalAcceptedCount':0}))
        return
    assert not output.exists(),f'Preserve existing export {output}'
    output.parent.mkdir(exist_ok=True,parents=True);canvas.save(output)
    spec['outputSha256']=sha(output);spec['createdAt']=datetime.now(timezone.utc).isoformat();save(recipe,spec)
    side={'file':str(output),'sha256':sha(output),'size':[4096,4096],'format':'PNG','opaque':True,'nativeCoreCount':16,'generatedNativeFileCount':17,'route':'selected native-core integer assembly plus local builtin image repairs','resized':False,'recipe':str(recipe),'recipeSha256':sha(recipe),'repairGenerationRecords':records,'actualModel':None,'actualQuality':None,'unverifiedReason':'Host tool does not disclose actual model or quality; composition does not establish them.','formalAcceptedCount':0,'status':spec['status']}
    save(str(output)+'.generation.json',side);print(json.dumps(side,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--recipe',default=str(HERE/'records/candidate-replay.json'));p.add_argument('--check',action='store_true');a=p.parse_args();run(Path(a.recipe),a.check)
