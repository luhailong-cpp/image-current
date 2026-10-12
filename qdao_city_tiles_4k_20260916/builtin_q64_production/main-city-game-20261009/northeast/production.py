from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import argparse, json, hashlib, re, shutil

ZONE = Path(__file__).resolve().parent
ROOT = ZONE.parent
CONTRACT = json.loads((ROOT/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG_PATH = Path('D:/work/image/config/image-generation.json')
if not CONFIG_PATH.exists():
    CONFIG_PATH = ZONE/'generation-route-resume-20261012.json'
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8-sig'))
TILE = ZONE/'r05_c13'
ZONE_SPEC = next(zone for zone in CONTRACT['zones'] if zone['id'] == 'northeast')
TILE_SIZE = CONTRACT['formalTilePixels'][0]
PYTHON = 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def tile_coordinates(tile_id):
    if not re.fullmatch(r'r\d{2}_c\d{2}', tile_id):
        raise ValueError('Use a tile ID such as r05_c14')
    row, col = int(tile_id[1:3]), int(tile_id[5:7])
    if not (ZONE_SPEC['rows'][0] <= row <= ZONE_SPEC['rows'][1] and
            ZONE_SPEC['columns'][0] <= col <= ZONE_SPEC['columns'][1]):
        raise ValueError('Tile is outside northeast ownership')
    return row, col, (col-1)*TILE_SIZE, (row-1)*TILE_SIZE
def tile_path(tile_id):
    tile_coordinates(tile_id)
    path = (ZONE/tile_id).resolve()
    if path.parent != ZONE.resolve():
        raise ValueError('Tile must be directly inside northeast')
    return path
def selected_native(tile, patch):
    tile = tile_path(tile.name)
    selection_file = tile/'selected-native.json'
    selection = json.loads(selection_file.read_text(encoding='utf-8-sig')) if selection_file.exists() else {}
    filename = selection.get(patch, f'{patch}.png')
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise ValueError('Selected native must be a filename inside its tile')
    native_dir = (tile/'native').resolve()
    if native_dir.parent != tile:
        raise ValueError('Native directory must stay inside its tile')
    src = (native_dir/filename).resolve()
    if src.parent != native_dir:
        raise ValueError('Selected native must stay inside its tile')
    return src
def context_neighbors(patch):
    if not re.fullmatch(r'p[1-4][1-4]', patch):
        raise ValueError('Context needs a patch ID from p11 through p44')
    r, c = int(patch[1]), int(patch[2])
    row, col, _, _ = tile_coordinates(TILE.name)
    neighbors = []
    if c > 1:
        neighbors.append((TILE, f'p{r}{c-1}', (1024,0,1254,1254), (0,0)))
    elif col > ZONE_SPEC['columns'][0]:
        neighbors.append((tile_path(f'r{row:02}_c{col-1:02}'), f'p{r}4', (1024,0,1254,1254), (0,0)))
    if r > 1:
        neighbors.append((TILE, f'p{r-1}{c}', (0,1024,1254,1254), (0,0)))
    elif row > ZONE_SPEC['rows'][0]:
        neighbors.append((tile_path(f'r{row-1:02}_c{col:02}'), f'p4{c}', (0,1024,1254,1254), (0,0)))
    return neighbors
def has_complete_candidate(tile):
    # An exported complete tile counts once, even when several QA signatures exist.
    manifests = list((tile/'qa').glob('**/assembly.json')) + list((tile/'candidates').glob('**/assembly.json'))
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding='utf-8-sig'))
            if (data.get('tile') != tile.name or data.get('complete4kCandidateCount', 0) < 1 or
                    data.get('validSelectedNativeCount') != 16 or data.get('coverageFraction') != 1 or
                    data.get('opaquePixelCount') != TILE_SIZE*TILE_SIZE or
                    data.get('missingSelectedIds') or data.get('invalidSelectedSources')):
                continue
            for artifact in data.get('artifacts', []):
                if artifact.get('kind') != 'complete-4k-candidate-unreviewed':
                    continue
                path = Path(artifact['file'])
                path = (path if path.is_absolute() else tile/path).resolve()
                if not path.is_relative_to(tile.resolve()) or not path.is_file():
                    continue
                with Image.open(path) as candidate:
                    candidate.load()
                    if (candidate.format != 'PNG' or candidate.size != (TILE_SIZE,TILE_SIZE) or
                            candidate.mode not in ('RGB','RGBA') or
                            (candidate.mode == 'RGBA' and candidate.getextrema()[3] != (255,255))):
                        continue
                if artifact.get('sha256') != sha(path):
                    continue
                return True
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return False
def update(next_step=None):
    tiles=[]
    for path in ZONE.iterdir():
        if path.is_dir() and re.fullmatch(r'r\d{2}_c\d{2}', path.name):
            try: tiles.append(tile_path(path.name))
            except ValueError: continue
    record_counts={tile.name:len(list(tile.glob('native/*.generation.json'))) for tile in tiles}
    _, _, ox, oy = tile_coordinates(TILE.name)
    save(ZONE/'progress.json', {'zone':'northeast','updatedAt':now(),'status':'native_patch_production','firstTile':'r05_c13','currentTile':TILE.name,'tileOrigin':[ox,oy],'zoneRows':ZONE_SPEC['rows'],'zoneColumns':ZONE_SPEC['columns'],'generatedNativeCount':sum(record_counts.values()),'complete4kCandidateCount':sum(has_complete_candidate(tile) for tile in tiles),'formalAcceptedCount':0,'currentTileNativeCount':record_counts.get(TILE.name,0),'nextStep':next_step or f'Continue overlapping native patches in {TILE.name}; no formal tile accepted.','actualModel':None,'actualQuality':None,'clientMappingValidated':False,'capacity5000Validated':False})
