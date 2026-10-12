"""Tile-isolated production wrapper with all-direction native/candidate context.
Does not select a model, resize native art, write shared config, or accept tiles.
"""
from pathlib import Path
import argparse, importlib.util, json
from PIL import Image

ZONE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('zone_production',ZONE/'production.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def setup(tile_id):
    reservations=ZONE/'reserved-tiles-20261013.json'
    if reservations.exists() and tile_id in json.loads(reservations.read_text(encoding='utf-8-sig')).get('reservedTiles',[]):
        raise ValueError('Tile transferred to independent owner; this production lane must not write it')
    p.TILE=p.tile_path(tile_id)
    p.update=lambda *a,**k:None
    original_save=p.save
    def tile_save(path,data):
        path=Path(path).resolve()
        if path==(ZONE/'model-verification.json').resolve():return
        if not path.is_relative_to(p.TILE):raise ValueError('Non-tile write refused')
        original_save(path,data)
    p.save=tile_save
def neighbors(patch):
    if len(patch)!=3 or patch[0]!='p' or patch[1] not in '1234' or patch[2] not in '1234':raise ValueError('Expected p11..p44')
    tr,tc,_,_=p.tile_coordinates(p.TILE.name)
    pr,pc=int(patch[1]),int(patch[2])
    # E/S first, then W/N: legacy top-left priority is retained.
    for direction,dr,dc,box,pos in [('east',0,1,(0,0,230,1254),(1024,0)),('south',1,0,(0,0,1254,230),(0,1024)),('west',0,-1,(1024,0,1254,1254),(0,0)),('north',-1,0,(0,1024,1254,1254),(0,0))]:
        r,c=pr+dr,pc+dc; rr,cc=tr,tc
        if r<1:rr-=1;r=4
        if r>4:rr+=1;r=1
        if c<1:cc-=1;c=4
        if c>4:cc+=1;c=1
        try:tile=p.tile_path(f'r{rr:02}_c{cc:02}')
        except ValueError:continue
        yield direction,tile,f'p{r}{c}',box,pos
def context(patch,required,dry=False):
    tile=p.TILE
    request=tile/'prompts'/f'{patch}.request.json'
    output=tile/'layout-only'/f'{patch}-mixed-context.png'
    if request.exists() and not dry:raise ValueError('Do not rewrite context already used by saved request')
    coord=next(x for x in json.loads((tile/'coordinates.json').read_text(encoding='utf-8'))['patches'] if x['id']==patch)
    guide=Path(coord['guide'])
    assert p.sha(guide)==coord['guideSha256']
    im=Image.open(guide).convert('RGB')
    sources=[{'file':str(guide),'sha256':p.sha(guide),'role':'layout-only blurred geometry, not game art'}]
    seen=set()
    adjacent_tiles=[]
    for direction,other,np,box,pos in neighbors(patch):
        src=p.selected_native(other,np)
        if not src.exists():
            if direction in required:raise ValueError(f'Required {direction} native missing: {src}')
            continue
        record=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8-sig'))
        assert p.sha(src)==record['sha256']
        native=Image.open(src).convert('RGB')
        assert native.size==(1254,1254)
        im.paste(native.crop(box),pos)
        sources.append({'file':str(src),'sha256':record['sha256'],'role':f'actual {direction} native context','tile':other.name,'patch':np,'crop':list(box),'paste':list(pos)})
        seen.add(direction)
        if other!=tile and other not in adjacent_tiles:adjacent_tiles.append(other)
    # Repaired 4096 candidates are authoritative for pixels inside their core.
    wx,wy,wr,wb=coord['contextWorldBox']
    for other in adjacent_tiles:
        progress_path=other/'tile-progress.json'
        progress=json.loads(progress_path.read_text(encoding='utf-8-sig')) if progress_path.exists() else {}
        selected_candidate=progress.get('candidate')
        f=Path(selected_candidate) if selected_candidate else other/'candidates'/f'{other.name}.candidate.png'
        assert f.resolve().is_relative_to(other.resolve()), 'Candidate must stay inside its tile'
        if not f.exists():continue
        _,_,ox,oy=p.tile_coordinates(other.name)
        x0,y0,x1,y1=max(wx,ox),max(wy,oy),min(wr,ox+4096),min(wb,oy+4096)
        if x1<=x0 or y1<=y0:continue
        h=p.sha(f)
        final=Image.open(f).convert('RGB')
        assert final.size==(4096,4096)
        source_box=[x0-ox,y0-oy,x1-ox,y1-oy];dest=[x0-wx,y0-wy]
        im.paste(final.crop(source_box),tuple(dest))
        assert p.sha(f)==h,'Neighbor candidate changed during context creation'
        sources.append({'file':str(f),'sha256':h,'role':'current repaired candidate core pixels; does not claim formal acceptance','crop':source_box,'paste':dest})
    if not set(required)<=seen:raise ValueError('Required neighbor not available in zone')
    if dry:
        print(json.dumps({'tile':tile.name,'patch':patch,'availableDirections':sorted(seen),'sources':sources,'noWrites':True},ensure_ascii=False))
        return
    im.save(output)
    p.save(Path(str(output)+'.generation.json'),{'file':str(output),'sha256':p.sha(output),'createdAt':p.now(),'assetRole':'mixed guide only; layout blur repainted, native overlap guides continuity','derivedFrom':sources,'operation':{'type':'integer source crops/pastes, no resampling','outputPixels':[1254,1254],'requiredDirections':required,'candidateCoreOverrides':True}})
    print(str(output))
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--tile',required=True)
    ap.add_argument('--require',nargs='*',choices=['north','south','east','west'],default=[])
    ap.add_argument('command',choices=['prepare','context','check-context','ingest'])
    ap.add_argument('operands',nargs='*')
    a=ap.parse_args();setup(a.tile)
    if a.command=='prepare':
        if (p.TILE/'coordinates.json').exists():raise ValueError('Existing tile must not be prepared again')
        p.prepare()
    elif a.command in ['context','check-context']:context(a.operands[0],a.require,a.command=='check-context')
    elif a.command=='ingest':p.ingest(*a.operands)
