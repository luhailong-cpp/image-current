from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/build_preview.py'
s=p.read_text(encoding='utf-8')
s=s[:s.index('html=')]+"""import runpy
runpy.run_path(str(ROOT/'tools/build_current_player.py'),run_name='__main__')
print(json.dumps({'produced':manifest['producedNative'],'groups':{k:len(v) for k,v in groups.items()}},ensure_ascii=False))
"""
p.write_text(s,encoding='utf-8')
(R/'tools/build_timing_review.py').write_text("from pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).with_name('build_current_player.py')),run_name='__main__')\n",encoding='utf-8')
(R/'tools/timing-review-template.html').write_text((R/'tools/uniform-player.html').read_text(encoding='utf-8'),encoding='utf-8')
p=R/'tools/finalize_current.py'
s=p.read_text(encoding='utf-8').replace("16,45),'hit'","16,75),'hit'").replace("'720ms-cycle-trial'","'user-requested-1200ms-uniform'").replace('720ms跑步试播','1200ms跑步正常播放').replace('preview/timing-grounding.html比较480/640/720/800ms及按本角色实际相位的承重停留。','preview/timing-grounding.html固定16帧×75ms=1200ms，保留慢放、暂停、逐帧；缺槽禁播整圈，旧速度档已移除。').replace('跑步E/S/W已建立16帧当前选择','跑步E/S/W/N/NW已建立16帧当前选择').replace('正在生成N/NE/NW/SW','正在完成NE/SW').replace('本机无客户端；未接入客户端，未进行Unity或游戏运行验收。','本机D:/work/mmorpg-client目录存在（2026-10-03只读确认）；本任务只修改本角色素材目录，未接入客户端或进行游戏内验收。')
p.write_text(s,encoding='utf-8')
p=R/'tools/export_run_candidates.py'
s=p.read_text(encoding='utf-8').replace("'legacyBaselineFrameDurationMs':30,'comparisonCycleMs':[480,640,720,800],'selectedCycleMs':None","'frameDurationMs':75,'selectedCycleMs':1200,'phaseWeightsApplied':False")
p.write_text(s,encoding='utf-8')

