from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
sel=json.loads((R/'review/run-E-selection.json').read_text(encoding='utf-8'))
manifest=json.loads((R/'candidate/manifest.json').read_text(encoding='utf-8'))
dirs=['N','NE','E','SE','S','SW','W','NW']
specs={'run':(dirs,16,75),'hit':(['E','W'],6,40),'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
rows=[]
for a,(ds,n,ms) in specs.items():
 for d in ds:
  count=sum((R/f'candidate/{a}/{d}/{i:02}.png').exists() for i in range(1,n+1))
  rows.append((a,d,count,n,ms))
text=['# 冰剑少女 · 本机动作交接','','用户时区2026-10-03。只修改本角色目录；未写其他角色或客户端，未作Git提交/推送。','','## 当前优先参数','','**跑步八方向统一1200ms/圈，16帧每帧75ms，正常1倍。** 当前预览已移除旧快速档及相位权重；保留0.25倍慢放、暂停和逐帧。单圈16帧全部播放，16→01不额外停留。正常速度来自用户最新指定，不宣称已改变游戏内速度。','','受击40ms×6=240ms；普攻30ms×12=360ms；施法45ms×16=720ms，均保持原值。参数入口为[animation-timing.json](animation-timing.json)。E选图、候选清单、预览构建/导出和旧检查工具默认已同步，重建不会回到旧速度。','','E当前可视触地候选仍为E01右脚、E08左脚，因此均匀75ms时两次间隔为525/675ms；本次没有伪造600/600或继续套用旧360/360。离地候选E05→06在375ms、E13→14在975ms。相位来自实图，时长遵循用户等帧要求。','','## 当前文件和验证','','- [正常1倍E动画](preview/run-E-1x-1200ms.webp) · [交互预览](preview/index.html)','- [当前源选择](review/run-E-selection.json) · [E候选PNG与SHA](candidate/manifest.json)','- [1200ms浏览器实测](preview/verification-current-timing.json) · [E当前视觉复核](preview/CURRENT16_REVIEW.md)','- [八方向脚向审计](review/FOOT_DIRECTION_E.md) · [制作状态](STATUS.md)','','E向16张1254原生、16张1024 RGBA候选已齐，PNG技术、来源SHA和真实透明度通过。浏览器实测当前1200ms完整16帧顺序和回环、128/256显示、暂停/慢放/逐帧均通过；不是游戏内验收。','','## 每段当前落盘数量','','| 动作/方向 | 1024候选 / 目标 | 正常单帧ms |','|---|---:|---:|']
for a,d,c,n,ms in rows:text.append(f'| {a}/{d} | {c}/{n} | {ms} |')
text+=['','上述是文件库存，不自动授予美术或动态通过。正式目标196张仍在继续制作，不能以E向齐全声称全套完成。旧512八方向128张作为已核查姿态参照保留，不直接放大计HD；旧受击E01/03/06三张原生先复核/编辑，缺槽逐张补。','','## 最新参照与实际问题','','用户已指定09竹弓少女当前版本作为姿态、脚向、手动作、节奏与接地参照，取代此前撤回的月影整体通过判断。实际读取09 manifest列出的同方向runtime图，对照具体相位；不复制竹弓的像素、衣服、武器、持手或跨方向编号。','','E已补落地—全掌压缩—蹬离—短腾空链；08反向抬脚、15先着地后回升、旧03/04与11/12翻剑及多手已修。03→04左符臂摆幅仍偏集中，继续针对中间臂姿处理；右手晶剑、左手蓝符不交换。其他方向和战斗分段继续补齐。','','## 根点与来源','','E暂用全1024画布虚拟近根[512,975.872]，远脚轨道970.752，只作观察诊断。不同方向需按实图膝踝与承重核实，不机械套用E鞋底线。所有导出整画布缩放、translation=[0,0]，不作最低脚贴线、镜像、复制或姿态插值。','','新图使用宿主内置image_gen；同批配置目标2.5 Sunburst/max，实际工具无型号/质量参数且未返回实际值，均记录null。各图旁.generation.json绑定sources/中的实际提示词/参考角色/工具回执/时间/SHA，保留配置目标与实际证据区别。','','## 客户端与保留','','D:/work/mmorpg-client目前已存在；旧“不存在”记录过时。本任务仍仅写私有素材目录，客户端尚未接入或运行。后续需同时接入资源、时长校验与位移步频关系，不能只复制75ms就声称游戏内生效。','','保留当前在制及编辑所依赖素材；成品落盘和当前引用完整后清理淘汰图，保留逐图文字来源。当前candidate为审阅导出，不自动覆盖客户端。','','## 当前E候选SHA','','| 文件 | SHA256 |','|---|---|']
for f in manifest['files']:text.append(f"| {f['path']} | {f['sha256']} |")
(R/'MERGE_HANDOFF.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
(R/'README.md').write_text('# 冰剑少女 · 动作制作\n\n跑步当前正常速度统一1200ms/圈、16×75ms；战斗时长保持不变。全套196帧继续制作，文件齐全与美术通过分别记录。\n\n- [当前1倍E动画](preview/run-E-1x-1200ms.webp)\n- [交互预览](preview/index.html)\n- [当前时长](animation-timing.json)\n- [交接/进度/来源](MERGE_HANDOFF.md)\n- [逐图选择记录](review/run-E-selection.json)\n\n使用内置image_gen，实际型号/质量未披露；实际提示词与回执位于sources/，各图旁generation记录可追溯。\n',encoding='utf-8')
print(json.dumps({'runCycleMs':1200,'frameMs':75,'candidateFiles':sum(x[2] for x in rows),'target':196}))
