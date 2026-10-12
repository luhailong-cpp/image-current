# 玄潮龟 hit/E04 半回弹返修终检

2026-10-08。仅替换 `runtime/hit/E/04.png`，内置 image_gen 单帧真实重绘，未复制、平移、镜像或插值生成姿态。

已实际查看原生 E/W 身份图、主要画法图、E03/E04旧版/E05、新生成结果以及最终 1024 正式图。新 E04 头冠目视约 y=500，位于 E03 约 y=566 与 E05 约 y=411 之间；头颈有短可见米白喉部，眼半开，近侧前足仍屈曲。背甲、桂枝朱结左侧归属、单尾、可见三爪和真实 E 斜前视角保持。E04 不再一帧接近全部回升。坐标是目视定位，不是自动关节识别。

本次只做单帧与相邻帧静态复核；没有声称正常/慢放连播通过。全序列连播由根任务在重建预览后检查。

- 正式图：`runtime/hit/E/04.png`，1024×1024 RGBA，SHA256 `398cfe35fcc6fdbfb43d65d0e1a726ce22744f66099e4a789a54d09e22932965`。
- 原生图：1254×1254 RGBA，统一全画布 Lanczos 导出到1024；无逐帧轮廓定位或平移。
- Alpha 极值 0–255；alpha>8 轮廓 [43,162,1013,895]，alpha>128 轮廓 [45,163,1012,894]；主体未裁切。全 alpha bbox [0,4,1016,990] 含低 alpha 像素，交由根任务棋盘/深浅底实看。
- E03/E04/E05 三张 SHA 各不相同。
- 新准确提示词：`prompts/hit/E/04-rebound-final.txt`；receipt：`provenance/hit/E/04.receipt.json`；原生与正式导出记录：`provenance/hit/E/04.generation.json` 和 `runtime/hit/E/04.png.generation.json`。
- 目标沿用本批 GPT Image 2.5/max；实际 submitted model/quality 与 actualModel/actualQuality 均为 null，工具无选择器且未披露返回版本，未将目标冒称实测版本。
- E05 原始输入的 E04 SHA 仍为 `c896e1c253d750b6aef3f7338441e2a9513a60f2a6db850d272e527be321dd18`。实际提交与历史 SHA 均未改写。历史记录连接见 `provenance/hit/E/04-historical-reference-link.json`，旧 receipt 与导出/生成文字记录保留；旧正式图片已由新图原路径替换，无图片回退副本。

没有读取客户端或兄弟仓库，没有 Git 操作，没有变更其它正式帧。原生生成缓存不在本次唯一可写目录，本子任务未删除；由主任务按权限与素材保留规则决定最终清理。
