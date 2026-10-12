from pathlib import Path
from PIL import Image, ImageChops
import json, hashlib, datetime, struct, zlib, binascii

ROOT = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009')
OUT = Path(__file__).resolve().parent
GROUP = OUT / 'group01-yamen-current-south-6tiles'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            h.update(b)
    return h.hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def save(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')

def capture():
    GROUP.mkdir(parents=True, exist_ok=True)
    ymanifest = ROOT/'accelerated-yamen-north/delivery-20261012-v1/delivery-manifest.json'
    nmanifest = ROOT/'northwest/verified-eleven-tiles-20261012/2f0946e391eb1655/delivery-summary.json'
    src = {}
    for t in read(ymanifest)['tiles']:
        src[t['tile']] = {'coordinate':t['tile'], 'file':t['candidate'], 'expectedSha256':t.get('candidateSHA256') or t.get('sha256'), 'adoptionManifest':str(ymanifest)}
    for t in read(nmanifest)['tiles']:
        if t['tile'] in ['r05_c04','r05_c05']:
            src[t['tile']] = {'coordinate':t['tile'], 'file':t['file'], 'expectedSha256':t.get('sha256'), 'adoptionManifest':str(nmanifest)}
    assert len(src) == 6
    for k,v in src.items():
        p = Path(v['file']).resolve()
        assert p.is_relative_to(ROOT.resolve())
        v['file'] = str(p)
        v['sha256'] = sha(p)
        if v['expectedSha256']:
            assert v['expectedSha256'] == v['sha256'], k
        with Image.open(p) as im:
            v['pixels'] = list(im.size)
            v['mode'] = im.mode
        assert v['pixels'] == [4096,4096] and v['mode'] == 'RGB'
        r,c = int(k[1:3]),int(k[5:7])
        v['worldBox'] = [(c-1)*4096,(r-1)*4096,c*4096,r*4096]
    baseline = ROOT/'accelerated-yamen-north/delivery-20261012-v1/boundary-review.json'
    bd = read(baseline)
    old_by_pair = {}
    for items in bd.values():
        if isinstance(items, list):
            for e in items:
                if isinstance(e,dict) and e.get('tile') in ['r04_c04','r04_c05'] and e.get('neighbor') in ['r05_c04','r05_c05'] and e.get('file'):
                    old_by_pair[(e['tile'],e['neighbor'],e['segment'])]=e
    crops=[]
    for c in [4,5]:
        a,b=f'r04_c{c:02}', f'r05_c{c:02}'
        with Image.open(src[a]['file']) as north, Image.open(src[b]['file']) as south:
            for s in range(4):
                x=s*1024
                crop=Image.new('RGB',(1024,320))
                crop.paste(north.crop((x,3936,x+1024,4096)),(0,0))
                crop.paste(south.crop((x,0,x+1024,160)),(0,160))
                p=GROUP/f'{a}--{b}-segment{s+1}-native100.png'
                crop.save(p)
                e={'file':str(p),'sha256':sha(p),'pixels':[1024,320],'nativePixelScale':1,'north':a,'south':b,'segment':s+1,'worldBox':[(c-1)*4096+x,16224,(c-1)*4096+x+1024,16544],'boundaryLocalY':160,'verdict':'PENDING_ACTUAL_VIEW'}
                old=old_by_pair.get((a,b,s+1))
                if old:
                    e['previousEvidence']=old
                    with Image.open(old['file']) as oi:
                        e['previousCropPixelIdentical']=oi.size==crop.size and ImageChops.difference(oi.convert('RGB'),crop).getbbox() is None
                    e['previousSouthBaselineStatus']='same visible crop' if e['previousCropPixelIdentical'] else 'STALE_FOR_CURRENT_ADOPTED_FULL_TILE'
                crops.append(e)
    junction=Image.new('RGB',(640,640))
    for k,box,xy in [
        ('r04_c04',(3776,3776,4096,4096),(0,0)),
        ('r04_c05',(0,3776,320,4096),(320,0)),
        ('r05_c04',(3776,0,4096,320),(0,320)),
        ('r05_c05',(0,0,320,320),(320,320))]:
        with Image.open(src[k]['file']) as im: junction.paste(im.crop(box),xy)
    p=GROUP/'x16384-y16384-fourway-native100.png'; junction.save(p)
    crops.append({'file':str(p),'sha256':sha(p),'pixels':[640,640],'worldBox':[16064,16064,16704,16704],'nativePixelScale':1,'junctionWorldXY':[16384,16384],'verdict':'PENDING_ACTUAL_VIEW'})
    control=[]
    for p in [ymanifest,nmanifest,baseline,ROOT/'production-contract.json',ROOT.parent/'acceleration-20261010/assignments.json',Path('D:/work/image/AGENTS.md')]:
        control.append({'file':str(p),'sha256':sha(p)})
    result={'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'6 existing 4K candidates, current adopted south-neighbor boundary review; no new art or repairs','groupCoordinates':sorted(src),'sourceFiles':list(src.values()),'controlSnapshots':control,'crops':crops,'formalAccepted':False,'wholeMapComplete':False,'assemblyAllowedAfterReview':False}
    save(GROUP/'manifest.json',result)
    print(json.dumps({'group':str(GROUP),'sourceCount':len(src),'cropCount':len(crops),'oldComparisons':[(e.get('north'),e.get('segment'),e.get('previousCropPixelIdentical')) for e in crops]},ensure_ascii=False))

def chunk(f, kind, data):
    f.write(struct.pack('>I',len(data))+kind+data+struct.pack('>I',binascii.crc32(kind+data)&0xffffffff))

def subjunctions():
    d=read(GROUP/'manifest.json')
    src={x['coordinate']:x for x in d['sourceFiles']}
    for c in [4,5]:
        a,b=f'r04_c{c:02}',f'r05_c{c:02}'
        with Image.open(src[a]['file']) as n, Image.open(src[b]['file']) as s:
            for x in [1024,2048,3072]:
                p=GROUP/f'{a}--{b}-junction-x{x}-native100.png'
                assert not p.exists()
                im=Image.new('RGB',(512,512))
                im.paste(n.crop((x-256,3840,x+256,4096)),(0,0))
                im.paste(s.crop((x-256,0,x+256,256)),(0,256))
                im.save(p)
                wx=(c-1)*4096+x
                d['crops'].append({'file':str(p),'sha256':sha(p),'pixels':[512,512],'nativePixelScale':1,'worldBox':[wx-256,16128,wx+256,16640],'junctionWorldXY':[wx,16384],'verdict':'PENDING_ACTUAL_VIEW'})
    save(GROUP/'manifest.json',d)
    print('Six subpatch/boundary junctions saved at 100%')

def verify_stream():
    d=read(GROUP/'manifest.json'); p=Path(d['assembly']['file'])
    actual=hashlib.sha256(); decoded=0; pending=bytearray(); inflater=zlib.decompressobj()
    rowbytes=8192*3
    with p.open('rb') as f:
        assert f.read(8)==b'\x89PNG\r\n\x1a\n'
        while True:
            n=struct.unpack('>I',f.read(4))[0]; kind=f.read(4); data=f.read(n); crc=f.read(4)
            assert struct.unpack('>I',crc)[0] == binascii.crc32(kind+data)&0xffffffff
            if kind==b'IDAT':
                pending.extend(inflater.decompress(data))
                while len(pending)>=rowbytes+1:
                    row=pending[:rowbytes+1]; del pending[:rowbytes+1]
                    assert row[0]==0
                    actual.update(row[1:]); decoded+=1
            if kind==b'IEND': break
    assert not pending and decoded==12288
    expected=hashlib.sha256()
    src={x['coordinate']:x for x in d['sourceFiles']}
    for r in [3,4,5]:
        with Image.open(src[f'r{r:02}_c04']['file']) as a, Image.open(src[f'r{r:02}_c05']['file']) as b:
            for y in range(4096):
                expected.update(a.crop((0,y,4096,y+1)).tobytes())
                expected.update(b.crop((0,y,4096,y+1)).tobytes())
    assert actual.hexdigest()==expected.hexdigest()
    d['assembly']['pixelIdentityVerification']={'passed':True,'decodedRows':decoded,'actualRasterSHA256':actual.hexdigest(),'sourceRasterSHA256':expected.hexdigest(),'method':'independent PNG CRC/filter-zero stream decode compared with exact source scanline concatenation; no full mosaic in memory'}
    save(GROUP/'manifest.json',d)
    print(json.dumps(d['assembly']['pixelIdentityVerification']))

def stream_assembly():
    d=read(GROUP/'manifest.json')
    assert d['assemblyAllowedAfterReview'] is True
    src={x['coordinate']:x for x in d['sourceFiles']}
    for v in src.values(): assert sha(v['file'])==v['sha256']
    p=GROUP/'yamen-current-south-6tiles-native-8192x12288.png'
    assert not p.exists(), 'Never overwrite a prior artifact'
    with p.open('wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        chunk(f,b'IHDR',struct.pack('>IIBBBBB',8192,12288,8,2,0,0,0))
        comp=zlib.compressobj(6)
        pending=bytearray()
        for r in [3,4,5]:
            with Image.open(src[f'r{r:02}_c04']['file']) as a, Image.open(src[f'r{r:02}_c05']['file']) as b:
                for y in range(4096):
                    raw=b'\x00'+a.crop((0,y,4096,y+1)).tobytes()+b.crop((0,y,4096,y+1)).tobytes()
                    pending.extend(comp.compress(raw))
                    if len(pending)>2**20:
                        chunk(f,b'IDAT',bytes(pending)); pending.clear()
        pending.extend(comp.flush())
        if pending: chunk(f,b'IDAT',bytes(pending))
        chunk(f,b'IEND',b'')
    # Pixel verification uses one row-pair at a time, never the complete map.
    # PIL verification below checks full PNG structure; output input pixel hashes
    # are independently reconstructed by row in verify_native_stream.py.
    with Image.open(p) as im:
        assert im.size==(8192,12288) and im.mode=='RGB'; im.verify()
    d['assembly']={'file':str(p),'sha256':sha(p),'pixels':[8192,12288],'worldBox':[12288,8192,20480,20480],'method':'integer-coordinate RGB concatenation; PNG row streaming; no overlap transform, interpolation, blur, blend, or new art','nativePixelScale':1,'sourceCoordinateRows':[[f'r{r:02}_c04',f'r{r:02}_c05'] for r in [3,4,5]],'formalMapAcceptance':False}
    save(GROUP/'manifest.json',d)
    # A clearly named downscaled preview is the only resampled result.
    preview=Image.new('RGB',(1536,2304))
    for k,v in src.items():
        r,c=int(k[1:3]),int(k[5:7])
        with Image.open(v['file']) as im: preview.paste(im.resize((768,768),Image.Resampling.LANCZOS),((c-4)*768,(r-3)*768))
    pp=GROUP/'PREVIEW-ONLY-downscaled-1536x2304.png'; preview.save(pp)
    d['preview']={'file':str(pp),'sha256':sha(pp),'pixels':[1536,2304],'previewOnly':True,'productionArt':False,'scale':0.1875}
    save(GROUP/'manifest.json',d)
    print(json.dumps(d['assembly'],ensure_ascii=False))

if __name__=='__main__':
    import sys
    {'capture':capture,'subjunctions':subjunctions,'assemble':stream_assembly,'verify':verify_stream}[sys.argv[1]]()
