from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'tools/write_handoff.py';s=p.read_text(encoding='utf-8')
s=re.sub(r'^timing=.*$', 'timing={"updatedAtUtc":datetime.now(timezone.utc).isoformat(),"run":{"frameMs":75,"frameDurationsMs":[75]*16,"cycleMs":1200,"slowFrameMs":300,"slowCycleMs":4800,"timingStatus":"offline_default_applied_client_unconfirmed","availableNormalCycleMs":[1200],"formalClientTimingConfirmed":False,"phaseWeightsApplied":False,"extraLoopPauseMs":0},"hit":{"frameMs":40,"cycleMs":240,"peakFrame":3},"attack":{"frameMs":30,"cycleMs":360,"fullDrawFrame":6,"releaseFrame":7},"cast":{"frameMs":45,"cycleMs":720,"fullDrawFrame":9,"releaseFrame":10},"clientIntegration":"not_integrated"}',s,flags=re.M)
s=s.replace('跑步使用相同16帧比较480/640/720/800ms；本素材包的正常预览与manifest默认已统一为720ms（45ms/帧），比旧480ms周期延长50%、步频降为2/3。客户端时长仍未接入确认；该参数不能当作游戏内实测。未照搬其他角色的承重权重。慢速0.25×为2880ms/圈。受击40ms/帧、普攻30ms/帧、施法45ms/帧保持不变。','最新用户要求：跑步正常1×采用1200ms完整循环，16帧均匀75ms，首尾不额外停顿；正式预览已移除480/640/720/800ms旧速度选项。慢速0.25×为每帧300ms、一圈4800ms。正确PNG保持用户认可的同一版本，不套用相位权重。受击40ms/帧、普攻30ms/帧、施法45ms/帧保持不变。客户端未同步或运行验收。accepted-version.json中的720ms是当时认可的历史预览节奏，当前时长以本文件和animation-timing.json为准。')
s=s.replace('打开[preview/index.html](preview/index.html)：全部14段、真实196帧、深浅底、128/256px游戏尺寸、放大、逐帧、慢速及四档跑步周期。preview/qa/提供接图与GIF；720ms GIF用40/50ms交替表示平均45ms，HTML使用精确45ms，不复制画面补时长。','打开[preview/index.html](preview/index.html)：全部14段、真实196帧、深浅底、128/256px游戏尺寸、放大、逐帧、暂停和慢放。正常跑步只保留1200ms。preview/qa/的跑步APNG与HTML均精确使用75ms/帧，慢放300ms/帧；战斗GIF时长不变。不复制画面补时长。')
s=s.replace('本包45ms参数','本包75ms参数').replace('[八方向720ms总览](preview/qa/run-eight-directions-720.gif)','[八方向1200ms总览](preview/qa/run-eight-directions-1200.apng)')
s=s.replace('以下是逐组既有技术审查与待观察项，保留为追溯记录。','以下是逐组既有技术审查与待观察项，保留为追溯记录；其中审阅者提及的旧试播时长不是当前播放配置，当前统一以1200ms/75ms为准。')
p.write_text(s,encoding='utf-8')
p=ROOT/'tools/review_n_frames.py';s=p.read_text();s=s.replace('"trialCycleMs":[480,640,720,800]','"trialCycleMs":[1200]').replace('"defaultTrialCycleMs":720','"defaultTrialCycleMs":1200');p.write_text(s,encoding='utf-8')
p=ROOT/'tools/PREVIEW_README.md';s=p.read_text(encoding='utf-8');s=s.replace('跑步默认试播1×为720ms/圈、45ms/帧；另提供旧480ms和640/800ms对照。慢速0.25×为2880ms/圈。','跑步正常1×为1200ms/圈、16帧均匀75ms；旧480/640/720/800ms档已移除。慢速0.25×为4800ms/圈、300ms/帧。').replace('GIF以40/50ms交替精确合计720ms，HTML按45ms。','跑步APNG与HTML逐帧精确75ms，完整16帧循环，无首尾额外停顿；战斗GIF保留原时长。');p.write_text(s,encoding='utf-8')
print('Current timing documentation generators synchronized.')
