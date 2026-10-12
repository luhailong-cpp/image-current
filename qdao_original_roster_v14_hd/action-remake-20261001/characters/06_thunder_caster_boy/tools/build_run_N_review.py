"""N-only review artifacts; full-canvas rendering, no runtime mutation."""

# RETIRED_20261005: direct human timing correction supersedes historical writers.
raise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")
from pathlib import Path
import json,hashlib,re
from PIL import Image
R=Path(__file__).resolve().parents[1]
O=R/'review'/'run_N_playback';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frames=[]
for n in range(16):
 p=R/'runtime'/'run'/'N'/f'{n:02d}.png'
 r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'))
 im=Image.open(p)
 assert im.size==(1024,1024) and im.mode=='RGBA'
 assert im.getextrema()[3][0]==0 and im.getextrema()[3][1]==255
 assert r['sha256']==sha(p)
 native=R/r['derivedFrom'][0]['file']; nr=json.loads(native.with_name(native.name+'.generation.json').read_text(encoding='utf-8-sig'))
 assert nr['sha256']==sha(native) and nr['width']>=1024 and nr['width']==nr['height']
 frames.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'nativeFile':native.relative_to(R).as_posix(),'nativeSHA':sha(native),'nativeSize':[nr['width'],nr['height']],'generatedAt':nr['generatedAt'],'generationRecord':p.relative_to(R).as_posix()+'.generation.json','model':nr['actualModel'],'quality':nr['actualQuality'],'review':r['visualReview']})
assert len(set(f['nativeSHA'] for f in frames))==16
data={'sequences':{'N':{'frames':frames}},'clientConnected':False,'visualArtAcceptance':False,'normalCycleMs':1200,'frameDurationMs':75,'comparisonCycleMs':[1200,3600,4800],'slowMeaning':'3600/4800 = 1200 ms normal at one-third/quarter speed; client not connected'}
(O/'review-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
html=(R/'tools'/'timing_grounding_template.html').read_text(encoding='utf-8')
assert 'at(elapsed,1200)' in html and 'value="1200" selected' in html, 'Run template must retain current 1200ms normal timing'
html=html.replace('__DATA__',json.dumps(data,ensure_ascii=False))
html=html.replace('<option value="4800">','<option value="3600">慢放 ⅓× · 3600ms</option><option value="4800">')
html=html.replace("($('cycle').value==='1200'?'正常 1×':'慢放 ¼×')", "($('cycle').value==='1200'?'正常 1×':$('cycle').value==='3600'?'慢放 ⅓×':'慢放 ¼×')")
html=html.replace('href="../index.html"','href="../../preview/index.html"')
html=html.replace('06 雷法少年 · 跑步接地和节奏复核','06 雷法少年 · 北向16帧候选复核')
(O/'index.html').write_text(html,encoding='utf-8')
src=(R/'tools'/'verify_headless_grounding.js').read_text(encoding='utf-8')
src=src.replace("'headless_grounding_'+stamp","'run_N_headless_'+stamp")
src=src.replace('/preview/timing-grounding-20261003/index.html','/review/run_N_playback/index.html')
src=src.replace("'runtime/run/S/'","'runtime/run/N/'").replace("selectOption('S')","selectOption('N')").replace("'/run/S/'","'/run/N/'").replace('data.sequences.S.frames','data.sequences.N.frames')
src=src.replace('page_loaded_S.png','page_loaded_N.png').replace('S run · actual browser playback','N run · actual browser playback').replace('S_1200_vs_','N_1200_vs_').replace('S_step_','N_step_').replace('06 南向实际浏览器播放采样','06 北向实际浏览器播放采样')
src=re.sub(r'for\(const cycle of \[[^\]]+\]\)', 'for(const cycle of [1200,3600,4800])', src)
assert "'old',1200)" in src and '1200ms | frame' in src, 'Headless base must retain current 1200ms normal timing'
src=src.replace('正常或四分之一慢放','正常或三分之一/四分之一慢放')
(R/'tools'/'verify_headless_run_N.js').write_text(src,encoding='utf-8')
print(json.dumps({'frames':len(frames),'uniqueNative':len(set(f['nativeSHA'] for f in frames)),'review':str(O)},ensure_ascii=False))
