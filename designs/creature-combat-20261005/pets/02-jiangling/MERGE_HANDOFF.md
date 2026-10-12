# 绛铃接入交接

只涉及本宠目录；未Git提交、推送、切分支或改索引，未读取客户端/兄弟仓库。

- 正式输入：`runtime/<hit|attack|cast>/<E|W>/<两位帧号>.png`，68张1024透明PNG。
- 清单：`manifest.json`，逐帧含文件、SHA、方向、动作、帧号、durationMs、pivot、event及sourceRecord。
- E是斜前朝右下；W是真正斜后朝左上。不得用镜像代替方向。
- 帧数/时长：hit 6×40ms；attack 12×30ms；cast 16×45ms。建议事件分别在03/07/10；实际客户端逻辑须独立确认。
- 底部原点pivot `[0.5,0.08]`；顶部坐标锚点 `[512,942]`。悬浮角色没有真实地面足点；不要按每帧最低鞋底重新对齐。
- RGBA Alpha保持原生边缘后统一全画布缩放，未加场景。正常反冲和衣袖/丝带/扇铃变化保留在帧中。
- 正常/慢放/逐帧预览见 `preview-native.cmd`、`preview.html` 与 `previews/`；角色身份和手足检查见 `qa/visual-review.json`。六组原生播放的正常/0.25倍速现场截图采样已完成，详细方法及边界见 `qa/native-playback-review.json`。
- 模型目标与实际未知字段必须一同保留，不能将本包标成已显式锁定某个API型号/质量。

待接入方验证：游戏内实际大小和落点、排序与遮挡、游戏内六组播放、出手事件、回收与待机衔接。本地原生播放采样已完成，未发现新增素材问题；没有客户端验证或游戏帧率保证。

核验命令（本机bundled Python或带Pillow的Python）：

```text
python tools/check_delivery.py --contacts --manifest --require-complete
python tools/make_previews.py
python tools/check_previews.py
python tools/checksum_packet.py
python tools/checksum_packet.py --verify
```

最终验收摘要合并写入manifest后，变更记录需重新生成SHA清单；这些工具不生成或补全AI姿态。
