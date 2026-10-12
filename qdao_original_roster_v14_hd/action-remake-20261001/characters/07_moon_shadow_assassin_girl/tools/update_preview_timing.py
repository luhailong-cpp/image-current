from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'tools/preview-template.html'
s=p.read_text(encoding='utf-8')
s=s.replace("${f.durationMs||specs[f.action].ms} ms · 本组", "${Math.round(frameDuration(f)*100)/100} ms${f.action==='run'?'（试播）':''} · 本组")
s=s.replace("$('runTiming').onchange=$('weighted').onchange=()=>{if(playing)", "$('runTiming').onchange=$('weighted').onchange=()=>{render();if(playing)")
s=s.replace("根锚点</label>", "根点 / 94%诊断线</label>")
p.write_text(s,encoding='utf-8')
