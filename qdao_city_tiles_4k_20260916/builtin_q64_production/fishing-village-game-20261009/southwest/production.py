import sys
sys.dont_write_bytecode = True

import json, hashlib, os, time, uuid
import importlib.util
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parent
CONTRACT = json.loads((ROOT.parent / 'production-contract.json').read_text(encoding='utf-8-sig'))
SCALE = 1254 / 57344

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + '.pending-' + uuid.uuid4().hex)
    pending.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for attempt in range(6):
        try:
            os.replace(pending, path)
            return
        except OSError:
            if attempt == 5:
                if path.name == 'progress.json':
                    print('Progress file busy; retained update at ' + str(pending), file=sys.stderr)
                    return
                raise
            time.sleep(0.1 * (attempt + 1))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def init():
    refs = []
    for key, role in [('layoutReference', 'only current full-map layout reference'), ('detailStyleReference', 'independent material and architecture style close-up, not a coordinate crop'), ('primaryStyleReference', 'primary approved Daoist Q painterly style; do not copy UI or night lighting')]:
        p = Path(CONTRACT[key])
        with Image.open(p) as im:
            size = list(im.size)
        refs.append({'path': p.as_posix(), 'role': role, 'sha256': sha(p), 'dimensions': size})
    assert refs[0]['sha256'] == CONTRACT['layoutSha256']
    assert refs[1]['sha256'] == CONTRACT['detailSha256']
    write(ROOT/'references.json', refs)
    tiles = []
    for r in range(8,15):
        for c in range(1,8):
            x,y=(c-1)*4096,(r-1)*4096
            patches=[]
            for pr in range(4):
                for pc in range(4):
                    px,py=x+pc*1024,y+pr*1024
                    box=[px-115,py-115,px+1139,py+1139]
                    patches.append({'id':f'p{pr+1:02d}_{pc+1:02d}', 'globalCoreBox':[px,py,px+1024,py+1024], 'globalContextBox':box, 'overviewContextBox':[v*SCALE for v in box], 'expectedNativeDimensions':[1254,1254], 'sourceCoreBox':[115,115,1139,1139], 'status':'pending'})
            tiles.append({'tile':f'r{r:02d}_c{c:02d}', 'globalCoreBox':[x,y,x+4096,y+4096], 'status':'pending','patches':patches})
    write(ROOT/'coordinate-plan.json', {'mapCanvas':[57344,57344], 'zone':'southwest','firstTile':'r09_c04','tiles':tiles,'allBoxesHalfOpen':True,'adjacentPatchOverlapPixels':230,'noUpscaleForFinalArt':True})
    write(ROOT/'progress.json', {'zone':'southwest','status':'preparing_first_native','updatedAtUtc':now(),'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'target4kCount':49,'currentTile':'r09_c04','currentPatch':'p01_01','nextStep':'Generate native p01_01 with attached style and exact layout guide, measure returned size before continuing.','errors':[],'capacity5000Validated':False,'clientMappingValidated':False})

def guide(tile_id, patch_id):
    plan=json.loads((ROOT/'coordinate-plan.json').read_text(encoding='utf-8'))
    tile=next(t for t in plan['tiles'] if t['tile']==tile_id)
    patch=next(p for p in tile['patches'] if p['id']==patch_id)
    source=Path(CONTRACT['layoutReference'])
    with Image.open(source) as im:
        for name, box in [(tile_id, tile['globalCoreBox']),(tile_id+'_'+patch_id,patch['globalContextBox'])]:
            bbox=[v*SCALE for v in box]
            result=im.transform((1254,1254),Image.Transform.EXTENT,bbox,resample=Image.Resampling.NEAREST)
            p=ROOT/'layout-only'/f'{name}.png'
            p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists():
                result.save(p)
            else:
                with Image.open(p) as existing:
                    identical = existing.size == result.size and existing.convert('RGB').tobytes() == result.convert('RGB').tobytes()
                if not identical:
                    pending = p.with_name(p.stem + '.pending-' + uuid.uuid4().hex + '.png')
                    result.save(pending)
                    os.replace(pending, p)
            write(Path(str(p)+'.derivation.json'), {'file':p.as_posix(),'sha256':sha(p),'role':'layout-only mechanical crop enlarged for coordinate guidance, NEVER final native game art','operation':{'type':'coordinate crop and nearest-neighbor enlargement','sourceBoxFloat':bbox,'outputDimensions':[1254,1254]},'derivedFrom':{'path':source.as_posix(),'sha256':sha(source)},'globalBox':box})
    print(json.dumps(patch))

def record(stem):
    imagepath=ROOT/'native'/f'{stem}.png'
    receiptpath=ROOT/'native'/f'{stem}.receipt.json'
    receipt=json.loads(receiptpath.read_text(encoding='utf-8-sig'))
    invocation=json.loads((ROOT/'native'/f'{stem}.request.json').read_text(encoding='utf-8-sig'))
    with Image.open(imagepath) as im:
        size=list(im.size)
        fmt=im.format
        image_info_keys=list(im.info.keys())
    refs=[]
    for r in invocation['references']:
        refs.append({**r,'sha256':sha(r['path'])})
    record={'file':imagepath.as_posix(),'sha256':sha(imagepath),'generatedAt':receipt['finishedAtUtc'],'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':(json.loads((ROOT.parents[3]/'config'/'image-generation.json').read_text(encoding='utf-8-sig')) if (ROOT.parents[3]/'config'/'image-generation.json').is_file() else None),'configSnapshotUnavailableReason':(None if (ROOT.parents[3]/'config'/'image-generation.json').is_file() else 'Configuration file not present at record time; actual model and quality remain undisclosed by builtin tool'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未开放型号/质量选择器，未披露实际型号/质量；PNG元数据无可核实型号字段。','evidence':{'receipt':receiptpath.as_posix(),'receiptFields':['result.output_hint'],'pngMetadataKeys':image_info_keys},'prompt':(ROOT/'native'/f'{stem}.prompt.txt').as_posix(),'references':refs,'coordinates':invocation['coordinates'],'status':'candidate_pending_seam_qa','nativePixelsResampled':False}
    write(Path(str(imagepath)+'.generation.json'),record)
    progress=json.loads((ROOT/'progress.json').read_text(encoding='utf-8-sig'))
    progress.update({'status':'native_candidate_ready','updatedAtUtc':now(),'generatedNativeCount':len(list((ROOT/'native').glob('*.png.generation.json'))),'currentTile':invocation['tile'],'currentPatch':invocation['patch'],'nextStep':'Inspect geometry and native dimensions, prepare adjacent continuity guide.'})
    write(ROOT/'progress.json',progress)
    print(json.dumps({'file':str(imagepath),'dimensions':size,'sha256':record['sha256']}))

def prepare(tile_id,patch_id,version='v1'):
    guide(tile_id,patch_id)
    plan=json.loads((ROOT/'coordinate-plan.json').read_text(encoding='utf-8'))
    tile=next(t for t in plan['tiles'] if t['tile']==tile_id)
    patch=next(p for p in tile['patches'] if p['id']==patch_id)
    target_box=patch['globalContextBox']
    pbase=ROOT/'layout-only'/f'{tile_id}_{patch_id}.png'
    canvas=Image.open(pbase).convert('RGB')
    sources=[]
    for rp in sorted((ROOT/'native').glob('*.png.generation.json')):
        rec=json.loads(rp.read_text(encoding='utf-8-sig'))
        if rec.get('status') in ['rejected','frozen_upstream_geometry_repair','superseded'] or rec.get('coordinates',{}).get('role','').startswith('localized native seam repair'): continue
        box=rec.get('coordinates',{}).get('globalContextBox')
        if not box or len(box)!=4: continue
        inter=[max(target_box[0],box[0]),max(target_box[1],box[1]),min(target_box[2],box[2]),min(target_box[3],box[3])]
        if inter[2]<=inter[0] or inter[3]<=inter[1]: continue
        if inter[2]-inter[0]>230 and inter[3]-inter[1]>230: continue
        with Image.open(rec['file']) as im:
            if im.size!=(1254,1254): raise ValueError('Need replan for actual native size')
            crop=im.crop((inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]))
            canvas.paste(crop,(inter[0]-target_box[0],inter[1]-target_box[1]))
        sources.append({'path':rec['file'],'sha256':rec['sha256'],'globalOverlapBox':inter,'targetBox':[inter[0]-target_box[0],inter[1]-target_box[1],inter[2]-target_box[0],inter[3]-target_box[1]],'role':'existing adjacent native overlap: preserve geometry, colors and details'})
    context=ROOT/'layout-only'/f'{tile_id}_{patch_id}_{version}_continuity.png'
    canvas.save(context)
    write(Path(str(context)+'.derivation.json'),{'file':context.as_posix(),'sha256':sha(context),'role':'mixed continuity edit guide: native overlap protected, enlarged layout elsewhere is guidance only','operation':'integer crop and paste, no resampling of native input, no drawing','baseGuide':pbase.as_posix(),'nativeSources':sources})
    stem=f'{tile_id}_{patch_id}_{version}'
    refs=[{'path':context.as_posix(),'role':'edit target: exact coordinate layout guide with existing adjacent native overlap to preserve'}, *json.loads((ROOT/'references.json').read_text(encoding='utf-8')), {'path':(ROOT/'layout-only'/f'{tile_id}.png').as_posix(),'role':'larger tile LAYOUT-ONLY context, not final pixels'}]
    write(ROOT/'native'/f'{stem}.request.json',{'stem':stem,'tile':tile_id,'patch':patch_id,'coordinates':patch,'references':refs,'overlaps':sources,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
    progress=json.loads((ROOT/'progress.json').read_text(encoding='utf-8-sig'))
    progress.update({'status':'preparing_native','updatedAtUtc':now(),'currentTile':tile_id,'currentPatch':patch_id,'nextStep':'Inspect continuity guide, save full prompt, invoke builtin image_gen.'})
    write(ROOT/'progress.json',progress)
    print(json.dumps({'stem':stem,'context':str(context),'overlaps':sources}))

def pairqa(leftstem,rightstem):
    left=ROOT/'native'/f'{leftstem}.png'
    right=ROOT/'native'/f'{rightstem}.png'
    with Image.open(left) as a,Image.open(right) as b:
        result=Image.new('RGB',(690,1024))
        result.paste(a.crop((794,115,1139,1139)),(0,0))
        result.paste(b.crop((115,115,460,1139)),(345,0))
    path=ROOT/'qa'/f'{leftstem}__{rightstem}_hard-seam-native.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    result.save(path)
    write(Path(str(path)+'.derivation.json'),{'file':path.as_posix(),'sha256':sha(path),'role':'native 100% seam QA, not game tile','operation':'integer crops with hard cut at canonical core boundary; no resize, no blend, no painted pixels','seamX':345,'derivedFrom':[{'path':left.as_posix(),'sha256':sha(left),'sourceBox':[794,115,1139,1139],'targetBox':[0,0,345,1024]},{'path':right.as_posix(),'sha256':sha(right),'sourceBox':[115,115,460,1139],'targetBox':[345,0,690,1024]}]})
    print(str(path))

def minpairqa(leftstem,rightstem):
    helper=ROOT/'tools'/'seam_helpers.py'
    spec=importlib.util.spec_from_file_location('mechanical_min_seam',helper)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    left=ROOT/'native'/f'{leftstem}.png'
    right=ROOT/'native'/f'{rightstem}.png'
    a=np.array(Image.open(left).convert('RGB'))
    b=np.array(Image.open(right).convert('RGB'))
    seam=module._minimum_vertical_seam(a[:,-230:],b[:,:230])
    mask=np.arange(230)[None,:]>=seam[:,None]
    overlap=np.where(mask[:,:,None],b[:,:230],a[:,-230:])
    merged=np.concatenate([a[:,:-230],overlap,b[:,230:]],axis=1)
    path=ROOT/'qa'/f'{leftstem}__{rightstem}_minimum-hard-seam-native.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(merged[115:1139,794:1484]).save(path)
    write(Path(str(path)+'.derivation.json'),{'file':path.as_posix(),'sha256':sha(path),'role':'native 100% seam QA, not game tile','operation':'minimum squared RGB error seam; hard choice between source pixels; no resize, no feather, no drawing, no colour correction','overlapPixels':230,'seamXByRowInOverlap':seam.tolist(),'derivedFrom':[{'path':left.as_posix(),'sha256':sha(left)},{'path':right.as_posix(),'sha256':sha(right)}]})
    print(str(path))

if __name__=='__main__':
    if sys.argv[1]=='init': init()
    elif sys.argv[1]=='guide': guide(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='record': record(sys.argv[2])
    elif sys.argv[1]=='prepare': prepare(*sys.argv[2:])
    elif sys.argv[1]=='pairqa': pairqa(*sys.argv[2:])
    elif sys.argv[1]=='minpairqa': minpairqa(*sys.argv[2:])
