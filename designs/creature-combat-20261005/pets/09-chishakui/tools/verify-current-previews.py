"""Offline derived-preview checks. Does not assert GUI playback or artistic continuity."""
from pathlib import Path
from PIL import Image
import json,hashlib,struct,io,datetime
ROOT=Path(__file__).resolve().parents[1]
def chunks(data,start,end):
    while start+8<=end:
        tag=data[start:start+4];n=struct.unpack_from('<I',data,start+4)[0]
        assert start+8+n<=end
        yield tag,start+8,n
        start+=8+n+(n%2)
    assert start==end
def main():
    m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));checks=[]
    for g in m['groups']:
        expected=[]
        for f in g['files']:
            with Image.open(ROOT/f) as im:expected.append(im.convert('RGBA').resize((512,512),Image.Resampling.LANCZOS).tobytes())
        for label,mult in [('normal',1),('slow025',4)]:
            p=ROOT/'preview'/f"{g['action']}-{g['direction']}-{label}.png"
            with Image.open(p) as im:
                assert im.n_frames==len(expected);times=[]
                for i,raw in enumerate(expected):
                    im.seek(i);assert im.convert('RGBA').tobytes()==raw,(str(p),i)
                    assert im.info['duration']==g['durationMs']*mult
                    times.append(im.info['duration'])
            checks.append({'file':p.relative_to(ROOT).as_posix(),'frames':len(expected),'pixelIdenticalToUniformlyResizedRuntime':True,'durationMs':times,'passed':True})
    proof={'reviewDate':'2026-10-08','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Offline APNG decode and exact RGBA comparison against uniformly resized current runtime. No browser or media player opened.','checks':checks,'sourceFrames':[{'file':e['file'],'sha256':e['sha256']} for e in m['frames']],'technicalPassed':True,'visualPlaybackVerified':False}
    (ROOT/'records/preview-pixel-audit-20261008.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    sources=json.loads((ROOT/'preview/native-video-sources.json').read_text(encoding='utf-8'));videos=[]
    for f in sources['files']:
        p=ROOT/f['file'];data=p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==f['sha256']
        for source in f['sources']:assert hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest()==source['sha256']
        assert data[:4]==b'RIFF' and data[8:12]==b'AVI ' and struct.unpack_from('<I',data,4)[0]+8==len(data)
        lists={data[off:off+4]:(off+4,n-4) for tag,off,n in chunks(data,12,len(data)) if tag==b'LIST'}
        off,n=lists[b'hdrl'];headers=list(chunks(data,off,off+n))
        av=next((off,n) for tag,off,n in headers if tag==b'avih');vals=struct.unpack_from('<14I',data,av[0]);assert vals[0]==f['scale']*1000 and vals[4]==f['frameCount']
        st=next((off,n) for tag,off,n in headers if tag==b'LIST' and data[off:off+4]==b'strl')
        stream=list(chunks(data,st[0]+4,st[0]+st[1]));off,n=next((off,n) for tag,off,n in stream if tag==b'strh')
        values=struct.unpack_from('<4s4sIHHIIIIIIIIhhhh',data,off);assert values[6]==f['scale'] and values[7]==f['rate'] and values[9]==f['frameCount']
        off,n=lists[b'movi'];frames=list(chunks(data,off,off+n));assert len(frames)==f['frameCount'];pixels=[]
        for tag,pos,size in frames:
            assert tag==b'00dc'
            with Image.open(io.BytesIO(data[pos:pos+size])) as im:
                im.load();assert im.size==(512,544);pixels.append(hashlib.sha256(im.convert('RGB').tobytes()).hexdigest())
        per=f['sourceFramesPerLoop'];assert all(pixels[i]==pixels[i%per] for i in range(len(pixels)))
        videos.append({'file':f['file'],'sha256':f['sha256'],'framesDecoded':len(frames),'frameDurationMs':f['scale'],'durationMs':f['durationMs'],'passed':True})
    audit=ROOT/'records/native-media-audit-20261008.json'
    doc=json.loads(audit.read_text(encoding='utf-8')) if audit.exists() else {}
    doc.update({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':videos,'technicalPassed':True,'scope':'Current files after cast W08–10 repair. Historical native-player attempt described separately; no new playback verification.'})
    audit.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'APNGTracks':len(checks),'APNGFramesCompared':sum(x['frames'] for x in checks),'AVIFiles':len(videos),'AVIFramesDecoded':sum(x['framesDecoded'] for x in videos),'visualPlaybackVerified':False}))
if __name__=='__main__':main()
