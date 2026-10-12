from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/uniform-player.html'
s=p.read_text(encoding='utf-8').replace("String(f.frame).padStart(2,'0')","String(f.sourceFrame??f.frame).padStart(2,'0')")
p.write_text(s,encoding='utf-8')
(R/'tools/timing-review-template.html').write_text(s,encoding='utf-8')
p=R/'tools/prepare_current_delivery.py'
s=p.read_text(encoding='utf-8').replace("'translation':[-16,174]","'translation':[0,174]").replace('x770,y1120','x746.3,y1120')
p.write_text(s,encoding='utf-8')

