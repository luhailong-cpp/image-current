from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/build_previews.py'
s=p.read_text(encoding='utf-8')
s=s.replace("s.action==='run'?'旧基线 480ms':'正常速度'","s.action==='run'?'正常 1× · 1200ms':'正常速度'")
s=s.replace('固定全画布显示，根锚点仅作参考标记，不自动贴地。','固定全画布显示，根锚点仅作参考标记，不自动贴地。跑步正常1×为1200ms（每帧75ms）；慢放为4800ms。')
s=s.replace('<div id="total" class="badge">','<p><a href="run-grounding.html">八方向跑步 · 1200ms正常 / 慢放 / 逐帧</a></p><div id="total" class="badge">')
s=s.replace("byId('frame').src='../'+f.path.split('/').map(encodeURIComponent).join('/')","byId('frame').src='../'+f.path.split('/').map(encodeURIComponent).join('/')+'?sha='+f.sha256")
s=s.replace("img.src='../'+f.path.split('/').map(encodeURIComponent).join('/')","img.src='../'+f.path.split('/').map(encodeURIComponent).join('/')+'?sha='+f.sha256")
s=s.replace("function stop(){clearTimeout(timer);timer=null}","let playbackStart=0,playbackSlot=1;function stop(){cancelAnimationFrame(timer);timer=null}")
old="function tick(){show(nextSlot(slot,seq().expected));timer=setTimeout(tick,seq().frame_ms*factor)}async function play(f){stop();factor=f;const selected=current;await Promise.all(preloadAll);if(current===selected)timer=setTimeout(tick,seq().frame_ms*factor)}"
new="function tick(now){const n=(playbackSlot-1+Math.floor((now-playbackStart)/(seq().frame_ms*factor)))%seq().expected+1;if(n!==slot)show(n);timer=requestAnimationFrame(tick)}async function play(f){stop();factor=f;const selected=current;await Promise.all(preloadAll);if(current===selected){playbackSlot=slot;playbackStart=performance.now();timer=requestAnimationFrame(tick)}}"
if old in s:s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
p=R/'tools/merge_inventory.py';s=p.read_text(encoding='utf-8')
s=s.replace('"target_frames":196,"frames":','"target_frames":196,"timing":{"run":{"frameMs":75,"cycleMs":1200,"uniform":True,"clientConfirmed":False},"hit":{"frameMs":40,"cycleMs":240},"attack":{"frameMs":30,"cycleMs":360},"cast":{"frameMs":45,"cycleMs":720}},"frames":')
p.write_text(s,encoding='utf-8')
p=R/'tools/write_handoff.py';s=p.read_text(encoding='utf-8')
s=s.replace("'legacyCycleMs':480,'comparisonCycleMs':[640,720,800],'adoptedCycleMs':None","'frameMs':75,'adoptedCycleMs':1200,'uniform':True,'clientConfirmed':False")
s=s.replace('提供480旧基线与640/720/800ms比较。跑步采用值尚未定稿，不能把试播时长当客户端参数。','提供1200ms正常、4800ms慢放和逐帧。用户明确采用正常16×75ms=1200ms，已移除旧快档；客户端尚未接入。')
p.write_text(s,encoding='utf-8')
print('updated generator defaults: run 16 x 75ms, no fast options')

