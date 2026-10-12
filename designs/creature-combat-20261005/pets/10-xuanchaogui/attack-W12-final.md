# 玄潮龟 attack/W12 回位修正

2026-10-08。只修 W12。使用 `imagegen` 技能及宿主内置 `image_gen.imagegen`；未使用 API/CLI、客户端或 Git。

## 实际输入与处理

- 已实际查看 TASK 指定原生 E/W 身份、主要画法成图，以及正式 W01、W11、旧 W12。三张规定参考实际传入工具，W01 作为主要编辑目标与构图基准，W11 作为上帧运动参考。
- 真 AI 独立生成最后收势。W12 头颈、甲体和左侧前足回到 W01 警戒位置；水纹与短穗留有独立的收势变化。没有复制、镜像、整图平移或插值。
- 新原生 1254×1254 RGBA；`tools/save_frame.py` 按本方向共用的整画布 1024×1024 导出，无内容对齐或平移。正式路径 `runtime/attack/W/12.png`。
- 配置目标 `gpt-image-2.5-sunburst` / `max`；真实提交 model/quality 与实际返回 model/quality 均未披露，记录为 null。准确提示见 `prompts/attack/W/12-final.txt`，调用证据见 `provenance/attack/W/12-final.receipt.json`，原生来源与导出 sidecar 已重建。
- 旧 W12 来源与导出文字分别保存在 `provenance/attack/W/12.pre-final.generation.json` 和 `12.pre-final.runtime-generation.json`；没有建立旧图备份。

## 实际复核

已打开新原生图和导出正式图。新 W12 头冠约 y=126（W01 约125，旧W12约185），左侧前足末端约 y=737（W01约740，旧W12约795），甲上沿约 y=250，较原W12明显回到W01高位；以上为人工目视量，不是关节自动识别。两后足支撑位置基本保持，尾单条上卷、右侧桂枝和朱结、每只可见足三爪保持，真实斜后左上视角未转胸面。末帧可直接交由根任务重建六组预览并检验正常/0.25×连播；本次没有独立声称全段动态已通过。

最终 PNG SHA256：`d045728774e76cc7279c05aa79b769f49c2c20102193194588a01188a1ed39d6`。

可见主体未裁切。低 alpha 零散边像素仍存在，技术 bbox 不等于实际主体边界；交由根任务结合整包深浅/棋盘背景验收。客户端未接入。
