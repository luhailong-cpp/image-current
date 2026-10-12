# 汐螺普攻分工交接

2026-10-05。此记录仅覆盖本子任务负责的 attack E01–12、W01–06，共18张；W07–12由父任务接续。

- 18张均为独立内置 image_gen 单帧生成，已实际逐张查看生成图，并由本只 finalize_frame.py 导出1024×1024 RGBA PNG。没有复制、镜像、全图平移造帧或插值补帧。
- 每帧原生1254×1254 RGBA；统一整画布缩放1024/1254，E固定offset [0,28]，W固定 [0,-13]。没有按帧最低脚点对齐。
- 正式图片：runtime/attack/E/01.png–12.png，runtime/attack/W/01.png–06.png。
- 实际提示词：prompts/attack/<E|W>/<NN>.txt；每图来源与模型证据：records/attack/<E|W>/<NN>.json；实际调用返回摘要：receipts/attack/<E|W>/<NN>.json。
- 配置目标gpt-image-2.5-sunburst/max；submittedParameters.model/quality及actualModel/actualQuality均为null，工具未开放选择器也未披露实际值。目标不当作实际锁定证据。
- E04/W03首轮调用发生connection failed错误，各有attempt01-failure.json；同一内置入口重试成功。失败无图片产物。
- 技术核验见 records/attack/owned-validation.json：18/18尺寸、真alpha、导出SHA、native SHA、prompt/receipt引用通过；18个唯一图片SHA。alpha>16主体均完整留在画布，边缘低alpha细点不等同主体裁切。
- 单帧已实看：E斜前朝右下、W真斜后朝左上；同一近钳执行收回、张开、前送，E07闭钳命中，E08–12回收并收势。另一钳守备，六步足保持合理根部与透视遮挡，未见明显多肢或换钳。
- 动态连播、慢放和全包美术验收由父任务执行，目前本记录不宣称动态通过；未接入游戏。独立生成仍有小幅轮廓/材质变化，尤其E01–02到E03的壳轮廓宽度残差，需在全组预览中评估。

## W06接续

原生：C:/Users/luyua/.codex/generated_images/01a10bb6-d490-72f1-a352-2ded1308726d/exec-51af280b-07c6-4b9a-a528-7393812a520c.png。

W06维持壳背主导、壳尖朝右下，脸藏在壳后，仅眼柄轮廓可见。左上近钳前送到半程且钳口已接近闭合。W07应沿同一连接略再上伸并完全闭钳，保持左侧留白，不转胸向镜头；随后同钳回收。W01中性原生路径在对应records中可查。

原生图目前仍被本次参考链及接续所需引用，未删除；全组最终引用确认后由父任务按根保留规则统一清理。未改公共文件、旧身份图、其它角色、客户端、兄弟仓库或Git状态。
