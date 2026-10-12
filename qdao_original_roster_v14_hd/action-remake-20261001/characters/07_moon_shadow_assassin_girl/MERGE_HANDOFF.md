# 07 月影少女 · 当前动作素材交付

2026-10-05：当前正式成品为196张1024×1024透明RGBA PNG及42张配套连图/APNG，均完成离线验收。当前记录为[本轮验收](review/limb-axis-20261005/final-review.json)，以manifest.json和SHA256SUMS.txt中的当前像素为准。

[打开全部动作预览](http://127.0.0.1:8777/preview/index.html)。右侧14个动作组可切换，支持正常速度、¼慢放、暂停、逐帧和160px/256px检查。图片带当前SHA版本参数。服务停止时可直接打开本目录preview/index.html，清单已内嵌。

## 当前节奏与范围

按用户最新直接确认，跑步已经统一为 **60ms/帧，16帧共960ms（0.96秒）**；¼慢放为240ms/帧、3840ms一圈。正式manifest、网页播放、回退值、连图标签与导出APNG一致。以前记录中的75ms/1200ms是历史版本，由[本次计时决定](review/limb-axis-20261005/timing-decision.json)覆盖；冻结的历史清单保留原值用于追溯。

跑步八方向各16张，共128张。受击E/W各6张、普攻E/W各12张、施法E/W各16张，共68张；战斗方向范围是E/W。受击40ms、普攻30ms、施法45ms每帧保持原值。

每半圈同一支撑腿依次四位置，各两张独立姿态：01–02前落地/缓冲、03–04身下承重、05–06后驱、07–08末端前掌；09–16换另一腿。本轮手脚局部修订保留支撑腿、相位和事件。

## 本轮四张修正

- run_S_07：前伸手的刀刃与柄尾恢复与06/08一致，修正单帧握刀反向。
- run_SW_14：后伸小靴鞋尖收向左下，衔接13/15/16与小腿方向。
- cast_W_07：补入06高举到08前伸之间的手臂过渡，保留两手各自肩部连接，修正单帧高低位置骤换。
- attack_W_09：近腰手匕首恢复向外，衔接08/10的手腕与刀柄。

本轮对196张原正式PNG及14张连图逐一审查，记录在review/hand-limb-audit-20261004。主审针对疑点查看相邻原图，复看四张原生编辑结果、四组候选连图和发布后的四组正式连图，再核对浏览器正式帧。192张保留帧的SHA与审查基线一致。hit_E_02–03属于伴随后仰的持续手臂旋转，run_NE_09–11未确认孤立扭踝，均保留正常屈膝、透视与姿态变化；未将疑点直接当作错误重画。

此前direction-alignment-20261004、direction-combat-20261004、run-grounding-20261004及axis-continuity-20261004修订继续保留。不同轮有重叠帧，替换数不能相加当作独立成品数。前轮外部视频只作为运动平面和连续性参考，其实际查看范围与限制见review/axis-continuity-20261004/reference-evidence.json。

## 来源与保留

正式文件：frames/{action}/{direction}/NN.png。每张图的.png.generation.json记录实际提示词、输入SHA、原生图SHA和工具回执。本轮通过宿主内置image_gen.imagegen编辑，再全画布等比Lanczos导出1024；未裁框、镜像、整体平移或插值造帧。工具未披露实际模型与质量，记录为null，与配置目标分开保存。

[本轮完整提示词与来源索引](review/limb-axis-20261005/prompt-index.json)。前轮索引保留在各自review目录。成品和引用验证后，本轮删除8张原生加工图与候选检查图，只保留196张游戏图和42张正式预览；保留来源文字与SHA清理台账，共518条历史清理记录。未删除本角色目录外的文件。

## 验证与接入边界

196张正式帧的结构、透明通道、内容唯一性、SHA与来源检查通过。42个预览文件齐全，真实APNG延时正确，14组动作共56项虚拟时钟播放检查通过。实际浏览器检查包括八方向跑步及本轮两组战斗的正常速度单次播放，四组修订动作的¼慢放和正常循环边界采样，以及四张修订正式帧的渲染截图查看。见[browser-check.json](review/limb-axis-20261005/browser-check.json)及[timing-verification.json](review/limb-axis-20261005/timing-verification.json)。没有连续浏览器录屏。

本次完成素材与离线预览，未修改、接入、启动或测试D:/work/mmorpg-client；世界位移、阴影、滑步和技能判定需要客户端实测。

复核命令（Python需Pillow）：

```powershell
python -X utf8 -B tools/verify_manifest.py --require-complete --report
python -X utf8 -B tools/check_direction_delivery.py --revision review/limb-axis-20261005
python -X utf8 -B tools/check_final_previews.py
```

只重建当前预览使用tools/rebuild_previews.py；只重建HTML使用tools/build_preview.py。不要重新运行历史发布、修订或导出脚本覆盖当前成品。
