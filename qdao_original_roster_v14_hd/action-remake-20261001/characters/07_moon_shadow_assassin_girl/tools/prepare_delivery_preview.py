"""Prepare finalized metadata without moving or deleting image data."""
import json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'tools/preview-template.html'
s=p.read_text(encoding='utf-8')
s=s.replace('根点 / 94%诊断线','根点 / 接地诊断线').replace('跑步试播 <select','跑步节奏 <select')
s=s.replace('<option value="720" selected>720ms / 圈（待审）</option>','<option value="manifest" selected>交付节奏 · 720ms / 圈</option><option value="720">720ms / 圈（匀速对照）</option>')
s=s.replace("if(f.action!=='run')return f.durationMs||specs[f.action].ms;","if(f.action!=='run'||$('runTiming').value==='manifest')return f.durationMs||specs[f.action].ms;")
s=s.replace("f.action==='run'?'（试播）':''","f.action==='run'?($('runTiming').value==='manifest'?'（交付节奏）':'（对照试播）'):''")
s=s.replace("$('root').style.top='94%'","$('ground').style.top=(anchor[1]/1024*100)+'%'")
s=s.replace("const initial=m.frames.find(f=>specs[f.action]);","const initial=m.frames.find(f=>f.action==='run'&&f.direction==='E')||m.frames.find(f=>specs[f.action]);")
s=s.replace("尚未通过视觉验收","待视觉复核").replace("'视觉通过'","'离线视觉复核通过'")
s=s.replace("结构通过和 SHA 不同均不能证明美术通过。","本页为离线动作复核；尚未接入客户端检查位移与滑步。")
p.write_text(s,encoding='utf-8')
print('Preview template updated; actual manifest still candidate.')

