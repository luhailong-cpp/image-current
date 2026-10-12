# 苍嶂麟交付接手

本只目录内的 68 张 `runtime` PNG 已完成；最终索引为 `manifest.json`，哈希为 `SHA256SUMS.txt`。无需从其它仓库取素材或补对象。本任务未提交 Git，没有客户端改动。

接入方应读取 manifest 的 action、direction、durationMs、pivot、anchorTopLeft 与 event；E 斜前右下，W 真斜后左上。hit/attack/cast 每向分别 6/12/16 帧，40/30/45ms，不能按固定同一帧率播放。普攻事件第07帧、施法事件第10帧仅为美术建议。

原生1254到1024的固定导出为整幅缩960、偏移(32,6)。不要再次逐帧裁到内容边界或按最低蹄对齐，否则会改变原地反冲与重心。若游戏使用图集，需保留每帧完整画布或提供等价的trim offset，透明边缘不要直接改成不透明底色。

人工检查包括全部帧、六组原速与0.25倍浏览器播放抽查、逐帧控制；记录位于 `qa/final-review.json`，并绑定当前成品 SHA。游戏内朝向、排序、pivot、透明混合、事件和待机衔接仍需在后续获授权的客户端任务中测试，本次不宣称引擎通过。

所有 prompt、来源 receipt、配置目标/实际未知参数和拒稿修订文字记录已保留，manifest逐帧链接正式生成记录。旧分组报告仅是过程证据。原身份与主要画法参考保持外部只读，正式 runtime 和 HTML 预览不依赖已清理的 staging 图片。

可直接打开 `preview/index.html` 看六组，或 `preview/{hit,attack,cast}-{E,W}.html` 看单组。重新验证/生成这些文档用 `build_delivery.py`，不需要 API 凭证；它只做本地检查和预览构建。
