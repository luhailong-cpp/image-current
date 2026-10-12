# 烛翎 · 受击、普攻、施法

三种动作共68/68帧已完成，验收范围见 [STATUS.md](STATUS.md)。最终合同为E斜前朝右下、W真斜后朝左上，68张1024×1024透明PNG；无移动动画。

[打开六组动作预览](preview/index.html)：支持正常1×、0.25慢放、暂停、逐帧滑块与前后帧、单组放大，以及透明棋盘/深色/浅色背景。预览仅切换实际帧，不插值。直接用浏览器打开本地HTML即可，无网络服务依赖。

|动作|每向帧数|每帧|每向时长|释放事件|
|---|---:|---:|---:|---|
|受击 hit|6|40ms|240ms|无|
|普攻 attack|12|30ms|360ms|07 impact|
|施法 cast|16|45ms|720ms|10 release|

图片路径 `runtime/<hit|attack|cast>/<E|W>/01.png`。每个动作的末帧为独立绘制的回稳姿态。E/W保持同一只原有靛蓝灵鸦：铜红翼斑、琥珀云冠、象牙绢领、青瓷烛坠、两翼两足与短扇尾。

## 文件与坐标

- [manifest.json](manifest.json)：逐帧路径、动作方向、时长、事件、SHA、模型证据路径与视觉状态。
- [SHA256SUMS.txt](SHA256SUMS.txt)、[validation.json](validation.json)：完整性、尺寸、RGBA/Alpha、重复检查。技术通过不自动表示动态美术通过。
- [POSES.md](POSES.md)：解剖、方向和动作阶段；[qa](qa/) 为逐帧检视与动态检查记录。
- [MERGE_HANDOFF.md](MERGE_HANDOFF.md)：接入字段和未验证范围。

全套统一将原生完整方形画布缩至820×820，再置于1024透明画布的(102,102)。保留图内自然重心变化，没有逐帧脚点归一、裁成局部、镜像或补帧。虚拟悬浮锚点以左上原点为(512,942)，左下归一pivot为(0.5,0.08)；它是播放锚点，不声称每帧爪底与其重合。

## 模型与来源

使用内置 image_gen，未使用单独计费API/CLI。目标为本批配置快照 `gpt-image-2.5-sunburst / max`；实际模型和质量因宿主管理且工具未披露而为null。详见 [MODEL_VERIFICATION.md](MODEL_VERIFICATION.md)。

逐图来源通过manifest的`generationRecord`索引：hit及部分attack图旁为`*.png.generation.json`，其余在`records/<action>/<direction>`。每张记录包含实际prompt、参考用途、时间、native/导出SHA、配置快照、实际提交与返回证据。失败请求与被替换候选的文字记录保留，不用配置目标冒充真实返回版本。

原有身份及风格参考位于Image既有目录，仅作只读输入。本目录不包含新引入宠物，不读取/修改客户端、兄弟仓库，不做Git提交。客户端材质、缩放、排序、帧事件与实机性能仍未验。
