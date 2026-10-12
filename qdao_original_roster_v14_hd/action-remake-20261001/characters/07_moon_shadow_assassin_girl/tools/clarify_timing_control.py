from pathlib import Path
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
p=r/'tools/preview-template.html';s=p.read_text(encoding='utf-8')
s=s.replace('E向承重稍停留','对照时延长E向承重')
s=s.replace("function render(){let f=frames[at];","function render(){$('weighted').disabled=$('runTiming').value==='manifest'||$('direction').value!=='E';let f=frames[at];")
p.write_text(s,encoding='utf-8')

