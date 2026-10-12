import json
from pathlib import Path

BASE = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
MAPS = ['main-city-game-20261009', 'fishing-village-game-20261009', 'island-game-20261009']
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def walk(o, prefix=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, prefix + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, prefix + f'[{i}]')
    else:
        yield prefix, o
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    wanted = sys.argv[1] if len(sys.argv)>1 else None
    for m in MAPS:
        for z in sorted((BASE/m).iterdir()):
            p=z/'progress.json'
            if not p.is_file() or (wanted and wanted not in str(z)): continue
            d=read(p)
            small={k:v for k,v in d.items() if not isinstance(v,(dict,list)) and (('Count' in k and 'Native' not in k and 'native' not in k) or k in ['status','updatedAt','updatedAtUtc','totalTiles','tileCount','assignment','target4kCount','assignedTileCount'])}
            paths={k:v for k,v in walk(d) if isinstance(v,str) and v.lower().endswith(('.png','.json','.zip')) and not any(x in k.lower() for x in ['nativefiles','generationrecord','error','old','historical','firstpostrestoration','worker','gate','ack','config','prompt','seed','capacity','pipeline','cleanup','handoff'])}
            print(json.dumps({'map':m,'zone':z.name,'counts':small,'activePaths':paths},ensure_ascii=False))
