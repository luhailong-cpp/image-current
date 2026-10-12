# 月弦师素材交接

交付范围仅Image原月弦师双向受击、攻击、施法共68张PNG；没有移动动作。已确认的鞋位问题已修复，静态/技术检查通过；实际连播和客户端运行仍未验。

正式来源`runtime/<hit|attack|cast>/<E|W>/<NN>.png`。manifest绑定文件SHA、帧序和时长：hit6×40ms，attack12×30ms，cast16×45ms。建议视觉事件点hit03 impact、attack07 release、cast11 release，最终战斗事件需由客户端校准。

PNG RGBA1024方图，pivot[0.5,0.08]，顶部锚点[512,942]。禁止图集自动旋转或按各帧alpha包围盒重新对齐；全部采用相同整画布导出变换。E斜前右下，W斜后左上；左手托琴、右手拨弦。

正常与0.25倍预览在preview.html和preview/*.apng。后续实际播放重点检查E攻击05–08腕部轨迹、末帧→戒备；W受击反冲恢复、攻击脚位小幅变化；施法衰光和回位。完整当前静态证据见VERIFICATION.md，不把编码或文件齐全当实际播放/游戏运行通过。

逐图记录中的实际model/quality仍为工具未披露的null；目标Sunburst/max不能冒充实际型号。原生/拒稿清理后保留SHA、prompt、receipt及输入来源文字，运行和预览仅依赖正式PNG。未自行接入客户端或发布，未读取兄弟仓库，未执行Git写操作。
