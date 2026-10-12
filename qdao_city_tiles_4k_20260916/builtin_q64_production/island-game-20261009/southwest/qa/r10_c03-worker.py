"""Local r10_c03 worker: mechanical coordinate guides and records only."""
import sys,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import production as p
INDEX=ROOT/'qa'/'r10_c03-worker-map.json'
TILE='r10_c03'
def state():
    return p.load(INDEX) if INDEX.exists() else {TILE:[[None]*4 for _ in range(4)],'tile':TILE,'status':'in_progress','formalAccepted':False,'generationCount':0,'qa':{}}
def save(d):
    d['updatedAtUtc']=p.now(); p.dump(INDEX,d)
def prepare(sr,sc,attempt=1):
    co=p.coords(10,3,sr,sc); stem=f'{TILE}_s{sr:02}_{sc:02}_v{attempt:02}'
    layout=ROOT/'guides'/f'{stem}.layout-only.png'
    with Image.open(p.REFS[0][0]) as im: im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(layout)
    p.dump(str(layout)+'.derivation.json',{'file':str(layout),'sha256':p.hashfile(layout),'operation':'Layout-only overview EXTENT; not final native contribution','source':p.metadata(*p.REFS[0]),'coordinates':co})
    p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
    canvas=Image.open(layout).convert('RGB'); sources=[p.metadata(layout,'layout-only base')]
    selected=state()[TILE]; neighbors=[]
    if sr==1:
        above=p.load(ROOT/'current-native-map.json')['r09_c03'][3][sc-1]; neighbors.append(above)
    else: neighbors.append(selected[sr-2][sc-1])
    if sc>1: neighbors.append(selected[sr-1][sc-2])
    box=co['nativeGlobalBox']
    for n in neighbors:
        assert n
        np=ROOT/'native'/f'{n}.png'; rec=p.load(str(np)+'.generation.json'); nb=rec['coordinates']['nativeGlobalBox']
        ib=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
        crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]]; dest=[ib[0]-box[0],ib[1]-box[1]]
        canvas.paste(Image.open(np).crop(crop),dest); sources.append({**p.metadata(np,'native neighbor at same global coordinates'),'sourceCrop':crop,'destinationTopLeft':dest})
    if sr==1:
        art=p.load(ROOT/'current-native-map.json')['candidateArtifacts']['r09_c03']; final=Path(art['path'])
        # Exact final tile border replaces raw candidate material for all overlapping official pixels.
        fb=[8192,32768,12288,36864]; ib=[max(box[0],fb[0]),max(box[1],fb[1]),min(box[2],fb[2]),min(box[3],fb[3])]
        crop=[ib[0]-fb[0],ib[1]-fb[1],ib[2]-fb[0],ib[3]-fb[1]]; dest=[ib[0]-box[0],ib[1]-box[1]]
        canvas.paste(Image.open(final).crop(crop),dest)
        sources.append({**p.metadata(final,'actual final r09_c03 border constraint; priority over raw subpatch'),'sourceCrop':crop,'destinationTopLeft':dest,'derivation':art['record']})
    out=ROOT/'guides'/f'{stem}.native-overlap-guide.png'; canvas.save(out)
    p.dump(str(out)+'.derivation.json',{'file':str(out),'sha256':p.hashfile(out),'operation':'Mechanical native same-coordinate paste over layout-only guide; no native resampling','sources':sources,'coordinates':co})
    refs=[p.metadata(out,'coordinate target; adjacent exact native overlaps; blurry remainder layout only'),p.metadata(ROOT/'native'/f'{neighbors[0]}.png','above native context; actual final border takes priority in guide')]+[p.metadata(*r) for r in p.REFS]
    req={'tool':'image_gen.imagegen','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
    request=ROOT/'prompts'/f'{stem}.request.json'
    assert not request.exists()
    p.dump(request,req)
    print(json.dumps({'stem':stem,'guide':str(out),'refs':[r['path'] for r in refs],'coordinates':co}))
def ingest(stem,source):
    src=Path(source); dst=ROOT/'native'/f'{stem}.png'; assert not dst.exists()
    shutil.copy2(src,dst)
    with Image.open(dst) as im: size=im.size; fmt=im.format
    req=p.load(ROOT/'prompts'/f'{stem}.request.json')
    record={'file':str(dst),'sha256':p.hashfile(dst),'generatedAt':p.now(),'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':p.CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host provides no model/quality selectors or returned version evidence.','prompt':str(ROOT/'prompts'/f'{stem}.prompt.txt'),'references':req['references'],'sourceToolPath':str(src),'evidence':[{'path':str(ROOT/'receipts'/f'{stem}.tool.json'),'type':'tool receipt'}],'coordinates':req['coordinates'],'status':'awaiting_visual_QA','nativeSizeMatchesPlan':list(size)==[1254,1254]}
    p.dump(str(dst)+'.generation.json',record)
    d=state(); d['generationCount']+=1; d['lastGenerated']=stem; save(d)
    print(json.dumps({'file':str(dst),'dimensions':size,'sha256':record['sha256']}))
def check(stem):
    co=p.load(ROOT/'prompts'/f'{stem}.coordinates.json'); sr,sc=co['subrow'],co['subcolumn']; selected=state()[TILE]
    outputs=[]
    if sr>1:
        name=f'{stem}-top-native100'; p.seamcheck(selected[sr-2][sc-1],stem,'vertical',name); outputs.append(str(ROOT/'qa'/f'{name}.png'))
    else:
        final=Path(p.load(ROOT/'current-native-map.json')['candidateArtifacts']['r09_c03']['path']); above=Image.open(final); cur=Image.open(ROOT/'native'/f'{stem}.png')
        x=(sc-1)*1024; canvas=Image.new('RGB',(1024,600)); canvas.paste(above.crop((x,3796,x+1024,4096)),(0,0));canvas.paste(cur.crop((115,115,1139,415)),(0,300))
        out=ROOT/'qa'/f'{stem}-actual-r09_c03-top-native100.png';canvas.save(out)
        p.dump(str(out)+'.derivation.json',{'operation':'native same-coordinate crops across formal tile border','sources':[p.metadata(final,'actual above final tile'),p.metadata(ROOT/'native'/f'{stem}.png','new below patch')],'sourceCrops':[[x,3796,x+1024,4096],[115,115,1139,415]],'seamAt':300});outputs.append(str(out))
    if sc>1:
        name=f'{stem}-left-native100'; p.seamcheck(selected[sr-1][sc-2],stem,'horizontal',name);outputs.append(str(ROOT/'qa'/f'{name}.png'))
    print(json.dumps({'checks':outputs}))
def select(stem,note):
    co=p.load(ROOT/'prompts'/f'{stem}.coordinates.json'); d=state();d[TILE][co['subrow']-1][co['subcolumn']-1]=stem;d['qa'][stem]={'visualNote':note,'status':'candidate','reviewedAtUtc':p.now()};save(d)
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='prepare': prepare(*map(int,sys.argv[2:]))
    elif cmd=='ingest': ingest(*sys.argv[2:])
    elif cmd=='check': check(sys.argv[2])
    elif cmd=='select': select(*sys.argv[2:])

