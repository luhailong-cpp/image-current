# 云啾啾帧导出与检查

此脚本只读取本只 `records/*.json` 指向的既有单帧 PNG，不调用 AI，不补缺帧，不插值、不镜像、不逐帧对脚、不删除素材。读取及写入范围限制在本只目录；身份/画法参考只保留记录中的文字路径，不读取外部素材像素。

当前可用 Python：`C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`，已确认 Pillow 12.3.0。

在本只目录运行（PowerShell）：

```powershell
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/build_combat.py plan
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/build_combat.py export
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/build_combat.py verify
```

`plan` 默认只读，不产生文件；`export` 处理存在且可验证的原生帧，写 runtime、派生记录、manifest、validation、六组 contact sheet 和 `preview/index.html`；`verify` 不改角色 PNG，只核验既有成品并更新报告/预览。退出码 0 表示技术完整通过，1 表示缺帧，2 表示存在技术/来源错误；任一状态均不代表美术或动态通过。

源文件与记录的 SHA/原生尺寸必须一致。存在多个选中记录会拒绝该帧；重试的旧记录设 `selected:false` 或 `status:"superseded"`。已有 runtime 像素不同会拒绝覆盖，主线程确认记录指向当前选定版本后可显式加 `--overwrite`。脚本不自行选择最新文件，也不扫描他只目录。

## 记录格式

一张独立生成帧一份 JSON，建议 `records/hit-E-01.json`。完整字段模板见 `record.example.json`；它不在 `records/` 下，不会误作生成证据。`file`、`prompt` 使用本只目录相对路径；generation receipt 可用 `evidence` 记录其相对路径及工具字段。`references` 存真实附图路径与用途。

必须区分 `configSnapshot` 目标、`submittedParameters` 实际参数、`actualModel`/`actualQuality` 实际返回值。工具不暴露参数时参数值为 null；返回未披露型号/质量时实际值为 null，说明原因。脚本不会根据当前配置或提示词补填型号。

没有 action/frame 或 `kind:"design"` 的静态设计记录会忽略。每帧 `visualStatus` 默认 pending；实际查看后才能写 passed。`event` 默认 null，由动作设计者按真实阶段填写，脚本不臆定攻击命中时刻。

## 坐标

同方向跨全部动作必须有相同原生画布尺寸。1024×1024 RGBA 原生 PNG 字节复制，保留 SHA；其它尺寸以整张画布统一等比缩放居中（不会按 alpha 包围框重新排版）。不同画布尺寸混入同一方向会报错。方向统一导出参数可以经 `--transforms tools/export-transforms.json` 提供，格式见 `transforms.example.json`。原生 1024 画布仍强制保持无位移、无缩放。自定义变换裁到可见像素会拒绝。

记录使用顶端原点脚点 `[512,942]` 与左下归一化 pivot `[0.5,0.08]`（规范整数像素四舍五入）；预览十字显示固定脚点，实际是否站稳需看原图和动作，不通过导出来遮掩。

若最终源 PNG 已按保留政策清理，在源记录添加 `sourceRetention:{"status":"deleted-after-export","deletedAt":"含时区时间","reason":"成品与引用已核验"}`，保留原 SHA/原生尺寸/生成证据。`verify` 可通过成品 `.png.generation.json` 检查来源链；缺失源但未记录清理会报错。脚本不会执行清理。

## 预览和检查边界

`preview/index.html` 内嵌 manifest，支持直接 file:// 打开，不依赖网络或 fetch。六组各显示全部约定时间槽，缺帧不跳过、不复用邻帧。支持 1× / 0.25×、同时播放、逐帧滑块、上一帧/下一帧以及固定脚点；无滤镜、插帧或图片混合。浏览器刷新率会限制 30ms 的可见帧时序，慢速/逐帧用于补充检查。

技术检查包含尺寸、RGBA、透明背景、来源 SHA/记录、缺帧、可见像素完全重复、仅平移的重复及跨方向精确镜像；边缘接触为需人工检查的警示。同时记录 alpha>0、>16、>128 三种包围框与触边状态，避免把极低 alpha 碎点直接当成主体裁切；不修改任何羽缘。它不能自动判定肢体数、物种、身份、真正后视、支撑、手翼连续性或动作美感。六组连播及逐帧实际检查结果应由主线程保存，不能把自动报告写成美术/客户端通过。
