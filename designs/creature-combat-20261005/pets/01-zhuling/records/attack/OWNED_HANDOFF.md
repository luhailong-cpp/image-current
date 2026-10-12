# attack 子任务交接

本子代理已完成 **18 张**独立 AI 帧：`runtime/attack/E/01.png..12.png` 与 `runtime/attack/W/01.png..06.png`。W07..12 由主代理承担，本子代理未触碰。

- 内置 image_gen；每张附原有 E/W 身份与既定画法图；未用付费 API/CLI、镜像、复制、插值或平移补帧。
- 目标配置 gpt-image-2.5-sunburst / max，真实 model/quality 无选择器且未披露，每图为 null。
- 原生均 1254×1254 RGBA；统一完整画布 resize 为 820×820 后在透明1024画布(102,102)合成，未按脚点/bbox单独对齐。
- 每图 prompt 在 prompts/attack/<direction>/<nn>.txt，记录在 records/attack/<direction>/<nn>.generation.json。记录有非像素 receipt、时间、native SHA、导出 SHA、输入路径与实际视觉检查。
- E10首次生成连接发送失败，错误记录保留；第二次成功。
- W05、W06初稿因姿态不合已用真实 AI 定点重绘，失败候选仅作为来源文字记录；最终 runtime 已替换。原生来源缓存仍被当前制作使用，不擅删目录外文件。

## 实际检查

所有18张在出图时实际看过；已实际查看棋盘底接触表 qa/attack/E-contact.png、qa/attack/W-contact.png。
技术检查 qa/attack/subagent-check.json：18/18均1024 RGBA，alpha覆盖0..255，SHA无重复。
E前右下，W后左上；后视无转胸、两翼两足与短扇尾及固定饰物均可辨。
E06..08横扫清楚；W05已改为低位前转，衔接W04与W06避免大V重新展开。W06近翼折肘向左内转、羽尖跨颈后，供W07继续前扫。
部分原生羽尖接边/低alpha噪点在记录中保留；统一导出后有留边，没有裁主体或清理像素冒称AI修改。
**本子代理未完成实际连续播放，统一动态实播由主代理做；客户端未读取、未接入。**

## 主代理衔接输入

W06 native：
C:/Users/luyua/.codex/generated_images/01a10bb5-3d7b-79b2-8a50-d8582f7e5d8c/exec-a3473007-72ae-4d77-9f80-c5c218591dce.png

native SHA256: 3c26ab8adcedd5e6e1b1651bd9fe2c3a93816bbf0b91e38f146f73e7a3162fb0

W05最终 native：
C:/Users/luyua/.codex/generated_images/01a10bb5-3d7b-79b2-8a50-d8582f7e5d8c/exec-efee117c-db16-4cb4-b8f7-7a0d36a4d2bf.png

检查脚本只写本子代理18帧记录与接触表；check_owned_frames.py 后应接 finalize_owned_qa.py 才恢复最新W05定点说明。不要在主代理统一QA状态写入后再运行，以免覆盖动态状态。

