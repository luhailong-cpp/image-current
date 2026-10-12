from pathlib import Path
p=Path(__file__).resolve().parent/"build_run_preview.py"
s=p.read_text(encoding="utf-8")
old="const segments=g.contactSegments.map(s=>s.frames.map(n=>String(n).padStart(2,'0')).join('→')).join(' / ');"
new="const segments=g.contactSegments.map(s=>(s.supportFoot==='right'?'右':'左')+'脚 '+String(s.frames[0]).padStart(2,'0')+'–'+String(s.frames[s.frames.length-1]).padStart(2,'0')).join(' / ');"
assert old in s;s=s.replace(old,new)
s=s.replace("'已复核接地段：'+segments","'接地脚序：'+segments")
s=s.replace(".muted{color:#bbcbbf}",".grounding{font-size:12px;overflow-wrap:anywhere}.muted{color:#bbcbbf}")
s=s.replace("检查脚向、支撑、腾空和16→01衔接","检查脚向、支撑、摆腿和16→01衔接")
p.write_text(s,encoding="utf-8")

