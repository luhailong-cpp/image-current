from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"tools/export_preview.py"
s=p.read_text(encoding="utf-8").replace("跑步默认720ms试播，可对比旧480ms、640ms、800ms和分相位720ms；都不是正式客户端值。","跑步正常1×统一1200ms/圈，16帧均匀75ms，无额外尾帧停留；客户端尚未接入。")
p.write_text(s,encoding="utf-8")
for name,target in [("build_run_grounding_preview.py","build_run_preview.py"),("refresh_status.py","merge_current_selections.py"),("update_trial_timing.py","build_run_preview.py"),("sync_timing.py","build_run_preview.py")]:
 (ROOT/"tools"/name).write_text('"""兼容入口；读取当前统一参数，禁止回写旧节奏。"""\nfrom pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).with_name("'+target+'")),run_name="__main__")\n',encoding="utf-8")
p=ROOT/"tools/merge_current_selections.py";s=p.read_text(encoding="utf-8").replace("跑步按640/720/800ms对比；720ms当前为离线试播，不是客户端定值。","跑步正常1×统一1200ms/圈、每帧75ms、无额外尾帧停留；客户端未接入。").replace("跑步节奏对比","八方向跑步预览");p.write_text(s,encoding="utf-8")
p=ROOT/"tools/write_handoff.py";s=p.read_text(encoding="utf-8");s=s.replace("from zoneinfo import ZoneInfo","from zoneinfo import ZoneInfo\nfrom timing import RUN_TIMING")
s=s.replace("{'status':'trial_only','defaultLoopMs':720,'comparisonLoopMs':[480,640,720,800],'phaseTrialMs':[65,85,75,45,20,20,25,25]*2}","RUN_TIMING")
s=s.replace("跑步默认720ms试播，比较640/720/800ms与旧480ms；可选承重停留方案[65,85,75,45,20,20,25,25]×2。所有跑步时长均待审，不是正式客户端值。","跑步正常1×统一1200ms/圈，16帧均匀75ms，无额外尾帧停留；保留4倍慢放和逐帧控制。该参数已写入离线交付，客户端未接入。")
p.write_text(s,encoding="utf-8")
print("当前预览、生成脚本及交接统一为1200ms/75ms。")
