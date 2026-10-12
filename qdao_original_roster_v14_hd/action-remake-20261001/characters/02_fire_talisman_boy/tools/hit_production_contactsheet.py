from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,argparse,sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('action',choices=['hit','run'])
parser.add_argument('direction',choices=['W','E','S','SW'])
args=parser.parse_args()
inv=json.loads((root/'inventory-hit.json').read_text(encoding='utf-8-sig'))
frames=sorted([f for f in inv['frames'] if f['action']==args.action and f['direction']==args.direction],key=lambda f:f['frame'])
expected=6 if args.action=='hit' else 16
if len(frames)!=expected:raise SystemExit('只对完整真实帧组生成联系表；当前帧不足')
cols=3 if expected==6 else 4
rows=(expected+cols-1)//cols
tile=384 if expected==6 else 320
header=36
font_path=Path('C:/Windows/Fonts/msyh.ttc')
font=ImageFont.truetype(str(font_path),16) if font_path.exists() else ImageFont.load_default()
sheet=Image.new('RGB',(cols*tile,rows*(tile+header)),(232,234,235))
draw=ImageDraw.Draw(sheet)
derived=[]
for i,f in enumerate(frames):
    x=(i%cols)*tile;y=(i//cols)*(tile+header)
    draw.text((x+12,y+8),f"{args.action} {args.direction} / {f['frame']:02d} / {'40' if args.action=='hit' else '75'} ms",font=font,fill=(36,42,46))
    for yy in range(0,tile,24):
        for xx in range(0,tile,24):
            c=(240,242,243) if (xx//24+yy//24)%2 else (218,222,225)
            draw.rectangle((x+xx,y+header+yy,min(x+xx+23,x+tile-1),min(y+header+yy+23,y+header+tile-1)),fill=c)
    ax=x+int(512/1024*tile);ay=y+header+int(920/1024*tile)
    draw.line((ax-6,ay,ax+6,ay),fill=(0,124,147),width=1)
    draw.line((ax,ay-6,ax,ay+6),fill=(0,124,147),width=1)
    p=root/f['path']
    with Image.open(p) as im:
        im=im.convert('RGBA').resize((tile,tile),Image.Resampling.LANCZOS)
        sheet.paste(im,(x,y+header),im)
    derived.append({'file':f['path'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':f['source_record']})
work='hit' if args.action=='hit' else 'run-'+args.direction
out=root/'work'/work/f'{args.action}-{args.direction}-contact-sheet.png'
out.parent.mkdir(parents=True,exist_ok=True)
sheet.save(out)
record={'file':str(out.relative_to(root)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'createdAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'operation':'整幅1024画布统一缩小制作逐帧联系表；没有逐帧裁剪、缩放角色包围盒、移动人物或最低脚对齐；青色十字仅表示声明根点','derivedFrom':derived,'modelGeneration':False,'purpose':'逐帧审核预览，不计入正式帧数量'}
(root/'records'/f'{args.action}-{args.direction}-contact-sheet.derived.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
