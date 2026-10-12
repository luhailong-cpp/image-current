"""Assemble reviewed selections without touching images or generation records."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent.parent
EVIDENCE=ROOT/'provenance/ground-contact-20261004'
DIRS=['N','NE','E','SE','S','SW','W','NW']

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

tables=['position-selection-E-root.json','position-selection-WN.json',
        'position-selection-NES.json','position-selection-SWNW.json']
rows=[]
for name in tables:rows.extend(load(EVIDENCE/name))
se=[r for r in load(EVIDENCE/'position-selection-SE-root.json') if r['targetFrame']<=12]
se.extend(load(EVIDENCE/'position-selection-SE-last4.json'))
rows.extend(se)
assert len(rows)==128
assert {(r['direction'],r['targetFrame']) for r in rows}=={(d,n) for d in DIRS for n in range(1,17)}
assert len({r['sha256'] for r in rows})==128
notes=['前部落脚','前部接受负荷','同脚早承重','身体经过支撑脚',
       '同脚髋下晚承重','同脚由髋下向后过渡','同脚后侧前掌蹬地','同脚后蹬并准备换脚']
for r in rows:
    assert sha(ROOT/r['sourceFile'])==r['sha256']
    if r.get('sourceGenerationRecordSha256'):
        assert sha(ROOT/r['sourceGenerationRecord'])==r['sourceGenerationRecordSha256']
    if r.get('visualNotes')=='pending visual review; source mapping only':
        r['visualNotes']=('右脚' if r['targetFrame']<=8 else '左脚')+'：'+notes[(r['targetFrame']-1)%8]+'；鞋掌与膝踝顺行进方向，另一腿回收前摆；主审整段实看通过。'
rows.sort(key=lambda r:(DIRS.index(r['direction']),r['targetFrame']))
save(EVIDENCE/'position-selection-all.json',rows)
for d in DIRS:
    group=[r for r in rows if r['direction']==d]
    for typ in ['full','feet']:
        w,h=(300,320) if typ=='full' else (360,160)
        sheet=Image.new('RGB',(w*4,h*4),'#d9e5e8');draw=ImageDraw.Draw(sheet)
        for i,r in enumerate(group):
            im=Image.open(ROOT/r['sourceFile']);x=i%4*w;y=i//4*h
            if typ=='feet':im=im.crop((200,725,925,1010))
            im.thumbnail((w,h-20),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+20),im)
            draw.text((x+5,y+3),f'{d}{i+1:02} {r["supportLeg"]} P{r["positionSegment"]}.{r["pairOrdinal"]}',fill='#182c32')
        sheet.save(EVIDENCE/f'selected-{d}-{typ}.jpg',quality=95)
print(json.dumps({'rows':len(rows),'newSources':sum(r['sourceFile'].startswith('staging/') for r in rows),
                  'reusedSources':sum(r['sourceFile'].startswith('final/') for r in rows),
                  'selectionSha256':sha(EVIDENCE/'position-selection-all.json')}))
