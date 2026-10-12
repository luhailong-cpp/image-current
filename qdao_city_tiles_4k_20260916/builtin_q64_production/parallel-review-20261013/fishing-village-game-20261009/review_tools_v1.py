"""Read-only native pixel review. All outputs are confined to this directory."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, struct, zlib
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
SRC = OUT.parent.parent / 'fishing-village-game-20261009'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p, data):
    p = Path(p).resolve()
    assert p.is_relative_to(OUT)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def record(p, **extra):
    p = Path(p)
    r = dict(file=str(p), sha256=sha(p), bytes=p.stat().st_size, **extra)
    if p.suffix.lower() == '.png':
        with Image.open(p) as im: r.update(dimensions=list(im.size), mode=im.mode)
    return r

def origin(tile):
    return ((int(tile[5:7])-1)*4096, (int(tile[1:3])-1)*4096)

def source(tile, p, role='current_selected_candidate', local_box=None, crop_box=None):
    x,y = origin(tile)
    return record(p, tile=tile, role=role, global_box=(local_box or [x,y,x+4096,y+4096]), source_crop_box=crop_box)

def crop_global(sources, box, dest):
    """Exact integer crop/paste only; raises for any uncovered pixels."""
    x0,y0,x1,y1=box
    im=Image.new('RGB',(x1-x0,y1-y0))
    mask=Image.new('1',im.size)
    used=[]
    for s in sources:
        a,b,c,d=s['global_box']
        l,t,r,bt=max(a,x0),max(b,y0),min(c,x1),min(d,y1)
        if l>=r or t>=bt: continue
        offset=(s.get('source_crop_box') or [0,0])[0:2]
        with Image.open(s['file']) as src:
            cut=src.crop((l-a+offset[0],t-b+offset[1],r-a+offset[0],bt-b+offset[1])).convert('RGB')
            im.paste(cut,(l-x0,t-y0))
            mask.paste(1,(l-x0,t-y0,r-x0,bt-y0))
        used.append(s)
    assert mask.getextrema()==(1,1), f'Uncovered pixels in {box}'
    dest=Path(dest).resolve(); assert dest.is_relative_to(OUT)
    dest.parent.mkdir(parents=True,exist_ok=True); im.save(dest)
    write(str(dest)+'.trace.json',dict(operation='unscaled integer crop and paste; no blending, repaint or resampling',global_box=box,output=record(dest),sources=used,review_status='unreviewed',stale_if='Any listed source hash changes'))
    return dest

def png_chunk(f, kind, data):
    f.write(struct.pack('>I',len(data))); f.write(kind); f.write(data)
    f.write(struct.pack('>I',zlib.crc32(kind+data)&0xffffffff))

def stitch_stream(sources, rows, cols, dest):
    """At most one row of native tiles decoded; output preserves all RGB pixels."""
    dest=Path(dest).resolve(); assert dest.is_relative_to(OUT)
    dest.parent.mkdir(parents=True,exist_ok=True)
    width,height=len(cols)*4096,len(rows)*4096
    lookup={s['tile']:s for s in sources}
    with dest.open('wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n'); png_chunk(f,b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))
        comp=zlib.compressobj(3)
        for r in rows:
            images=[]
            for c in cols:
                s=lookup[f'r{r:02d}_c{c:02d}']
                im=Image.open(s['file']); assert im.size==(4096,4096)
                images.append(im.convert('RGB')); im.close()
            for y in range(4096):
                scan=b'\x00'+b''.join(im.crop((0,y,4096,y+1)).tobytes() for im in images)
                data=comp.compress(scan)
                if data: png_chunk(f,b'IDAT',data)
            for im in images: im.close()
        png_chunk(f,b'IDAT',comp.flush()); png_chunk(f,b'IEND',b'')
    write(str(dest)+'.trace.json',dict(created_at_utc=datetime.now(timezone.utc).isoformat(),operation='unscaled integer row/column assembly of existing 4096 native-composed candidates; no AI call',rows=rows,columns=cols,output=record(dest),sources=sources,formal_accepted=False,stale_if='Any source hash or adopted selection changes'))
    return dest

def preview(sources, box, dest, scale=1/4):
    x0,y0,x1,y1=box
    im=Image.new('RGB',(round((x1-x0)*scale),round((y1-y0)*scale)))
    for s in sources:
        x,y,_,_=s['global_box']
        with Image.open(s['file']) as tile:
            p=tile.convert('RGB'); p.thumbnail((round(4096*scale),round(4096*scale)),Image.Resampling.LANCZOS)
            im.paste(p,(round((x-x0)*scale),round((y-y0)*scale)))
    draw=ImageDraw.Draw(im); draw.rectangle((0,0,im.width,34),fill=(30,45,50)); draw.text((8,9),'DOWNSAMPLED PREVIEW - candidate only - not native QA',fill='white')
    dest=Path(dest).resolve(); assert dest.is_relative_to(OUT); dest.parent.mkdir(parents=True,exist_ok=True); im.save(dest)
    write(str(dest)+'.trace.json',dict(classification='clearly labelled downsampled preview only; never native detail evidence',scale=scale,output=record(dest),sources=sources))
