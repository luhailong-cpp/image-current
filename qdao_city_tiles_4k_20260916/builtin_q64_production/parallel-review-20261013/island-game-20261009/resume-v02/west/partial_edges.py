import json,hashlib
from pathlib import Path
from PIL import Image
O=Path(__file__).parent
j=json.loads((O/'source-delta.json').read_text(encoding='utf-8'))
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009')
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def n(p):return str(p).replace('\\','/')
tiles={t['tileId']:t for z in j['zones'].values() for t in z['tiles']}
def core(tile,r,c):
    s=next(s for s in tiles[tile]['selectedSources'] if (s['subrow'],s['subcolumn'])==(r,c))
    return Image.open(s['path']).convert('RGB').crop((115,115,1139,1139))
def adopted(tile):return Image.open(tiles[tile]['adopted4kCandidate']['path']).convert('RGB')
def pair(a,b,axis):
    im=Image.new('RGB',(512,1024) if axis=='vertical' else (1024,512))
    if axis=='vertical':im.paste(a.crop((768,0,1024,1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0))
    else:im.paste(a.crop((0,768,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,256)),(0,256))
    return im
specs=[
 ('r08c02-s01_04--r08c03-s01_01',core('r08_c02',1,4),adopted('r08_c03').crop((0,0,1024,1024)),'vertical',[8192,28672,8192,29696]),
 ('r08c02-s01_04--s02_04',core('r08_c02',1,4),core('r08_c02',2,4),'horizontal',[7168,29696,8192,29696]),
 ('r09c01-s01_04--r09c02-s01_01',core('r09_c01',1,4),adopted('r09_c02').crop((0,0,1024,1024)),'vertical',[4096,32768,4096,33792]),
 ('r09c06-s01_01--s01_02',core('r09_c06',1,1),core('r09_c06',1,2),'vertical',[21504,32768,21504,33792]),
 ('r09c06-s01_02--s01_03',core('r09_c06',1,2),core('r09_c06',1,3),'vertical',[22528,32768,22528,33792])]
out=[];d=O/'partial-core-edges';d.mkdir(exist_ok=True)
for name,a,b,axis,line in specs:
    cp=d/(name+'-100pct.png');im=pair(a,b,axis);im.save(cp);out.append({'id':name,'path':n(cp),'sha256':h(cp),'axis':axis,'globalSeamLine':line,'dimensions':list(im.size)})
board=Image.new('RGB',(2048,1024));v=[x for x in out if x['axis']=='vertical']
for i,x in enumerate(v):
    with Image.open(x['path']) as im:board.paste(im,(i*512,0))
bp=d/'four-vertical-edges-board-100pct.png';board.save(bp)
records=[]
for z,zz in j['zones'].items():
    for t in zz['tiles']:
        for s in t['selectedSources']:
            if s['change']=='unchanged':continue
            p=Path(s['path']+'.generation.json');g=json.loads(p.read_text(encoding='utf-8-sig'))
            r=s['subrow'];c=s['subcolumn'];tr=int(t['tileId'][1:3]);tc=int(t['tileId'][5:7]);x=(tc-1)*4096+(c-1)*1024;y=(tr-1)*4096+(r-1)*1024
            co=g.get('coordinates')
            cp=None
            if co is None:
                ip=P/z/'guides'/(Path(s['path']).stem+'.input.json')
                if ip.exists():
                    gg=json.loads(ip.read_text(encoding='utf-8-sig'));co=gg.get('coordinates',gg.get('coordinate'));cp={'path':n(ip),'sha256':h(ip),'keys':list(gg)}
            records.append({'tileId':t['tileId'],'subrow':r,'subcolumn':c,'sourcePath':s['path'],'sourceSha256':s['sha256'],'generationRecordPath':n(p),'generationRecordSha256':h(p),'recordImageHashMatches':g.get('sha256')==s['sha256'],'actualModel':g.get('actualModel'),'tool':g.get('tool'),'route':g.get('route'),'expectedCoreGlobalBox':[x,y,x+1024,y+1024],'recordedCoordinates':co,'coordinateInput':cp})
(O/'new-core-evidence.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'partial-edges.json').write_text(json.dumps({'edges':out,'board':n(bp),'boardPanels':[x['id'] for x in v]},ensure_ascii=False,indent=2),encoding='utf-8')
print('partial edges',len(out),'new record hash matches',sum(x['recordImageHashMatches'] for x in records),'/',len(records))
print('coordinates',[(x['tileId'],x['subrow'],x['subcolumn'],x['recordedCoordinates']) for x in records])
