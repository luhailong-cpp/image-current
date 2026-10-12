"""Exclusive west-sector native generation helper. Mechanical guides/provenance only."""
from pathlib import Path
import sys,json,shutil,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import production as p
INDEX=ROOT/'qa'/'expansion-west-worker-map.json'
TILES=[f'r{r:02}_c{c:02}' for r in range(9,15) for c in (1,2)]

def state():
    if INDEX.exists(): return p.load(INDEX)
    return {**{t:[[None]*4 for _ in range(4)] for t in TILES},'worker':'west','assignedTiles':TILES,'status':'generating','formalAccepted':False,'qa':{},'candidateArtifacts':{}}
def save(d):
    d['updatedAtUtc']=p.now();p.dump(INDEX,d)
def intersects(a,b):
    z=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
    return z if z[0]<z[2] and z[1]<z[3] else None
def prepare(r,c,sr,sc,attempt=1):
    tile=f'r{r:02}_c{c:02}'; assert tile in TILES
    co=p.coords(r,c,sr,sc);box=co['nativeGlobalBox'];stem=f'{tile}_s{sr:02}_{sc:02}_v{attempt:02}'
    reqpath=ROOT/'prompts'/f'{stem}.request.json'
    assert not reqpath.exists(),f'Existing request: {stem}'
    layout=ROOT/'guides'/f'{stem}.layout-only.png'
    with Image.open(p.REFS[0][0]) as im:
        im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(layout)
    p.dump(str(layout)+'.derivation.json',{'sha256':p.hashfile(layout),'operation':'Overview EXTENT for composition only; never final native contribution','source':p.metadata(*p.REFS[0]),'coordinates':co})
    canvas=Image.open(layout).convert('RGB'); sources=[p.metadata(layout,'layout-only base')]
    d=state();main=p.load(ROOT/'current-native-map.json')
    selected={k:v for k,v in main.items() if re.fullmatch(r'r\d{2}_c\d{2}',k)}
    selected.update({t:d[t] for t in TILES})
    def paste(path,gb,role,extra=None):
        clip=intersects(box,gb)
        if not clip:return
        crop=[clip[0]-gb[0],clip[1]-gb[1],clip[2]-gb[0],clip[3]-gb[1]];dest=[clip[0]-box[0],clip[1]-box[1]]
        with Image.open(path) as im: canvas.paste(im.convert('RGB').crop(crop),dest)
        sources.append({**p.metadata(path,role),'sourceGlobalBox':gb,'sourceCrop':crop,'destinationTopLeft':dest,**(extra or {})})
    for selected_tile,matrix in selected.items():
        for row in matrix:
            for neighbor in row:
                if not neighbor:continue
                np=ROOT/'native'/f'{neighbor}.png';rec=p.load(str(np)+'.generation.json')
                if intersects(box,rec['coordinates']['nativeGlobalBox']):paste(np,rec['coordinates']['nativeGlobalBox'],'adjacent native source at same global coordinates',{'generationRecord':str(np)+'.generation.json'})
    artifacts={**main.get('candidateArtifacts',{}),**d.get('candidateArtifacts',{})}
    for atile,art in artifacts.items():
        ar,ac=map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',atile).groups());gb=[(ac-1)*4096,(ar-1)*4096,ac*4096,ar*4096]
        if intersects(box,gb):paste(Path(art['path']),gb,'latest assembled native 4K border; priority over raw cores',{'derivation':art.get('record') or art.get('sourceReport')})
    guide=ROOT/'guides'/f'{stem}.native-overlap-guide.png';canvas.save(guide)
    p.dump(str(guide)+'.derivation.json',{'sha256':p.hashfile(guide),'operation':'Only same-coordinate native crop/paste onto layout guide; no native resampling/feather/warp/recolor','sources':sources,'coordinates':co,'finalArt':False})
    prompt=f'''Use case: stylized-concept. Native map patch production, not a standalone illustration.
Create exactly one square 1254 by 1254 native high-detail game-map patch for tile {tile}, subrow {sr}, subcolumn {sc}. Its global footprint is {box}; central [115,115,1139,1139] is the 1024-square core.
Image 1 is the coordinate edit target: its blurry area establishes exact composition, object silhouettes, projection and scale from the original overview. Its sharp neighbor strips are actual native pixels at identical global coordinates: preserve their placement, contours, material and lighting exactly and continue them into the newly rendered area. Do not enlarge or blur those existing native details. Fully redraw the blurry interior into crisp native detail without changing object footprints, object counts, orientation, height, negative space or terrain boundaries.
Images 2–4 are mandatory references. Image 2 alone fixes the whole-map layout. Image 3 is independent close-up material/style, never a coordinate crop. Image 4 establishes the approved Daoist Q painterly game-art style; ignore its interface or any night lighting.
Maintain the exact daylight isometric/oblique projection and consistent view scale. Match warm pale natural stone, carved Daoist architecture, festive red/gold details, greenery or water only where already present in the target. At this close zoom, preserve the actual area contents: do not add temples, characters, symbols, flowers, new buildings or decorative objects to sparse terrain. No text, UI, watermark, camera reframing, perspective shift, blur or invented border. Adjacent objects crossing image boundaries must continue through the boundary without being completed, mirrored or moved inward. Prioritize continuous shared-edge geometry and crisp natural brush material at the original pixel scale. Render the entire 1254-square patch including its halo.'''
    refs=[p.metadata(guide,'coordinate edit target with exact adjacent native border strips')]+[p.metadata(*r) for r in p.REFS]
    pp=ROOT/'prompts'/f'{stem}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
    p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
    req={'stem':stem,'tool':'image_gen.imagegen','prompt':prompt,'promptPath':str(pp),'promptSha256':p.hashfile(pp),'refs':[x['path'] for x in refs],'references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
    p.dump(reqpath,req);d['currentRequest']=stem;save(d);print(json.dumps(req,ensure_ascii=True))
def ingest(stem,source):
    dst=ROOT/'native'/f'{stem}.png';assert not dst.exists();src=Path(source);shutil.copy2(src,dst)
    with Image.open(dst) as im:size=im.size;fmt=im.format
    req=p.load(ROOT/'prompts'/f'{stem}.request.json')
    rec={'file':str(dst),'sha256':p.hashfile(dst),'width':size[0],'height':size[1],'format':fmt,'generatedAt':p.now(),'tool':'image_gen.imagegen','route':'builtin','sourceToolPath':str(src),'configSnapshot':p.CONFIG,'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host exposes no actual model/quality evidence.','submittedParameters':req['submittedParameters'],'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'coordinates':req['coordinates'],'evidence':[{'path':str(ROOT/'receipts'/f'{stem}.tool.json'),'type':'tool receipt'}],'status':'awaiting_visual_QA','nativeSizeMatchesPlan':list(size)==[1254,1254]}
    p.dump(str(dst)+'.generation.json',rec)
    d=state();d['lastGenerated']=stem;d['generationCount']=d.get('generationCount',0)+1;save(d)
    print(json.dumps({'path':str(dst),'sha256':rec['sha256'],'dimensions':size}))
def select(stem,note):
    co=p.load(ROOT/'prompts'/f'{stem}.coordinates.json');d=state();assert co['tile'] in TILES
    rec=p.load(ROOT/'native'/f'{stem}.png.generation.json');assert rec['nativeSizeMatchesPlan']
    d[co['tile']][co['subrow']-1][co['subcolumn']-1]=stem
    d['qa'][stem]={'reviewedAtUtc':p.now(),'nativeVisualStatus':'candidate_usable','note':note,'internalTileSeamsPassed':False,'externalTileSeamsPassed':False}
    d['selectedNativeCount']=sum(bool(x) for t in TILES for row in d[t] for x in row);save(d)
    print(json.dumps({'selected':stem,'selectedNativeCount':d['selectedNativeCount']}))
def annotate(stem,note):
    assert not (ROOT/'native'/f'{stem}.png').exists()
    reqpath=ROOT/'prompts'/f'{stem}.request.json';req=p.load(reqpath)
    promptpath=Path(req['promptPath']);promptpath.write_text(req['prompt']+'\nPatch-specific constraint: '+note,encoding='utf-8')
    req['prompt']=promptpath.read_text(encoding='utf-8');req['promptSha256']=p.hashfile(promptpath);p.dump(reqpath,req)
    print(json.dumps(req,ensure_ascii=True))
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='prepare':prepare(*map(int,sys.argv[2:]))
    elif cmd=='ingest':ingest(*sys.argv[2:])
    elif cmd=='select':select(*sys.argv[2:])
    elif cmd=='annotate':annotate(*sys.argv[2:])
