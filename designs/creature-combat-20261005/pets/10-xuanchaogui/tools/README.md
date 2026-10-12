# 玄潮龟验收与预览工具

只读取本只 `runtime` 与来源记录，不生成、修改或补齐正式姿态。

本机宿主 Python 已验证含 Pillow 12.3.0：

```powershell
& 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\work\image\designs\creature-combat-20261005\pets\10-xuanchaogui\tools\build_delivery.py'
```

默认将暂态检查写入 `preview/audit/manifest.json` 与 `preview/audit/validation.json`，六组辅助联系表写入 `preview/contact-sheets`。不完整时正常返回退出码 1。只生成 HTML 用 `--preview-only`；不需联系表加 `--no-contact-sheets`。最终由主任务运行 `--output-dir .`，才会输出角色根目录 `manifest.json` / `validation.json`。

可直接打开 `preview/index.html`，相对链接适用 `file://` 或局域 HTTP。六组各自有正常 / 0.25 慢放、暂停、前后帧、滑条、循环选项；也可全局同步控制。PNG 未到齐会明确显示缺失。无浏览器补帧或插值。可切白底／深底检查透明边缘，脚点标记只是约定坐标，不移动图像。

## 来源记录

优先读取每张 `01.png.generation.json`，其次 `01.generation.json`，兼容集中 `generation.json` 内按 `file` 精确匹配的独立条目。

原生生成记录按项目模型策略保存：`file`、`sha256`、`generatedAt`、`width`、`height`、`format`、`tool`、`route`、`configSnapshot`、`submittedParameters`、`actualModel`、`actualQuality`、`evidence`、`prompt`、`references`。未知实际型号／画质必须明确为 `null` 并附 `unverifiedReason`；检查不据目标回填实际值。

导出 sidecar 记录当前帧 `file`、`sha256`、`derivedFrom`、`operation`。`derivedFrom` 为对象或对象数组，各项含源 `file`、`sha256`、`generationRecord`。源图清理后保留文字记录并标 `deleted: true` 或 `removedAfterExport: true`；不会把合规清理等同来源遗失。`generationRecord` 支持原始 JSON 路径或嵌入记录对象。路径支持本角色根目录相对路径、记录旁相对路径或绝对路径。

逐帧检查尺寸、PNG/RGBA、透明与不透明像素、alpha 包围盒、边缘接触、文件 SHA 和像素 SHA、来源 SHA 与提示／参考可读取性。边缘接触作为警告交给目视复核。精确像素相同判重复；哈希不能识别所有镜像、平移、插值或解剖错误。

技术脚本本身不判定美术和动态通过。人工结论另存 `visual-review.json`，包含全部正式 PNG 的 SHA；仅在 68 张图与记录完全一致且技术错误为零时，将既有人工结论合并到本次 manifest。只要图片变化或出现技术错误，人工字段恢复待复核，不能自动沿用旧结论。客户端状态始终保持未接入。
