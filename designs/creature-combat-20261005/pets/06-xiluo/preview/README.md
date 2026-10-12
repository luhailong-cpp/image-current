# 汐螺动画预览

正式素材是上一层 runtime 中的 1024×1024 PNG。本目录 WebP 为 512×512 透明播放预览；只按顺序打包正式帧，不插值、不合成新姿态。

|动作|E 正常|E 0.25×|W 正常|W 0.25×|
|---|---|---|---|---|
|受击|[播放](hit-E-normal.webp)|[慢放](hit-E-slow.webp)|[播放](hit-W-normal.webp)|[慢放](hit-W-slow.webp)|
|普攻|[播放](attack-E-normal.webp)|[慢放](attack-E-slow.webp)|[播放](attack-W-normal.webp)|[慢放](attack-W-slow.webp)|
|施法|[播放](cast-E-normal.webp)|[慢放](cast-E-slow.webp)|[播放](cast-W-normal.webp)|[慢放](cast-W-slow.webp)|

[逐帧/深浅背景交互页](../preview.html) · [每个媒体的帧数、精确时长和源 SHA](media-manifest.json)

WebP 帧时已通过解码检查。实时视觉连播与游戏内衔接尚未验证，详见 [检查记录](../qa/visual-review.json)。
