import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone
from types import SimpleNamespace
from PIL import Image
import batch_pipeline as bp

B = Path(__file__).resolve().parents[1]
SCOPES = ('r02_c03', 'r01_c03')
def now(): return datetime.now(timezone.utc).isoformat()
def rec(p):
    p=Path(p); return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def write(p,x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(x,f,ensure_ascii=False,indent=2)
    return rec(p)
def load_state():
    ps=list(B.glob('c03-progress-v*.json'))
    p=max(ps,key=lambda p:int(re.search(r'-v(\d+)',p.name)[1]))
    return json.loads(p.read_text(encoding='utf-8-sig')),int(re.search(r'-v(\d+)',p.name)[1])
def approve(stem,notes,allowed,layout_hold=False):
    assert stem[:7] in SCOPES
    raw=B/'native'/f'{stem}.png'; meta=json.loads(Path(str(raw)+'.generation.json').read_text(encoding='utf-8-sig'))
    assert meta['nativeGeometryEligible'] and not meta['requiresReferenceRecheck']
    with Image.open(raw) as im: assert im.size==(1254,1254)
    folder=B/'qa/c03'/stem
    previous=list(folder.glob('quick-review-v*.json')) if folder.exists() else []
    qv=max([int(re.search(r'-v(\d+)',x.name)[1]) for x in previous]+[0])+1
    p=folder/f'quick-review-v{qv:02d}.json'
    q=write(p,{'checkedAtUtc':now(),'stem':stem,'raw':rec(raw),'dimensions':[1254,1254],'layoutQuickPass':allowed and not layout_hold,'adjacentQuickPass':allowed,'propagationAllowed':allowed,'localRepairPending':layout_hold,'notes':notes,'formalAccepted':False})
    s,v=load_state(); s['selected']=[x for x in s['selected'] if x['stem'][:14]!=stem[:14]]
    if allowed: s['selected'].append({'stem':stem,'raw':rec(raw),'qa':q})
    s.update(updatedAtUtc=now(),selectedCount=len(s['selected']),formalAccepted=False,status='active_native_production')
    return write(B/f'c03-progress-v{v+1:02d}.json',s)
def prepare(tile,sr,sc,attempt,edit_source=None,edit_instruction=None,local_instruction=None):
    assert tile in SCOPES
    s,v=load_state(); selected={x['stem'][:14]:x for x in s['selected']}
    args=SimpleNamespace(tile=tile,subrow=sr,subcol=sc,attempt=attempt,geometry_references_only=True,no_neighbor_contact=True)
    directions=[]
    for d,dr,dc in [('south',1,0),('west',0,-1),('east',0,1),('north',-1,0)]:
        rr,cc=sr+dr,sc+dc; tr=int(tile[1:3]); tc=int(tile[5:7])
        if rr>4: tr+=1; rr=1
        if rr<1: tr-=1; rr=4
        if cc>4: tc+=1; cc=1
        if cc<1: tc-=1; cc=4
        coord=f'r{tr:02d}_c{tc:02d}_s{rr:02d}_{cc:02d}'
        x=selected.get(coord)
        p=Path(x['raw']['path']) if x else None
        evidence=None
        if tr==3 and tc==3 and rr==1:
            p=B/'anchors/v01'/f'r03_c03_s01_{cc:02d}_current-derived-v01.png'
            evidence=p.with_suffix('.derivation.json')
        setattr(args,d,str(p) if p else None); setattr(args,d+'_record',str(evidence) if evidence else None)
        if p: directions.append(d)
    assert directions, 'Need a stable adjacent native reference'
    core,gbox=bp.boxes(tile,sr,sc)
    stem=f'{tile}_s{sr:02d}_{sc:02d}_a{attempt:02d}'
    rules={'south':'SOUTH top 230 pixels align to target bottom 230 pixels at y=1024', 'west':'WEST right 230 pixels align to target left 230 pixels at x=0','east':'EAST left 230 pixels align to target right 230 pixels at x=1024','north':'NORTH bottom 230 pixels align to target top 230 pixels at y=0'}
    prompt=f'''Generate ONE native opaque PNG exactly 1254x1254 for game-map patch {stem}. This is a tiny magnified crop of the existing island, NOT a whole scene. Image 1 is the exact target composition guide. Global target box {gbox}, central 1024 core {core}.
Only render the local objects, planes and silhouettes visible in Image 1 at exactly the same camera, magnification, positions, relative sizes and angles. Follow only the close-up architectural, sea, rock and foliage fragments visible in the target guide. Keep their scale and avoid inventing a complete scene.
The sharp border strips in Image 1 are actual native neighbor pixels. Preserve their geometry and colors and continue them seamlessly into the remaining target area: {'; '.join(rules[d] for d in directions)}. Never copy the entire adjacent image. Never shift the shared strips, invent a boundary, or change scale. Do not create a straight strip seam where native meets blurry guide. Redraw the blurry overview interior into fine original hand-painted detail, not an enlargement. Use the sharp neighboring art for native brush quality, rounded Daoist Q shapes, bright daylight, blue ceramics, warm orange/gold trim, ivory walls, natural grey stone and turquoise sea only where actually present. Do not invent objects, ornament, paving, buildings, vegetation, lanterns or shore absent from the guide. No whole building or courtyard unless the guide actually contains one. No text, UI, people, watermark, frame or padding. All objects that run off-frame must remain cropped. Opaque 1254x1254, actual builtin included image route only.'''
    if local_instruction: prompt += '\nLOCAL MATERIAL/GEOMETRY: '+local_instruction
    if edit_source:
        target=Path(edit_source).resolve(); assert target.parent==B/'native' and target.name[:14]==stem[:14]
        prompt=f'''Use case: precise-object-edit. Edit Image 1, the existing 1254x1254 native map patch {stem}; Image 2 is a coordinate geometry guide with current exact neighboring border strips. Return one opaque 1254x1254 PNG. Preserve camera, overall layout, pixel scale, brush quality, colors and all unaffected objects. Repair only this issue: {edit_instruction}. The sharp strips in Image 2 are immutable native neighbor geometry: {'; '.join(rules[d] for d in directions)}. Match them exactly and continue their lines and materials naturally into the edited transition. Remove straight paste boundaries; do not introduce extra roof ridges or ornaments. Keep all crop silhouettes and continuous blue ceramic tile cadence. No complete buildings, new props, text, UI, people, frame, watermark or padding. Native details throughout; no resizing.'''
        original_save=bp.save_json
        def edit_save(path,value):
            if str(path).endswith('.references.json'):
                value['inputs'].insert(0,{**rec(target),**bp.dimensions(target),'role':'same-coordinate AI edit target; preserve all unaffected art'})
                value['imageGenReferencedImagePaths'].insert(0,target.as_posix())
            return original_save(path,value)
        bp.save_json=edit_save
    custom=B/'prompts'/f'{stem}.custom.txt'
    with custom.open('x',encoding='utf-8') as f:f.write(prompt)
    args.prompt_file=str(custom)
    return bp.prepare(args)
def comparisons(stem):
    inp=json.loads((B/'guides'/f'{stem}.input.json').read_text(encoding='utf-8-sig'))
    with Image.open(B/'native'/f'{stem}.png') as raw,Image.open(inp['guide']['path']) as guide:
        for n in inp['neighbors']:
            d=n['direction']; box={'south':(0,1024,1254,1254),'north':(0,0,1254,230),'west':(0,0,230,1254),'east':(1024,0,1254,1254)}[d]
            aa=raw.crop(box).convert('RGB'); bb=guide.crop(box).convert('RGB')
            w,h=aa.size; out=Image.new('RGB',(w*2,h));out.paste(bb,(0,0));out.paste(aa,(w,0))
            p=B/'qa/c03'/stem/f'{d}-native-comparison-v01.png';p.parent.mkdir(parents=True,exist_ok=True)
            assert not p.exists();out.save(p); print(p.as_posix())
p=argparse.ArgumentParser();p.add_argument('command',choices=['approve','hold','prepare','comparisons']);p.add_argument('--stem');p.add_argument('--notes');p.add_argument('--tile');p.add_argument('--sr',type=int);p.add_argument('--sc',type=int);p.add_argument('--attempt',type=int,default=1);p.add_argument('--layout-hold',action='store_true');p.add_argument('--edit-source');p.add_argument('--edit-instruction');p.add_argument('--local-instruction');a=p.parse_args()
if a.command in ('approve','hold'):print(json.dumps(approve(a.stem,a.notes,a.command=='approve',a.layout_hold),ensure_ascii=False))
elif a.command=='prepare':print(json.dumps(prepare(a.tile,a.sr,a.sc,a.attempt,a.edit_source,a.edit_instruction,a.local_instruction),ensure_ascii=False))
else:comparisons(a.stem)
