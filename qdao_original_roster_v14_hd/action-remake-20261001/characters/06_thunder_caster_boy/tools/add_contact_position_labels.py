from pathlib import Path
p=Path('tools/build_preview.py')
s=p.read_text(encoding='utf-8')
needle="$('frame-meta').textContent=`帧 ${slot+1}"
replacement="const cp=frame.contactPosition;const contact=cp?('支撑：'+cp.supportLeg+' · '+cp.positionPhase+' · 配对 '+(cp.pairFrames??[]).map(n=>String(n).padStart(2,'0')).join('/')+'（150ms）\\n'):'';$('frame-meta').textContent=contact+`帧 ${slot+1}"
assert needle in s
s=s.replace(needle,replacement,1)
p.write_text(s,encoding='utf-8')
p=Path('tools/build_delivery.py');s=p.read_text(encoding='utf-8')
s=s.replace('需按实图确认两侧接触、承重、蹬离与短暂腾空','需按实图确认两侧接触、承重、身体经过与后侧蹬离')
p.write_text(s,encoding='utf-8')
