# 09 私有库存与动态预览

`verify_inventory.py` 只读检查当前角色，不触碰旧任务或其他角色。默认只输出 stdout；本批已使用 `--write-reports` 生成当前报告。

```powershell
python tools/verify_inventory.py
python tools/verify_inventory.py --write-reports
```

本机 `python` 是未启用的 Store 别名；实际可用解释器为 `C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。使用 `-X utf8` 可确保中文输出编码。`node tools/verify_player_timing.cjs` 使用模拟 DOM 核验控件与循环时长，不打开浏览器。浏览器工具已拒绝本地 file 导航；不要运行旧 `smoke_preview.cjs` 或换协议绕过该限制。代码时序测试不代表实播美术通过。

加 `--write-reports` 后仅更新本角色 `status.json`、`manifest.json`、`preview/data.js`。没有导出图片、生成补帧、裁切、镜像、重心定位或自动美术通过功能。库存不完整仍可生成预览；不要将命令退出 0 当作交付通过。

正式入口：`runtime/<action>/<direction>/<01..N>.png`。文件须 1024×1024、RGBA、真实透明、非全空，记录轮廓是否碰边与可见像素重复/镜像。每一目标槽都单独记录；共196槽/14段。磁盘 PNG 总数与槽位占用数分开统计。全部独立 PNG 已存在也不会自动变为完整验收。

可选 `selection.json` 或 `selection/*.json` 提供已选在制稿与来源；路径均相对此角色目录。示例：

```json
{
  "frames": [{
    "action": "hit", "direction": "E", "frame": 3,
    "file": "staging/hit/E/03.png", "sha256": "实际文件哈希",
    "generationRecord": "provenance/receipts/hit-E-03.json",
    "generationRecordSha256": "来源记录哈希",
    "sourceNativeSize": [1024, 1024]
  }]
}
```

也兼容旧单动作选表：文件顶层给 `action`、`direction`，`frames` 里仅写 `frame` 等项。正式 runtime 存在时优先用于预览；否则选定在制稿必须本身是 1024画布才能播放。其他尺寸会明确显示未通过预览检查，保留原文件链接，不自动缩放。来源 `nativeCellSize` 优先于 `nativeSize`，最后才采用 `width/height`；拼图研究稿须准确填写每个角色小格的原生尺寸，不能用整图尺寸冒充原生单帧尺寸。原生尺寸证据项只是库存字段检查，仍须人工检查记录真实性。

来源记录必填字段沿用旧管线：`file, sha256, generatedAt, tool, route, configSnapshot, submittedParameters, actualModel, actualQuality, evidence, prompt, references, width, height`。未知实际型号或质量允许 `null`，但必须有 `unverifiedReason`；目标配置不冒充实测。记录必须匹配当前选定图的路径和SHA。缺记录、缺原生单帧尺寸证据或低于1024均不计为技术通过。若 runtime 是选定图的非逐字节复制派生物，本检查保守标记需派生回执复核，不自行判通过。

人工逐帧视觉和动态验收可记在本角色 `review.json`：

```json
{
  "frames": [{"slot": "hit/E/03", "status": "passed", "sha256": "当前选定或runtime文件哈希", "evidence": "真实查看后的说明"}],
  "sequences": [{"sequence": "hit/E", "status": "passed", "frameSha256": ["按01至06顺序的完整哈希"], "evidence": "正常、0.25倍与逐帧检查说明"}]
}
```

只有哈希仍匹配才统计通过；动态通过必须该段全部槽实际存在，且当前完整有序哈希与复核记录相同。实际美术判断不由脚本代做。

可选 `anchor.json` 的 `root: [x,y]` 和 `evidence` 仅画固定参考标记，不移动图像。未提供时如实标记未核验。预览始终 `drawImage(image,0,0)`，无 bbox 缩放或逐帧最低脚贴地。CSS仅缩放整个1024显示窗口，与帧内容无关。

用户可双击 `preview/index.html` 查看（不依赖 fetch 或服务器）。跑步正常1×为1200ms/圈、16帧均匀75ms；旧480/640/720/800ms档已移除。慢速0.25×为4800ms/圈、300ms/帧。受击40ms、普攻30ms、施法45ms/帧不随跑步降速。支持逐帧、深浅底、128/256px显示、逐段/14段顺序播放与库存表。此处时长不是已集成客户端的参数。跑步APNG与HTML逐帧精确75ms，完整16帧循环，无首尾额外停顿；战斗GIF保留原时长。载入失败、未生成与尺寸不符分别显示，缺帧不缩短、不复用别的帧补齐。

本预览和脚本只完成素材侧检查；客户端未接入、未运行游戏验收。
