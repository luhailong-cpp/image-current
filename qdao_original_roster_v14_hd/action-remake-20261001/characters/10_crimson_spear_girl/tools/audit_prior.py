from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
PROJECT=Path('D:/work/image')
old=PROJECT/'qdao_original_roster_v14_hd/recovery-20260921/10-delivery-preview/current'
records=[]
(ROOT/'preview').mkdir(exist_ok=True)
for direction in ['N','NE','E','SE','S','SW','W','NW']:
    sheet=Image.new('RGB',(1400,1440),'#eae9e2')
    draw=ImageDraw.Draw(sheet)
    for i in range(1,17):
        p=old/'walk'/direction/f'{i:02}.png'
        if not p.exists(): continue
        im=Image.open(p)
        metadata=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
        records.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'direction':direction,'frame':i,'size':im.size,'mode':im.mode,'generationRecord':str(p)+'.generation.json','priorVisual':metadata.get('finalVisualReview'),'currentRunReview':'not accepted as corrected run; prior walk status alone is insufficient'})
        thumb=im.copy();thumb.thumbnail((350,350))
        x=((i-1)%4)*350;y=((i-1)//4)*360
        sheet.paste(thumb,(x,y),thumb)
        draw.text((x+8,y+340),f'{direction} {i:02}',fill='#222222')
    out=ROOT/'preview'/f'prior-walk-{direction}.jpg'
    sheet.save(out,quality=92)
    trace={'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'read-only prior-walk audit thumbnail sheet','derivedFrom':[{'file':r['file'],'sha256':r['sha256'],'generationRecord':r['generationRecord']} for r in records if r['direction']==direction]}
    Path(str(out)+'.generation.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data={'character':'10_crimson_spear_girl','priorWalkFrames':len(records),'priorCorrectionPNGs':0,'priorCombatPNGs':0,'evidence':'Local run-correction contains HANDOFF.md only; combat contains export tool and initial inventory only. PRIOR_RUN_AUDIT and PRIOR_COMBAT_AUDIT agree.','files':records}
(ROOT/'PRIOR_INVENTORY.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(records))