def prepare():
    for name in ['layout-only','native','prompts','receipts','qa','candidates']:(TILE/name).mkdir(parents=True,exist_ok=True)
    src=Path(CONTRACT['layoutReference']); im=Image.open(src).convert('RGB'); w,h=im.size
    _, _, ox, oy = tile_coordinates(TILE.name)
    canvas_w, canvas_h = CONTRACT['artCanvasPixels']
    mapping={'tile':TILE.name,'canvasPixels':[canvas_w,canvas_h],'coreWorldBox':[ox,oy,ox+TILE_SIZE,oy+TILE_SIZE],'layoutSource':str(src),'layoutSha256':sha(src),'layoutNativePixels':[w,h],'layoutCropBox':[ox*w/canvas_w,oy*h/canvas_h,(ox+TILE_SIZE)*w/canvas_w,(oy+TILE_SIZE)*h/canvas_h],'patches':[]}
    for r in range(1,5):
        for c in range(1,5):
            x,y=ox+(c-1)*1024,oy+(r-1)*1024
            box=[x-115,y-115,x+1139,y+1139]
            bbox=[box[0]*w/canvas_w,box[1]*h/canvas_h,box[2]*w/canvas_w,box[3]*h/canvas_h]
            p=TILE/'layout-only'/f'p{r}{c}-layout-only.png'
            im.transform((1254,1254),Image.Transform.EXTENT,bbox,Image.Resampling.BICUBIC).save(p)
            item={'id':f'p{r}{c}','coreWorldBox':[x,y,x+1024,y+1024],'contextWorldBox':box,'layoutSourceBox':bbox,'coreCrop':[115,115,1139,1139],'guide':str(p),'guideSha256':sha(p)}
            mapping['patches'].append(item)
            save(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'createdAt':now(),'assetRole':'layout-only; never game art','derivedFrom':[{'file':str(src),'sha256':sha(src)}],'operation':{'type':'fractional layout crop enlarged for geometry guidance only','sourceBox':bbox,'outputPixels':[1254,1254],'resample':'bicubic'}})
    guide=im.transform((1024,1024),Image.Transform.EXTENT,mapping['layoutCropBox'],Image.Resampling.BICUBIC)
    draw=ImageDraw.Draw(guide)
    for v in [256,512,768]:draw.line([(v,0),(v,1023)],fill='#ff00ff',width=2);draw.line([(0,v),(1023,v)],fill='#ff00ff',width=2)
    draw.text((8,8),f'LAYOUT ONLY / {TILE.name} / NOT GAME PIXELS',fill='black',stroke_width=2,stroke_fill='white')
    guide.save(TILE/'layout-only'/'tile-grid-layout-only.png')
    save(TILE/'coordinates.json',mapping)
    save(ZONE/'model-verification.json',{'checkedAt':now(),'configSnapshot':CONFIG,'sameBatchSettings':True,'officialChecks':[{'url':'https://developers.openai.com/api/docs/models','finding':'GPT-Image-2.5 Sunburst listed as most capable image model'},{'url':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','finding':'low medium high xhigh max auto supported'},{'url':'https://openai.com/index/introducing-chatgpt-images-2-5/','finding':'Images 2.5 available in Codex'}],'builtinToolSchemaFields':['prompt','referenced_image_paths','num_last_images_to_include','transparent_background'],'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in tool does not expose model/quality selectors or a result until generation; target is not proof of actual model.'})
    update('Generate p11 from its layout-only guide with all three approved references attached.')
    print(json.dumps(mapping,ensure_ascii=False))
def ingest(patch, source):
    dest=TILE/'native'/f'{patch}.png'
    if dest.exists():raise RuntimeError('Existing native file must not be overwritten')
    shutil.copy2(source,dest)
    with Image.open(dest) as im: width,height=im.size; fmt=im.format; im.verify()
    payload=json.loads((TILE/'prompts'/f'{patch}.request.json').read_text(encoding='utf-8'))
    coordinates=json.loads((TILE/'coordinates.json').read_text(encoding='utf-8'))
    coord=next(p for p in coordinates['patches'] if p['id']==patch.split('-')[0])
    refs=[]
    for i,p in enumerate(payload['referenced_image_paths']):refs.append({'file':p,'sha256':sha(p),'role':payload['referenceRoles'][i]})
    record={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'nativeSize':[width,height],'width':width,'height':height,'format':fmt,'tool':'image_gen','route':'builtin','sourceOutputPath':source,'configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号和质量；配置目标与提示词不代表实际版本。','prompt':str(TILE/'prompts'/f'{patch}.prompt.txt'),'request':str(TILE/'prompts'/f'{patch}.request.json'),'references':refs,'evidence':str(TILE/'receipts'/f'{patch}.receipt.json'),'coordinates':coord,'dimensionsMatch1254Plan':(width,height)==(1254,1254),'resized':False,'status':'native-candidate-awaiting-seam-review'}
    save(Path(str(dest)+'.generation.json'),record)
    update(f'Inspect {patch} native pixels and produce next overlapping patch.')
    print(json.dumps({'file':str(dest),'nativeSize':[width,height],'sha256':sha(dest)}))
def context(patch):
    neighbors = context_neighbors(patch)
    guide=TILE/'layout-only'/f'{patch}-layout-only.png'
    im=Image.open(guide).convert('RGB')
    sources=[{'file':str(guide),'sha256':sha(guide),'role':'layout-only background; must be regenerated'}]
    for neighbor_tile, neighbor_patch, box, pos in neighbors:
        src=selected_native(neighbor_tile, neighbor_patch)
        if src.exists():
            neighbor=Image.open(src).convert('RGB')
            if neighbor.size!=(1254,1254):raise RuntimeError('Native geometry mismatch')
            im.paste(neighbor.crop(box),pos)
            sources.append({'file':str(src),'sha256':sha(src),'role':'locked native overlap','tile':neighbor_tile.name,'patch':neighbor_patch,'crop':box,'paste':pos})
    dest=TILE/'layout-only'/f'{patch}-mixed-context.png'
    im.save(dest)
    save(Path(str(dest)+'.generation.json'),{'file':str(dest),'sha256':sha(dest),'createdAt':now(),'assetRole':'mixed guide only; blurred region is layout-only, sharp strips are locked native neighbors','derivedFrom':sources,'operation':{'type':'integer crop and paste without resampling','outputPixels':[1254,1254]}})
    print(str(dest))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Northeast native tile production; defaults to r05_c13.')
    parser.add_argument('command', choices=['prepare','ingest','context'])
    parser.add_argument('operands', nargs='*')
    parser.add_argument('--tile', default='r05_c13')
    args=parser.parse_args()
    if len(args.operands) != {'prepare':0,'ingest':2,'context':1}[args.command]:
        parser.error('Use prepare, context PATCH, or ingest PATCH SOURCE, optionally followed by --tile TILE')
    try:
        TILE=tile_path(args.tile)
    except ValueError as error:
        parser.error(str(error))
    if args.command=='prepare':prepare()
    elif args.command=='ingest':ingest(*args.operands)
    elif args.command=='context':context(*args.operands)
