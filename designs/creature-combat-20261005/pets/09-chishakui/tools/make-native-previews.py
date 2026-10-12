"""MJPEG AVI review files using Pillow, exact rational frame timing, no new poses."""
from pathlib import Path
import struct, io, json, hashlib
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def chunk(tag,data):
    return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)%2 else b'')
def list_chunk(tag,data): return chunk(b'LIST',tag+data)
def encode_avi(frames,ms,width,height):
    # dwScale/dwRate retains exact 30, 40 and 45 ms durations, unlike GIF.
    n=len(frames); maximum=max(map(len,frames))
    avih=struct.pack('<14I',ms*1000,int(maximum*1000/ms),0,0x10,n,0,1,maximum,width,height,0,0,0,0)
    strh=struct.pack('<4s4sIHHIIIIIIIIhhhh',b'vids',b'MJPG',0,0,0,0,ms,1000,0,n,maximum,0xffffffff,0,0,0,width,height)
    strf=struct.pack('<IiiHH4sIiiII',40,width,height,1,24,b'MJPG',width*height*3,0,0,0,0)
    hdrl=list_chunk(b'hdrl',chunk(b'avih',avih)+list_chunk(b'strl',chunk(b'strh',strh)+chunk(b'strf',strf)))
    movi=bytearray();index=bytearray();offset=4
    for data in frames:
        encoded=chunk(b'00dc',data)
        index.extend(struct.pack('<4sIII',b'00dc',0x10,offset,len(data)))
        movi.extend(encoded);offset+=len(encoded)
    return chunk(b'RIFF',b'AVI '+hdrl+list_chunk(b'movi',movi)+chunk(b'idx1',index))

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    output=[]
    for group in manifest['groups']:
        for label,mult in [('normal',1),('slow025',4)]:
            frames=[]
            for i,file in enumerate(group['files']):
                canvas=Image.new('RGB',(512,544),(47,60,61));draw=ImageDraw.Draw(canvas)
                for y in range(0,512,32):
                    for x in range(0,512,32):
                        if (x//32+y//32)%2:draw.rectangle((x,y,x+31,y+31),fill=(60,73,74))
                with Image.open(ROOT/file) as im:
                    im=im.convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);canvas.paste(im,(0,0),im)
                draw.text((12,521),f"{group['action']} {group['direction']} | {'1x' if mult==1 else '0.25x'} | {i+1:02d}/{group['count']} | {group['durationMs']*mult}ms",fill=(245,240,215))
                buf=io.BytesIO();canvas.save(buf,format='JPEG',quality=92,subsampling=0);frames.append(buf.getvalue())
            target=ROOT/'preview'/f"{group['action']}-{group['direction']}-{label}.avi"
            target.write_bytes(encode_avi(frames*4,group['durationMs']*mult,512,544))
            output.append({'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':512,'height':544,'codec':'MJPG','scale':group['durationMs']*mult,'rate':1000,'frameCount':len(frames)*4,'sourceFramesPerLoop':len(frames),'loops':4,'durationMs':len(frames)*4*group['durationMs']*mult,'sources':[{'file':f,'sha256':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in group['files']]})
    (ROOT/'preview/native-video-sources.json').write_text(json.dumps({'format':'AVI MJPEG','purpose':'Supplementary local media-player review; opaque checkerboard video is not a runtime game asset.','operation':'Each runtime canvas uniformly scaled to512, composited on checkerboard, frame/time label added, encoded JPEG. Four exact source loops; no interpolation and no new animation poses.','generatedImageModel':None,'isNewAIGeneration':False,'files':output},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'nativeVideos':len(output),'totalBytes':sum((ROOT/x['file']).stat().st_size for x in output)}))
if __name__=='__main__':main()
