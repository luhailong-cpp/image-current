# 赤枪少女 · 成品交接

196张动作成品已完成本轮全动作手脚复核，替换21张跑步帧。当前图片runtime/，逐图清单manifest.json和delivery-current.json。客户端尚未接入。

| 动作 | 方向数 | 每方向帧数 | 每帧 | 一圈 |
|---|---:|---:|---:|---:|
| 跑步 | 8 | 16 | 60ms | 960ms |
| 受击 | 2 | 6 | 40ms | 240ms |
| 普攻 | 2 | 12 | 30ms | 360ms |
| 施法 | 2 | 16 | 45ms | 720ms |

跑步连续支撑位置各两张独立姿态，沿真实运动方向推进。运行目录编号01起已是播放顺序，不可再次应用历史源帧重排。所有图片1024×1024 RGBA，保持各帧独立姿势。普攻06为接触标记，施法09为释放标记。

本轮内容：
- E14：修正近侧摆动腿与远侧支撑腿的前后遮挡，保持13→14→15支撑归属连续。
- W09–12：修正提前换支撑腿的画面归属，保留同一腿的连续四位置推进。
- SW15/16：收回过长的侧向后蹬，保持自然屈膝、前掌支撑及两张独立姿态。
- NW11/12：减小突增的后蹬跨距；NW02/03/05–16同时修正下枪杆与枪尾偏离上枪杆延长线的问题。

预览：preview/index.html为全部动作；preview/all-directions.html为八方向同屏；preview/timing-grounding.html为跑步放大逐帧。均支持正常、¼慢放、暂停和逐帧。

检查范围及限制见FINAL_REVIEW.md；逐帧当前SHA判读见full-limb-review-20261004/current-frame-review.json；发布来源见同目录publish-report.json与publish-journal.json。客户端接入时需再验证世界坐标、地面层级及动作状态切换。

原生1254输出和1024导出分开记录。每张图片旁generation.json保留来源SHA；manifest.json的nativeGenerationRecord可查提示词和内置工具回执。实际模型和质量没有披露，记录为null。成品验证后清理原图、拒稿和过程图，只留正式图及文字来源，见retention-report.json。
