from pathlib import Path
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');p=B/'tools/build_reference09_s_preview.py';s=p.read_text(encoding='utf-8')
s=s.replace('<button id="play">暂停</button>','<button id="play">暂停</button><button id="slow">慢放</button>')
s=s.replace('playing=true,last=performance.now()','playing=true,slow=false,last=performance.now()')
s=s.replace("$('prev').onclick=", "$('slow').onclick=()=>{slow=!slow;$('slow').textContent=slow?'恢复正常':'慢放';last=performance.now()};$('prev').onclick=")
s=s.replace("function tick(t){if(playing&&t-last>=75){let step=Math.floor((t-last)/75);n=(n+step)%16;last+=75*step;show()}","function tick(t){let frameDuration=slow?150:75;if(playing&&t-last>=frameDuration){let step=Math.floor((t-last)/frameDuration);n=(n+step)%16;last+=frameDuration*step;show()}")
p.write_text(s,encoding='utf-8');print('slow control added')

