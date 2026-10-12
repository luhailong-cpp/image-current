"""Read only the user-provided local video through a localhost review player."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import re
SOURCE=Path('C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
HTML='''<!doctype html><meta charset="utf-8"><title>06动作方向参考视频</title><style>body{font:16px system-ui;background:#202936;color:white}video{width:100%;max-width:1280px}button,select{font:inherit;padding:8px}#zoom{width:512px;height:440px;border:1px solid #888;image-rendering:auto}</style><h1>用户动作方向参考 · 原视频</h1><p>只观察动作轴线、连续性和接地。小人物/遮挡位置不能证明每帧脚掌细节。</p><video id="video" src="/reference.mp4" controls muted playsinline></video><p><button id="play">播放/暂停</button> <button id="back">前一帧</button> <button id="next">后一帧</button> 速度 <select id="speed"><option value="1">正常</option><option value="0.25">四分之一</option></select> <span id="time"></span></p><canvas id="zoom" width="512" height="440"></canvas><p>中央角色区域连续放大（只读视频裁切显示）</p><script>const v=document.querySelector('video'),c=document.querySelector('canvas'),ctx=c.getContext('2d');document.querySelector('#play').onclick=()=>v.paused?v.play():v.pause();document.querySelector('#speed').onchange=e=>v.playbackRate=Number(e.target.value);document.querySelector('#back').onclick=()=>{v.pause();v.currentTime=Math.max(0,v.currentTime-1/24)};document.querySelector('#next').onclick=()=>{v.pause();v.currentTime=Math.min(v.duration,v.currentTime+1/24)};function draw(){if(v.readyState>=2)ctx.drawImage(v,570,190,145,150,0,0,512,440);document.querySelector('#time').textContent=v.currentTime.toFixed(3)+' / '+(v.duration||0).toFixed(3)+' 秒';requestAnimationFrame(draw)};draw();</script>'''.encode('utf-8')
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/' or self.path.startswith('/index.html'):
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(HTML)));self.end_headers();self.wfile.write(HTML);return
  if self.path!='/reference.mp4':self.send_error(404);return
  size=SOURCE.stat().st_size;start=0;end=size-1;part=False
  if value:=self.headers.get('Range'):
   m=re.fullmatch(r'bytes=(\d+)-(\d*)',value)
   if m:start=int(m[1]);end=min(int(m[2]) if m[2] else end,end);part=True
  self.send_response(206 if part else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if part:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with SOURCE.open('rb') as f:
    f.seek(start);left=end-start+1
    while left:
     data=f.read(min(65536,left))
     if not data:break
     self.wfile.write(data);left-=len(data)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*args):pass
print('Reference player http://127.0.0.1:18609',flush=True)
HTTPServer(('127.0.0.1',18609),Handler).serve_forever()
