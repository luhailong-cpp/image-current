from pathlib import Path
p=Path(__file__).resolve().parent/'preview-template.html'
s=p.read_text(encoding='utf-8')
s=s.replace('.stage img{','.stage canvas{')
s=s.replace('<img alt="${g.id} 动作帧">','<canvas width="1024" height="1024" role="img" aria-label="${g.id} 动作帧"></canvas>')
s=s.replace("article.querySelector('.stage img').src=s.images[s.index].src;","const can=article.querySelector('canvas'),ctx=can.getContext('2d'),img=s.images[s.index];if(img.complete&&img.naturalWidth&&s.lastDrawn!==s.index){ctx.clearRect(0,0,1024,1024);ctx.drawImage(img,0,0,1024,1024);s.lastDrawn=s.index;}")
p.write_text(s,encoding='utf-8')
