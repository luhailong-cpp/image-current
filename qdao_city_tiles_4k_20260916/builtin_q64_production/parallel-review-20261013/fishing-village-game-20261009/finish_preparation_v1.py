from review_tools_v1 import *

def sheet(paths,dest,cols):
    ims=[Image.open(p).convert('RGB') for p in paths]
    w=max(i.width for i in ims); h=max(i.height for i in ims)
    out=Image.new('RGB',(w*cols,(h+28)*((len(ims)+cols-1)//cols)),(26,26,26)); draw=ImageDraw.Draw(out)
    assert out.width<=1536 and out.height<=1536
    for n,(p,im) in enumerate(zip(paths,ims)):
        x=(n%cols)*w; y=(n//cols)*(h+28)
        out.paste(im,(x,y+28)); draw.text((x+4,y+7),p.stem,fill='white'); im.close()
    assert not dest.exists(); out.save(dest)
    write(str(dest)+'.trace.json',dict(classification='100 percent native contact sheet; labels outside art, no resampling',inputs=[record(p) for p in paths],output=record(dest)))

for d in sorted(OUT.glob('G0[234]-*')):
    for prefix,chunk,cols in [('V',3,3),('H',2,1),('VJ',6,3),('HJ',6,3)]:
        paths=sorted(p for p in d.glob(prefix+'??-100pct.png'))
        for n in range(0,len(paths),chunk): sheet(paths[n:n+chunk],d/f'{prefix}-native-sheet-v2-{n//chunk+1:02d}.png',cols=min(cols,len(paths[n:n+chunk])))

d=OUT/'G04-southwest-southeast-r10-r11-v1'
traces=[read(p) for p in d.glob('V??-100pct.png.trace.json')]
sources={s['file']:s for t in traces for s in t['sources']}
write(d/'manifest-v1.json',dict(created_at_utc=datetime.now(timezone.utc).isoformat(),group='G04',source_coordinate_count=4,sources=list(sources.values()),selection_records=[record(SRC/'southwest/current-tile-ledger.json'),record(SRC/'southeast/delivery-index-20261012.json')],segments=[str(p) for p in sorted(d.glob('V??-100pct.png'))],junctions=[str(p) for p in sorted(d.glob('VJ??-100pct.png'))],native_scale=True,review_status='unreviewed',formal_accepted=False,stale_if='Any source or adopted selection changes',preparation_note='All crops succeeded; corrected the metadata index filename after initial manifest write failed. Source pixels were not regenerated or overwritten.'))
print('Native review sheets and all manifests ready.')
