> 历史快照（2026-10-05）：本记录保留原验收经过，不能代表2026-10-08修后的当前像素。当前验收及SHA以根目录README、qa/final-visual-review.json为准。原接触图已清理，当前全帧图位于qa/contact。

# 普攻子任务交付

24/24正式帧：runtime/attack/E/01.png–12.png及runtime/attack/W/01.png–12.png。每帧30ms，第08帧事件attack-contact。两向均为独立内置AI姿态，不做镜像、复制、平移或插值补帧。

每帧有prompts/attack/<方向>-<帧>.txt、records/attack/<方向>/<帧>.generation.json、request.json、receipt.json。配置目标为任务授权的GPT Image2.5/max，真实tool参数没有model/quality选择器，真实返回未披露，submitted/actual均为null。W06一次网络错误单独记录，随后成功。

E-technical.json与W-technical.json均通过尺寸/alpha/SHA/记录/参考存在检查；全组共24个独立最终SHA。E-static-review.md和W-static-review.md记录实际逐图与总览静态复核。W09→10远侧后足收势向内变化已交主窗口慢放复核，不把静态检查当作动态通过。

source/attack中的24张原生图已在核对24张正式帧、prompt、receipt、SHA及当前参考完整后清除，共35,229,924字节；正式runtime帧SHA保持不变。每个generation记录的native和derivedFrom均保留原生SHA，标记deleted:true并注明保留策略及qa/attack/cleanup.json。所有文字生成证据继续保留，source/attack已无图片。未删除任何跨窗身份参考、宿主默认输出或其它对象资源。

正常、慢放、逐帧六组预览、manifest总表、SHA总表与客户端未验边界由主窗口统一汇总。客户端未读取、未接入，未执行Git操作。
