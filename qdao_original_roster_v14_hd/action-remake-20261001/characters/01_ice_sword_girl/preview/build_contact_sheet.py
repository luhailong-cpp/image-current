from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CHAR = HERE.parent
SELECTION = json.loads((CHAR/'review/run-E-selection.json').read_text(encoding='utf-8-sig'))
NAMES = [Path(frame['path']).stem if frame else None for frame in SELECTION['frames']]
CELL = 380
FONT = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
SMALL = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
full = Image.new('RGB',(CELL*4,(CELL+44)*4),(40,54,65))
feet = Image.new('RGB',(CELL*4,220*4),(40,54,65))
records=[]
for i,name in enumerate(NAMES):
    if name is None:
        continue
    path=CHAR/'drafts/run/E'/f'{name}.png'
    image=Image.open(path).convert('RGBA')
    x=(i%4)*CELL;y=(i//4)*(CELL+44)
    thumb=image.resize((CELL,CELL),Image.Resampling.LANCZOS)
    full.paste(thumb,(x,y+44),thumb)
    draw=ImageDraw.Draw(full)
    draw.text((x+12,y+6),f'E{name}  {image.width}x{image.height}',font=FONT,fill='white')
    draw.line((x,y+44+CELL*0.953,x+CELL,y+44+CELL*0.953),fill=(232,169,81),width=1)
    draw.line((x+CELL*.5-5,y+44+CELL*.953,x+CELL*.5+5,y+44+CELL*.953),fill='white',width=2)
    fy=(i//4)*220
    # Fixed identical source window for lower-body diagnosis; never used as a sprite.
    box=(int(image.width*.20),int(image.height*.68),int(image.width*.90),image.height)
    lower=image.crop(box).resize((CELL,174),Image.Resampling.LANCZOS)
    feet.paste(lower,(x,fy+44),lower)
    draw=ImageDraw.Draw(feet)
    draw.text((x+12,fy+6),f'E{name}',font=FONT,fill='white')
    line_y=fy+44+(0.953-.68)/.32*174
    draw.line((x,line_y,x+CELL,line_y),fill=(232,169,81),width=1)
    records.append({'path':str(path.relative_to(CHAR)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':list(image.size)})
full.save(HERE/'current-contact-sheet.png')
feet.save(HERE/'current-feet-sheet.png')
(HERE/'current-contact-sheet.sources.json').write_text(json.dumps({'purpose':'visual diagnostic only; full unchanged source canvas shown at identical display scale; not sprite exports','selectionSha256':hashlib.sha256((CHAR/'review/run-E-selection.json').read_bytes()).hexdigest(),'rootCandidateNormalized':[.5,.953],'rootCandidate1024':[512,975.872],'farFootGroundY1024':970.752,'referenceSoleEvidence':'E02 visible shoe bottom near 1195/1254; y95.3% is provisional, not formal acceptance','images':records},indent=2),encoding='utf-8')
print('Created two diagnostic sheets from current selection; retained null slots.')
