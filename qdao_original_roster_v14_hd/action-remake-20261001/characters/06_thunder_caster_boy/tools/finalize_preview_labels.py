from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/build_preview.py'
s=p.read_text(encoding='utf-8')
s=s.replace("frame.technical_ok?'技术检查通过；美术待验收':", "frame.technical_ok?(data.visual_approval==='current_frames_reviewed_offline'?'当前手脚已复核；客户端未接入':'技术检查通过；美术待验收'):")
s=s.replace("'技术检查通过，待美术验收'", "'技术检查通过；复核范围见页面状态'")
p.write_text(s,encoding='utf-8')
p=R/'tools/contact_sheet.py'
s=p.read_text(encoding='utf-8').replace(' · 候选',' · 当前帧').replace('仅用于候选逐帧检查','仅用于当前帧逐帧检查')
p.write_text(s,encoding='utf-8')
print('Preview/contact labels updated; no sprite pixels changed')
