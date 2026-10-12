# 葫团团交接说明

**2026-10-08收尾：光效待修项已关闭，68帧可按manifest接入。** 只替换W施法08：原生画布局部编辑第二稿保住角色尺度，紧凑光团衔接07、09、10。新SHA为 `15e5a73fd7551d453c278d04cf39a92fb84da6191d595ecd4409ae38ff7e2831`，其他67帧未变。相邻帧双人复核与修订组正常／0.25倍浏览器播放截图抽样已完成。采用来源为 `source/cast/W/08-glow-repair-20261008-r2.png.generation.json`；旧未通过记录另存，当前结论在 `repairCompletion20261008`。仍未接入客户端或完成引擎内验收。

交付目录为本文件所在目录。正式素材为runtime内68张1024×1024透明RGBA PNG，manifest.json列出动作、方向、帧序、时长、事件、pivot与SHA；每张旁边的generation.json记录来源。preview/index.html是六组交互预览，正常和慢放APNG与逐帧总览均在preview目录。

延续原版白毛、金发带、玉绿披肩、青绿尾部毛区、抱太极葫芦的葫团团。E朝右下斜正面；W独立绘制为朝左上真斜背面。坐姿和葫芦保持，没有位移动作。

| 动作 | 每向帧数 | 每帧时长 | 事件 |
|---|---:|---:|---|
| hit | 6 | 40ms | 第02帧 contact |
| attack | 12 | 30ms | 第07帧 impact |
| cast | 16 | 45ms | 第11帧 release |

名义脚点是顶部坐标[512,942]，左下归一化pivot为[0.5,0.08]。正式runtime已完成一次固定注册：同方向跨动作使用相同缩放和偏移，记录在records/final-registration.json。不要再次运行register_final.py，也不要按逐帧包围盒重新对齐；自然受击和发力起伏属于实际绘制动作。

原67帧来源链为runtime generation.json → pre-registration文字记录 → source原生记录；修订W施法08直接指向本次原生来源，固定两次整画布缩放与贴入步骤记在operation和 `records/repair-registration-20261008.json`。最初74张来源／中间图、前次3张试修图、本次4张原生／导出已按保留规则清理，三个cleanup记录保留路径和哈希；主cleanup已追加本次4张。不能仅靠文字重建相同像素。当前E/W方向设计及共享身份／风格参考保留。

配置目标为gpt-image-2.5-sunburst/max，实际内置工具没有型号／质量选择器，未提供可验证的实际型号与质量，因此实际字段为null。官方核对和逐图提示词、时间、工具来源均已记录。没有使用单独收费API/CLI。

68帧技术检查和12个APNG帧数／时长检查通过。全部帧经过逐张查看，最终总览与浏览器正常、0.25倍播放采用现场截图抽样复核；没有连续录像，也未进行客户端或引擎内验收。轻微手绘轮廓变化保留，浏览器调度延迟不代表引擎实际帧率。最终视觉结论在records/final-visual-review.json，与68张最终文件哈希绑定；制作期报告仅保留历史证据。

复核可使用具备Pillow的Python运行tools/build_preview.py --check-only。需要重建派生预览时，依次运行tools/build_preview.py --manifest-out manifest.json与tools/build_apng.py，再运行tools/verify_apng.py检查APNG。若修改正式帧，应重新复核视觉与来源，不能沿用旧哈希对应的视觉结论。

素材修订仅写本只目录，未修改客户端、其他仓库或其他电脑，未操作Git索引、提交、分支或推送；接入方按manifest消费正式帧。
