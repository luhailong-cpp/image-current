from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
def edit(rel,fn):
 p=ROOT/rel;s=p.read_text(encoding='utf-8-sig');p.write_text(fn(s),encoding='utf-8')
edit('preview/index.html',lambda s: re.sub(r'<select id="runCycle".*?</select>','<select id="runCycle" aria-label="跑步周期"><option value="1200" selected>跑步 1200ms · 75ms/帧</option></select>',s,flags=re.S).replace('试播 1×','正常 1×').replace('跑步默认 720ms 仅为节奏试播，正式速度尚未确认。旧基线与 640/720/800ms 使用同一组真实帧；降速不代表接地姿态已修好。','跑步正常 1×：完整16帧，每帧75ms，一圈1200ms；首尾不额外停顿。保留已认可动作，客户端尚未同步。').replace('<option value="256">','<option value="256" selected>'))
edit('tools/verify_inventory.py',lambda s:s.replace('"run": (16, 45,','"run": (16, 75,').replace('offline_default_720ms_client_unconfirmed','offline_default_1200ms_client_unconfirmed').replace('comparisonCycleMs=[480,640,720,800]','comparisonCycleMs=[1200]'))
edit('tools/build_review_previews.py',lambda s:s.replace('("run",d,16,45)','("run",d,16,75)').replace('  if a=="run":timings.extend([("old480",30),("trial640",40),("trial720",[40,50]*8),("trial800",50)])','').replace('   frames[0].save(out/f"{a}-{d}-{speed}.gif",save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False,disposal=2)','   if a=="run":\n    frames[0].save(out/f"{a}-{d}-{speed}.apng",format="PNG",save_all=True,append_images=frames[1:],duration=duration,loop=0,disposal=0,blend=0)\n   else:\n    frames[0].save(out/f"{a}-{d}-{speed}.gif",save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False,disposal=2)').replace('720ms trial only; client timing unconfirmed','1200ms / uniform75ms applied to preview; client unchanged').replace('GIF45ms average uses alternating40/50ms; HTML uses exact45ms.','Run APNG and HTML use exact75ms; run slow300ms. Combat GIF45ms uses alternating40/50ms, unchanged.'))
edit('tools/build_run_overview.py',lambda s:s.replace('720ms','1200ms').replace('run-eight-directions-720.gif','run-eight-directions-1200.apng').replace("duration=[40,50]*8,loop=0,optimize=False,disposal=2","duration=75,loop=0,format='PNG',disposal=0,blend=0").replace('sum(times)==720','sum(times)==1200'))
edit('tools/verify_delivery_previews.py',lambda s:s.replace("'run':45","'run':75").replace("gp=p.with_name(name+'-'+speed+'.gif')","gp=p.with_name(name+'-'+speed+('.apng' if action=='run' else '.gif'))").replace("sum(overview['durationsMs'])==720","sum(overview['durationsMs'])==1200").replace("'normalAndSlowGifsVerified'","'normalAndSlowAnimationsVerified'").replace("len(durations)==count and sum(durations)==count*frameMs*mult","len(durations)==count and sum(durations)==count*frameMs*mult").replace("  gifs.append(","  if action=='run':assert durations==[75*mult]*16,durations\n  gifs.append("))
edit('tools/write_foot_closeout.py',lambda s:s.replace("'currentRunDefaultMs':720","'currentRunDefaultMs':1200").replace("'perFrameRunMs':45","'perFrameRunMs':75"))
# Historical acceptance remains at its original timing, since PNG approval and timing are separate.
# Retire old private rebuilders to the current shared private generator; never re-emit old timings or reviews.
groups={
 'provenance/run-north/build_current_review.py':['E','NE','NW'],
 'provenance/run-north/finalize_closeout.py':['E','NE','NW'],
 'provenance/run-north/write_review_current.py':['E','NE','NW'],
 'provenance/run-south/make_review.py':['W','S','SE'],
 'provenance/run-south/review_v2.py':['W','S','SE'],
 'provenance/run-south/qa_final.py':['W','S','SE'],
 'provenance/run-south/write_current_review.py':['W','S','SE'],
 'provenance/run-SW/build_preview.py':['SW'],
 'provenance/run-SW/write_review.py':['SW']}
for rel,dirs in groups.items():
 p=ROOT/rel
 if not p.exists():continue
 p.write_text("# Current preview adapter: preserves approved images and existing visual reviews.\nfrom pathlib import Path\nimport runpy,sys\nROOT=Path(__file__).resolve().parents[2]\nsys.argv=[str(ROOT/'tools/build_review_previews.py')]+"+repr(['run/'+d for d in dirs])+"\nrunpy.run_path(sys.argv[0],run_name='__main__')\n",encoding='utf-8')
for rel in ['provenance/run-south/current-review.html','provenance/run-south/W-review.html','provenance/run-SW/review.html']:
 (ROOT/rel).write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>09 当前动作预览</title><p>当前跑步：16帧 × 75ms = 1200ms；已移除旧速度。正常、慢放、暂停和逐帧检查统一在下列入口维护。</p><a href="../../preview/index.html">打开当前完整动作预览</a></html>',encoding='utf-8')
(ROOT/'tools/update_trial_preview.py').write_text("# Superseded one-off migration; no old speed controls may be reintroduced.\nprint('Current preview already uses1200ms/75ms. Build with tools/build_review_previews.py.')\n",encoding='utf-8')
print('Current run preview sources migrated to uniform75ms/1200ms; image files unchanged.')
