# 霞角鹿战斗素材交接

交付对象为 Image 原有宠物「霞角鹿」，唯一写入范围为本目录。原有身份、四足鹿解剖和颈部装饰沿用 [TASK.md](TASK.md) 与 [POSES.md](POSES.md)；本包提供受击、普攻、施法 E/W 六组，共 68 张正式透明 PNG。

## 接入规格

| 字段 | 值 |
|---|---|
| 正式入口 | [manifest.json](manifest.json) 与 [runtime](runtime/) |
| 图像 | 1024×1024、PNG、RGBA、真实 alpha |
| 路径 | `runtime/<hit|attack|cast>/<E|W>/<01…nn>.png` |
| E | 斜前朝右下，敌方朝向 |
| W | 真斜后朝左上，我方朝向；独立绘制 |
| 脚点 | 顶部原点 `[512,942]`，近似整数像素 |
| pivot | 左下原点归一化 `[0.5,0.08]` |
| 导出 | 原生 1254×1254 完整画布统一缩放到 1024×1024 |
| 移动 | 无走路、跑步、移动循环或位移序列 |
| 客户端验收 | `not-tested`，本任务未读取或接入客户端 |

| 动作 | 每向帧数 × 时间 | 总时间 | manifest 中的关键事件 |
|---|---|---:|---|
| `hit` | 6 × 40 ms | 240 ms | 01 `hit-start`；03 `recoil-peak`；06 `settled` |
| `attack` | 12 × 30 ms | 360 ms | 01 `windup-start`；04 `windup-peak`；07 `contact`；12 `settled` |
| `cast` | 16 × 45 ms | 720 ms | 01 `gather-start`；08 `charge-peak`；10 `release`；16 `settled` |

按 manifest 的帧序与毫秒时长播放，保留统一画布和 pivot。自然受击反冲、蓄力、抬肢与回位已经包含在帧内，不应为每帧单独调整脚点或翻转 W。事件名描述视觉节点，尚未绑定客户端伤害、特效或战斗逻辑；接入时由负责方确认映射。APNG 循环用于观察，不定义游戏内动作的循环策略。

## 验收依据与限制

- [validation.json](validation.json) 记录缺帧、尺寸、RGBA/alpha、SHA、重复与来源引用检查；其 `technicalStatus` 只代表这些技术项目。
- [visual-review.json](visual-review.json) 记录全帧静态检查、正常和慢放播放抽查及关键帧逐帧结论，包括方向、四足支撑、晶角/短尾数量、回收动作及相邻帧衔接。素材结论为 `accepted-with-notes`；W 受击 04→05 回位偏快，已保留备注。最终结论以该文件和 [STATUS.md](STATUS.md) 为准，不能由 68/68 数量推定。
- [SHA256SUMS.txt](SHA256SUMS.txt) 对应正式 PNG；[最终交付审计](provenance/final-delivery-audit.json) 和 [cleanup.json](cleanup.json) 对应最新源链与清理证据；[前期逐图来源审计](provenance/audit-final.json) 保留历史。修图后应使用更新的导出记录与 SHA。
- [preview/index.html](preview/index.html) 提供六组正常、0.25 倍慢放和逐帧；各组独立 APNG 与总览见 [README.md](README.md)。

来源保留配置目标 `gpt-image-2.5-sunburst / max`；工具实际模型和质量未披露，相关字段为 `null`。不能向接入记录填写“已验证为指定模型”。清理后历史原生/拒稿路径是来源记录，正式读取入口始终为 `runtime`；重建脚本只可复验正式文件及重建预览，不能复原已删 AI 图片。

本交接不代表客户端渲染、锚点、战斗事件或运行性能已通过。接入工作尚未执行；本任务未操作客户端、兄弟仓库或 Git 共享状态。公共规范、旧身份图和其他宠物目录保持只读。
