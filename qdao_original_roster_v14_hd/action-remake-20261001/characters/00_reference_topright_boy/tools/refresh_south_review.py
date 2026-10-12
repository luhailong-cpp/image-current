"""Rebuild diagnostics from current selections without changing any selections/art."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review/grounding-fourframes'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
all_rows=[]
for d in ('S','SE','SW'):
    rows=json.loads((ROOT/f'generation/run/{d}/selection-middle4-side2-20261004.json').read_text(encoding='utf-8-sig'))
    full=Image.new('RGB',(1200,1320),'#dedede');lower=Image.new('RGB',(1600,880),'#dedede')
    fd=ImageDraw.Draw(full);ld=ImageDraw.Draw(lower)
    for i,row in enumerate(rows):
        path=ROOT/row['source'];digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert row['sourceSha256']==digest
        with Image.open(path) as im:
            thumb=im.resize((300,300),Image.Resampling.LANCZOS)
            x=i%4*300;y=i//4*330;full.paste(thumb,(x,y+27),thumb)
            fd.text((x+4,y+3),f'{d}{i+1:02d} {path.stem} {row["supportFoot"]} P{i%8//2+1}',font=font,fill='black')
            crop=im.crop((200,780,1150,1254)).resize((400,200),Image.Resampling.LANCZOS)
            x=i%4*400;y=i//4*220;lower.paste(crop,(x,y+20),crop)
            ld.text((x+4,y+1),f'{d}{i+1:02d} {path.stem} {digest[:8]}',font=font,fill='black')
    full.save(OUT/f'{d}-south-final-candidate-full.jpg',quality=94)
    lower.save(OUT/f'{d}-south-final-candidate-lower.jpg',quality=95)
    all_rows.extend(rows)
report_path=OUT/'south-static-evidence-middle4-side2.json'
report=json.loads(report_path.read_text(encoding='utf-8-sig'))
report.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),frames=all_rows,
              status='current_selection_static_evidence_independent_report_authoritative',
              independentReport='S-SE-SW-independent-static-review.json')
report['rejectedCandidates'].update({'SW/07-v6':'错误左腿后撑，已替换','SW/08-v8':'错误左腿后撑，已替换','SW/07-v7':'髋连接修正但整体放大，已拒绝'})
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# S / SE / SW 当前静态复核','', '当前来源以局部选表及独立报告绑定SHA为准。16×75ms=1200ms；动态与客户端未验收。','', '|方向|帧|来源|支撑|观察|','|---|---:|---|---|---|']
for row in all_rows:
    lines.append(f'|{row["direction"]}|{row["frame"]:02d}|{Path(row["source"]).stem}|{row["supportFoot"]}|{row["observation"]}|')
(OUT/'south-static-evidence-middle4-side2.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('48 current rows and six diagnostic sheets refreshed; source art and selections unchanged.')
