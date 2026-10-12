"""Native-player video QA, raster only, no HTML/script page execution.
Encodes exact original frame durations at 200fps and 0.25x at 50fps.
Frames are held/repeated for duration, never interpolated.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"/"_video_vendor"))
import imageio_ffmpeg
FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
OUT=ROOT/"preview"/"video";OUT.mkdir(parents=True,exist_ok=True)
fontpath=Path("C:/Windows/Fonts/segoeui.ttf")
font=ImageFont.truetype(str(fontpath),22);small=ImageFont.truetype(str(fontpath),18)
TILE=384;CELL=428;W=1152;H=912;TOP=56;BG=(232,237,232)
groups=[]
for action,n,ms in [("hit",6,40),("attack",12,30),("cast",16,45)]:
 for direction in ("E","W"):
  tiles=[];hashes=[]
  for k in range(1,n+1):
   p=ROOT/"runtime"/action/direction/f"{k:02}.png";im=Image.open(p).convert("RGBA").resize((TILE,TILE),Image.Resampling.LANCZOS)
   tile=Image.new("RGB",(TILE,CELL),BG);tile.paste(im,(0,0),im)
   ImageDraw.Draw(tile).text((12,391),f"{action.upper()} {direction}    {k:02}/{n}    {ms} ms",fill=(20,53,42),font=small)
   tiles.append(tile);hashes.append({"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
  groups.append(dict(action=action,direction=direction,n=n,ms=ms,tiles=tiles,sources=hashes))
meta=[]
# Each segment is 2880ms original time, 4 full cast cycles / 8 attacks / 12 hits.
for name,fps,loops in [("normal",200,4),("slow",50,2)]:
 target=OUT/f"six-groups-{name}.mp4";frames=576*loops
 args=[FFMPEG,"-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","fast","-crf","15","-pix_fmt","yuv420p","-movflags","+faststart","-video_track_timescale","20000",str(target)]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 prev=None;raw=None
 for tick in range(frames):
  original_ms=tick*5
  indices=tuple((original_ms//g["ms"])%g["n"] for g in groups)
  if indices!=prev:
   frame=Image.new("RGB",(W,H),BG);dr=ImageDraw.Draw(frame)
   speed="1x ORIGINAL TIMING" if name=="normal" else "0.25x SLOW PLAYBACK"
   dr.text((16,12),f"SHUANGTUAN | {speed} | E front-right / W rear-left",font=font,fill=(20,53,42))
   # action columns, E upper row W lower row
   for gi,g in enumerate(groups):
    col=gi//2;row=gi%2;frame.paste(g["tiles"][indices[gi]],(col*TILE,TOP+row*CELL))
   raw=frame.tobytes();prev=indices
  proc.stdin.write(raw)
 proc.stdin.close();err=proc.stderr.read().decode(errors="replace");rc=proc.wait()
 if rc:raise RuntimeError(err)
 decode=subprocess.run([FFMPEG,"-v","error","-i",str(target),"-f","null","-"],capture_output=True,text=True)
 if decode.returncode:raise RuntimeError(decode.stderr)
 meta.append({"file":target.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"width":W,"height":H,"fps":fps,"encodedFrames":frames,"durationMs":frames*1000/fps,"speed":1 if name=="normal" else .25,"exactOriginalFrameDurations":True,"timeQuantumMs":5,"operation":"Raster-only native-player preview: hold existing source frames for their exact duration; neutral background and labels; no interpolation, mirroring or synthesized poses.","sources":[{k:g[k] for k in ("action","direction","sources")} for g in groups]})
report={"generatedAt":datetime.now(timezone.utc).isoformat(),"ffmpegVersion":imageio_ffmpeg.get_ffmpeg_version(),"encoderPackage":"imageio-ffmpeg==0.6.0","decodeCheck":"passed","files":meta}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"files":len(meta),"decodeCheck":"passed","paths":[x["file"] for x in meta]}))

