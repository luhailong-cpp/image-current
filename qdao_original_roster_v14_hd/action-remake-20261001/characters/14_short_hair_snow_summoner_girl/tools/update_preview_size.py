from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/preview_template.html'
s=p.read_text(encoding='utf-8')
s=s.replace('.stage{position:relative;aspect-ratio:1;', '.stage{position:relative;width:240px;max-width:100%;aspect-ratio:1;')
s=s.replace('<button id="background">切换深浅底</button>', '<button id="background">切换深浅底</button><label>显示 <select id="displaySize"><option value="240">正常 240px</option><option value="512">放大 512px</option></select></label><a href="timing-grounding.html">跑步节奏对照</a>')
s=s.replace("el('background').onclick=()=>el('stage').classList.toggle('light');dirs();", "el('background').onclick=()=>el('stage').classList.toggle('light');el('displaySize').onchange=()=>el('stage').style.width=el('displaySize').value+'px';dirs();")
p.write_text(s,encoding='utf-8')

