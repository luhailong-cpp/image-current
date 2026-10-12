import json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
report=json.loads(r'''{
  "schemaVersion": 1,
  "reviewDate": "2026-10-05",
  "reviewer": "/root/finish_n_nw",
  "scope": "run/N、NE、NW、E当前64帧：肩—肘—腕—手指/持物及髋—大腿—膝—胫—踝—鞋头全链。",
  "frameDurationMs": 60,
  "cycleDurationMs": 960,
  "cycleFrames": 16,
  "timingAuthority": "2026-10-05用户最新要求覆盖旧75ms。",
  "status": "静态逐帧及相邻相位复核完成；完整循环播放交主窗口。",
  "staticVisualInspectionCompleted": true,
  "dynamicPlaybackReviewed": false,
  "clientIntegrated": false,
  "method": [
    "实际逐张打开64张runtime全图检查；发生本轮替换的帧全部重新打开，检查相机、双手连接、腿脚保留。",
    "N新12张摆臂均结合保留02/03/10/11实际逐张看，检查前后换相和首尾邻接，不以哈希/计数代替动作判断。",
    "实际查看09弓少女N/NE/NW/E联系表，参考同向运动平面；不把其帧号等同本角色相位，不复制其持物。",
    "此前用户截图与视频参考仅用于识别侧翻/纵向运动原则，原视频尺寸小且遮挡，不作为本角色逐帧鞋细节证据。"
  ],
  "historicalFindings": [
    {
      "issue": "NE02/03支撑靴前脸朝镜头，不能以抬跟单独解释方向。",
      "status": "resolved",
      "resolution": "分别AI局部重画后跟纵缝及远端朝NE的鞋头，保留双手/另腿/相机。",
      "resolvedFiles": [
        "runtime/run/NE/02.png",
        "runtime/run/NE/03.png"
      ],
      "evidence": "review/NE_02_03_wholeaxis_correction_20261005.json"
    },
    {
      "issue": "N大部分帧双臂在相似高位，07/11/14出现孤立下落，缺少肩肘交替连续性。",
      "status": "resolved_static",
      "resolution": "12张独立AI局部摆臂修正，02/03/10/11保留为中间位；新完整N16静态邻帧已实看，未将像素变化当充分摆臂。",
      "resolvedFiles": [
        "runtime/run/N/00.png",
        "runtime/run/N/01.png",
        "runtime/run/N/04.png",
        "runtime/run/N/05.png",
        "runtime/run/N/06.png",
        "runtime/run/N/07.png",
        "runtime/run/N/08.png",
        "runtime/run/N/09.png",
        "runtime/run/N/12.png",
        "runtime/run/N/13.png",
        "runtime/run/N/14.png",
        "runtime/run/N/15.png"
      ]
    },
    {
      "issue": "E14右臂在13→14→15中单帧前收。",
      "status": "resolved",
      "resolution": "主窗口局部修正后已实看13/14/15，右肩肘保持后摆弧。",
      "resolvedFiles": [
        "runtime/run/E/14.png"
      ]
    },
    {
      "issue": "NW09符牌单帧倒向下，握点从下沿跳到上端。",
      "status": "resolved",
      "resolution": "主窗口修正左手/牌后已实看08/09/10，牌顶向上且握下沿。",
      "resolvedFiles": [
        "runtime/run/NW/09.png"
      ]
    }
  ],
  "frames": [
    {
      "file": "runtime/run/N/00.png",
      "action": "run",
      "direction": "N",
      "frame": 0,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左肩前收、左肘屈曲牌近肩；右肩肘后摆，握杖腕降腰侧且连通。",
      "wholeLegAxisObservation": "右前载膝踝在髋下，支撑靴后跟居中朝N；左膝后收露底。",
      "adjacentFrames": [
        15,
        1
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/01.png",
      "action": "run",
      "direction": "N",
      "frame": 1,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左牌臂仍前摆、右杖臂低位开始回收；腕随前臂转，未换握侧。",
      "wholeLegAxisObservation": "右膝较00屈，鞋后跟顺小腿轴；左脚回收略降而未横转。",
      "adjacentFrames": [
        0,
        2
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/02.png",
      "action": "run",
      "direction": "N",
      "frame": 2,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "双臂经过中位，右腕由01低位上行、左臂由前摆转后摆；保留原帧可连接03/04。",
      "wholeLegAxisObservation": "右腿承重经过，短胫骨直连后跟；左腿后折，鞋底长轴近纵向。",
      "adjacentFrames": [
        1,
        3
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/03.png",
      "action": "run",
      "direction": "N",
      "frame": 3,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "双肩中段转移，右杖臂继续向前、左牌臂开始向后；没有孤立握点漂移。",
      "wholeLegAxisObservation": "右支撑腿承重，踝鞋后跟居中，左靴保持屈膝后摆。",
      "adjacentFrames": [
        2,
        4
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/04.png",
      "action": "run",
      "direction": "N",
      "frame": 4,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：右肩前摆、肘屈，杖在肩前；左肩后摆、肘伸，左手直接握牌下沿。",
      "wholeLegAxisObservation": "右后蹬前掌阶段，足底俯仰随胫骨；左膝收回，不侧叉。",
      "adjacentFrames": [
        3,
        5
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/05.png",
      "action": "run",
      "direction": "N",
      "frame": 5,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左后摆腕进一步下移，右肘保持前收；两臂真实摆动，手指连接正确。",
      "wholeLegAxisObservation": "右跟抬起、膝仍自然屈，左脚底纵向；未把自然后蹬改锁膝。",
      "adjacentFrames": [
        4,
        6
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/06.png",
      "action": "run",
      "direction": "N",
      "frame": 6,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：右臂前摆至高位部分被头遮，左臂后摆；持物仍随肩肘运动。",
      "wholeLegAxisObservation": "左前端初接地，膝胫轴沿髋下N平面；右腿屈膝回收。",
      "adjacentFrames": [
        5,
        7
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/07.png",
      "action": "run",
      "direction": "N",
      "frame": 7,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：右腕前收稍降，左牌后摆稍回，独立衔接06和08。",
      "wholeLegAxisObservation": "左膝屈承接初接，左靴跟与胫骨一致，右脚悬摆无外扭。",
      "adjacentFrames": [
        6,
        8
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/08.png",
      "action": "run",
      "direction": "N",
      "frame": 8,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：右杖臂前、左牌臂后；左掌直接握无柄矩形牌下沿，拒稿黑柄已无。",
      "wholeLegAxisObservation": "左腿前载，后跟近竖直在胫骨下；右脚底朝后，髋下步宽自然。",
      "adjacentFrames": [
        7,
        9
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/09.png",
      "action": "run",
      "direction": "N",
      "frame": 9,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左腕从后摆低点回收，右腕从前摆高点下落，接10中位；无牌柄或换手。",
      "wholeLegAxisObservation": "左膝承重更屈，支撑足长轴朝N；右脚屈膝回收略下降。",
      "adjacentFrames": [
        8,
        10
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/10.png",
      "action": "run",
      "direction": "N",
      "frame": 10,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "双臂经过中位，左肩将前摆、右肩将后摆；手腕与同侧袖口连续。",
      "wholeLegAxisObservation": "左腿承重经过，膝—踝—后跟没有横向折线；右回收脚底与小腿一致。",
      "adjacentFrames": [
        9,
        11
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/11.png",
      "action": "run",
      "direction": "N",
      "frame": 11,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右杖腕从10开始向腰侧落，左牌肘前收，可连续接新12/13；原孤立下落变成中间相位。",
      "wholeLegAxisObservation": "左支撑小腿近纵向，后跟接胫骨；右膝屈脚底朝后。",
      "adjacentFrames": [
        10,
        12
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/12.png",
      "action": "run",
      "direction": "N",
      "frame": 12,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左牌臂前、右杖臂后，右肩到袖口到腕可连续追踪。",
      "wholeLegAxisObservation": "左足后蹬，鞋底随踝俯仰，右回收脚不横开，保留原自然屈膝。",
      "adjacentFrames": [
        11,
        13
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/13.png",
      "action": "run",
      "direction": "N",
      "frame": 13,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：右后摆腕较12略低，左牌保持肩前，右腕未倒折。",
      "wholeLegAxisObservation": "左后蹬跟更抬，靴尖仅小幅透视偏转，未见独立踝侧拧；右脚后收。",
      "adjacentFrames": [
        12,
        14
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/14.png",
      "action": "run",
      "direction": "N",
      "frame": 14,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左肩肘前收，右肩肘后开接13，腕在腰侧，臂长仍为短比例。",
      "wholeLegAxisObservation": "右前端初接、靴后跟朝N，左膝折回；下身相位和足位保留。",
      "adjacentFrames": [
        13,
        15
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/N/15.png",
      "action": "run",
      "direction": "N",
      "frame": 15,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮修正：左牌前收，右杖后摆开始回收接00；握点仍在短柄，双手不交叉。",
      "wholeLegAxisObservation": "右脚承接初落，膝屈和脚尖方向同面；左脚回摆稍偏左为整体胫骨方向，未单独外扭。",
      "adjacentFrames": [
        14,
        0
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/00.png",
      "action": "run",
      "direction": "NE",
      "frame": 0,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左肩屈肘前收牌近肩；右肘稍后开，手拳包住杖柄上端，腕顺前臂。",
      "wholeLegAxisObservation": "右腿承重，膝落在髋下，后跟近侧、鞋头向NE远处；左腿回收露底。",
      "adjacentFrames": [
        15,
        1
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/01.png",
      "action": "run",
      "direction": "NE",
      "frame": 1,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂较00展开少许，右杖腕低于00；可见肩肘变化，握持身份不变。",
      "wholeLegAxisObservation": "右小腿短而屈，脚尖随NE方向收向右上；左靴随屈膝后收。",
      "adjacentFrames": [
        0,
        2
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/02.png",
      "action": "run",
      "direction": "NE",
      "frame": 2,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘前摆承接01，左牌臂向后；两腕与同侧袖口连续。",
      "wholeLegAxisObservation": "本轮修正：右支撑靴近侧改为黑后跟纵金缝，远端鞋头收向右上，屈膝和后蹬未改。",
      "adjacentFrames": [
        1,
        3
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/03.png",
      "action": "run",
      "direction": "NE",
      "frame": 3,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "两臂延续02独立相位，右杖手位置稳定在柄部，左牌仍握下沿。",
      "wholeLegAxisObservation": "本轮修正：右靴不再大前掌朝镜头，后跟抬起并朝近侧、鞋尖朝NE；另一腿原位回收。",
      "adjacentFrames": [
        2,
        4
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/04.png",
      "action": "run",
      "direction": "NE",
      "frame": 4,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘更屈，雷杖近脸侧；左牌腕降至腰后，没有出现第三手。",
      "wholeLegAxisObservation": "左前侧初接地，靴后跟近侧、鞋头远右；右腿屈膝回收沿同向平面。",
      "adjacentFrames": [
        3,
        5
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/05.png",
      "action": "run",
      "direction": "NE",
      "frame": 5,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右上臂前伸、肘稍打开，左牌腕较04后伸；未靠独立道具漂移表现摆臂。",
      "wholeLegAxisObservation": "左膝踝短链承重，右脚后收露底，鞋底长轴随回收小腿。",
      "adjacentFrames": [
        4,
        6
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/06.png",
      "action": "run",
      "direction": "NE",
      "frame": 6,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肩前摆达到高点，左肘后摆牌向后；握杖手不跨接到左臂。",
      "wholeLegAxisObservation": "左腿前载、右膝回收；支撑足远端未横向外开，髋下间距自然。",
      "adjacentFrames": [
        5,
        7
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/07.png",
      "action": "run",
      "direction": "NE",
      "frame": 7,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右腕稍下落延续前摆，左牌肘继续后开；牌底仍与左手接触。",
      "wholeLegAxisObservation": "左支撑靴远端右上，右脚底近纵向；没有从膝到踝突然转侧。",
      "adjacentFrames": [
        6,
        8
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/08.png",
      "action": "run",
      "direction": "NE",
      "frame": 8,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肩肘开始收回，左臂在腰后；两手握点随前臂整体移动。",
      "wholeLegAxisObservation": "左腿承重经过，后跟与小腿连通；右腿后折回收。",
      "adjacentFrames": [
        7,
        9
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/09.png",
      "action": "run",
      "direction": "NE",
      "frame": 9,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右腕略前上、左牌臂开始回收；局部有袖口摆动但未见腕倒折。",
      "wholeLegAxisObservation": "左足继续承重，右回收靴露底随胫骨方向，不单独横转。",
      "adjacentFrames": [
        8,
        10
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/10.png",
      "action": "run",
      "direction": "NE",
      "frame": 10,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘仍前侧，左牌腕上移进入过渡；双手相位较09有变化。",
      "wholeLegAxisObservation": "左腿向后支撑，右屈膝较展开；可见鞋底来自屈膝和俯仰，未确证踝横翻。",
      "adjacentFrames": [
        9,
        11
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/11.png",
      "action": "run",
      "direction": "NE",
      "frame": 11,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肩稍回、左牌继续抬；均保持原解剖手侧。",
      "wholeLegAxisObservation": "左脚后蹬抬跟，右脚回摆，鞋跟/前掌俯仰与10的回收阶段连续。",
      "adjacentFrames": [
        10,
        12
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/12.png",
      "action": "run",
      "direction": "NE",
      "frame": 12,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂前摆近肩，右杖臂后开降到腰侧；肩肘两端相反变化清楚。",
      "wholeLegAxisObservation": "右腿开始前接触，右靴后跟近下、鞋头远右上；左回收腿在后方。",
      "adjacentFrames": [
        11,
        13
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/13.png",
      "action": "run",
      "direction": "NE",
      "frame": 13,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右杖手较12更低，左肘保持前收；握柄未飞离手掌。",
      "wholeLegAxisObservation": "右膝稍屈承重，靴长轴仍朝右上；左底面随膝后收。",
      "adjacentFrames": [
        12,
        14
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/14.png",
      "action": "run",
      "direction": "NE",
      "frame": 14,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂前收、右臂后摆，雷杖低位随手，不是双手固定。",
      "wholeLegAxisObservation": "右支撑腿纵向置于髋下，脚趾远右上；左膝后折保持窄幅。",
      "adjacentFrames": [
        13,
        15
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NE/15.png",
      "action": "run",
      "direction": "NE",
      "frame": 15,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌手与肩相近、右肘低位开始回收接00，握持仍正确。",
      "wholeLegAxisObservation": "右足承重、左足悬摆，双腿没有侧向张叉；足端朝向可接00。",
      "adjacentFrames": [
        14,
        0
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/00.png",
      "action": "run",
      "direction": "NW",
      "frame": 0,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌前摆近脸，右杖臂后伸在腰侧；两侧肩肘连接清楚。",
      "wholeLegAxisObservation": "右支撑腿沿髋后方斜向右下延伸，靴后跟近右、鞋头朝远左；非横向分腿。",
      "adjacentFrames": [
        15,
        1
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/01.png",
      "action": "run",
      "direction": "NW",
      "frame": 1,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌腕较00抬高少许，右腕后伸维持柄部握持。",
      "wholeLegAxisObservation": "右膝更屈、踝靴仍随NW/SE纵向平面，左腿后收露底。",
      "adjacentFrames": [
        0,
        2
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/02.png",
      "action": "run",
      "direction": "NW",
      "frame": 2,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘后开略上抬，左肩前收持牌，腕不反折。",
      "wholeLegAxisObservation": "右腿承重经过、鞋头朝左远端，膝胫轴未从髋侧折出。",
      "adjacentFrames": [
        1,
        3
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/03.png",
      "action": "run",
      "direction": "NW",
      "frame": 3,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌肘展开、右肩向前转换，双手仍在各自袖口延长线上。",
      "wholeLegAxisObservation": "右腿向后延展而非向右侧劈开；左脚收起有底面斜透视，踝接小腿。",
      "adjacentFrames": [
        2,
        4
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/04.png",
      "action": "run",
      "direction": "NW",
      "frame": 4,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右杖臂明显前摆上抬，左牌臂后摆下移，握持牢固。",
      "wholeLegAxisObservation": "右后蹬腿连续髋—膝—踝向后延伸；露底是后蹬俯仰，足长轴未单独横拧。",
      "adjacentFrames": [
        3,
        5
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/05.png",
      "action": "run",
      "direction": "NW",
      "frame": 5,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘屈且高位、左肘后伸更低，形成04的后一相位。",
      "wholeLegAxisObservation": "右腿蹬离稍更展开，靴底角变化随小腿后展；左腿向前回收。",
      "adjacentFrames": [
        4,
        6
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/06.png",
      "action": "run",
      "direction": "NW",
      "frame": 6,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂腰后低位、右杖臂在前侧，保持握牌下沿。",
      "wholeLegAxisObservation": "左足初落、右屈膝后收，支撑左鞋尖指向NW远左，不朝画面右侧翻。",
      "adjacentFrames": [
        5,
        7
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/07.png",
      "action": "run",
      "direction": "NW",
      "frame": 7,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右腕稍收、左牌后摆至近水平倾角，握点仍在牌下端。",
      "wholeLegAxisObservation": "左膝踝承重，右脚底顺回收腿长轴，鞋未从踝横向外折。",
      "adjacentFrames": [
        6,
        8
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/08.png",
      "action": "run",
      "direction": "NW",
      "frame": 8,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左肘后伸，左手在牌下沿，右肘前屈；摆动有肩关节参与。",
      "wholeLegAxisObservation": "左腿前载，踝下靴朝左远处；右后摆脚虽露底但轴随胫骨。",
      "adjacentFrames": [
        7,
        9
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/09.png",
      "action": "run",
      "direction": "NW",
      "frame": 9,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮已由主窗口修正：左手握牌下沿、牌顶朝上，08→09→10不再出现倒牌。",
      "wholeLegAxisObservation": "原左支撑与右回收腿保持，左鞋头远左、髋膝踝没有新增外叉。",
      "adjacentFrames": [
        8,
        10
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/10.png",
      "action": "run",
      "direction": "NW",
      "frame": 10,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂低位开始回收、右臂略收，两腕与前臂走向一致。",
      "wholeLegAxisObservation": "左脚承重经过、右腿后收，鞋底长轴与足踝连续。",
      "adjacentFrames": [
        9,
        11
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/11.png",
      "action": "run",
      "direction": "NW",
      "frame": 11,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂向前抬至脸侧，右肘收向躯干，连接正常。",
      "wholeLegAxisObservation": "左胫骨承重置于髋下，右回收底面斜向但无独立反转。",
      "adjacentFrames": [
        10,
        12
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/12.png",
      "action": "run",
      "direction": "NW",
      "frame": 12,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌前摆、右杖后伸，肩胛和袖口呈反向摆臂。",
      "wholeLegAxisObservation": "左脚后侧蹬离、靴后跟抬起；右膝折向后，露底沿原运动平面。",
      "adjacentFrames": [
        11,
        13
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/13.png",
      "action": "run",
      "direction": "NW",
      "frame": 13,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "两臂延续12并保持独立相位，牌底与左手相连。",
      "wholeLegAxisObservation": "左跟进一步抬起、右脚回摆更近躯干，后跟/脚尖关系未互换。",
      "adjacentFrames": [
        12,
        14
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/14.png",
      "action": "run",
      "direction": "NW",
      "frame": 14,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌近肩前收、右腕后摆低位，保持解剖手侧。",
      "wholeLegAxisObservation": "右前端初接、膝踝在髋后投影内；鞋头朝远左，左脚底回收。",
      "adjacentFrames": [
        13,
        15
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/NW/15.png",
      "action": "run",
      "direction": "NW",
      "frame": 15,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右臂后摆与14接近但肩肘不同，左牌手仍握下端。",
      "wholeLegAxisObservation": "右膝屈承接着地，左脚悬摆；支撑鞋未侧撇，与00连续。",
      "adjacentFrames": [
        14,
        0
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/00.png",
      "action": "run",
      "direction": "E",
      "frame": 0,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肩后伸雷杖在背后、左牌臂前屈，前后摆臂清楚。",
      "wholeLegAxisObservation": "侧向承重腿膝踝朝E，靴尖水平向右；后腿屈膝不横扭。",
      "adjacentFrames": [
        15,
        1
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/01.png",
      "action": "run",
      "direction": "E",
      "frame": 1,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右后摆肘略回收、左牌腕前侧，杖柄被右拳完整环握。",
      "wholeLegAxisObservation": "前载膝更屈、后脚收近臀，鞋头保持E运动平面。",
      "adjacentFrames": [
        0,
        2
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/02.png",
      "action": "run",
      "direction": "E",
      "frame": 2,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右臂由后摆回到身体侧中位，左肘前收，具备03前摆的中间位。",
      "wholeLegAxisObservation": "右向小腿与靴尖一致，后腿膝弯后收，未见外八。",
      "adjacentFrames": [
        1,
        3
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/03.png",
      "action": "run",
      "direction": "E",
      "frame": 3,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右杖臂前摆、左牌臂后摆，肩肘随持物换相而非换手。",
      "wholeLegAxisObservation": "支撑脚朝E，后脚屈膝朝下回收；腿未在画面横向旋出。",
      "adjacentFrames": [
        2,
        4
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/04.png",
      "action": "run",
      "direction": "E",
      "frame": 4,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘前伸保持握持、左肩后摆，腕没有倒折。",
      "wholeLegAxisObservation": "前腿抬膝伸踝向右，支撑腿朝E落地，两腿同一纵向运动面。",
      "adjacentFrames": [
        3,
        5
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/05.png",
      "action": "run",
      "direction": "E",
      "frame": 5,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "左牌臂开始回收、右杖前臂略收，手仍从各自袖口伸出。",
      "wholeLegAxisObservation": "前脚朝右上抬、后支撑向后伸，正常屈伸不是横叉。",
      "adjacentFrames": [
        4,
        6
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/06.png",
      "action": "run",
      "direction": "E",
      "frame": 6,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右杖腕前侧下移、左牌腕向后，肩肘连续。",
      "wholeLegAxisObservation": "前腿向右前摆，后腿向后蹬，鞋长轴均沿E方向。",
      "adjacentFrames": [
        5,
        7
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/07.png",
      "action": "run",
      "direction": "E",
      "frame": 7,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右前摆转折、左牌后位，握点不离柄/牌底。",
      "wholeLegAxisObservation": "前脚下落承接接地，后跟抬起，踝靴同向。",
      "adjacentFrames": [
        6,
        8
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/08.png",
      "action": "run",
      "direction": "E",
      "frame": 8,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右肘前屈、左牌肘后开，双臂依然相反摆动。",
      "wholeLegAxisObservation": "承重腿屈膝、靴尖向E，后脚回收底面符合侧视。",
      "adjacentFrames": [
        7,
        9
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/09.png",
      "action": "run",
      "direction": "E",
      "frame": 9,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右腕开始向身体回收，左牌后臂也进入转换段。",
      "wholeLegAxisObservation": "支撑鞋向右，后腿屈膝回摆；无单帧鞋头转向镜头。",
      "adjacentFrames": [
        8,
        10
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/10.png",
      "action": "run",
      "direction": "E",
      "frame": 10,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右杖臂收至肩身侧中位，左牌臂转前，09→10→11换相可读。",
      "wholeLegAxisObservation": "支撑腿屈膝承重，鞋尖E；后踝延续小腿折回，无膝外翻。",
      "adjacentFrames": [
        9,
        11
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/11.png",
      "action": "run",
      "direction": "E",
      "frame": 11,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右雷杖臂已后摆、左牌前摆，肩肘和握物均同侧连接。",
      "wholeLegAxisObservation": "支撑足朝E，后脚膝弯幅度自然，未见足轴偏离。",
      "adjacentFrames": [
        10,
        12
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/12.png",
      "action": "run",
      "direction": "E",
      "frame": 12,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右后摆手高位、左牌臂前屈，双腕在合理范围。",
      "wholeLegAxisObservation": "一腿抬膝向右、另一腿支撑朝右，膝—踝—鞋没有侧叉。",
      "adjacentFrames": [
        11,
        13
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/13.png",
      "action": "run",
      "direction": "E",
      "frame": 13,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右臂后摆展开、左牌前举，与后续14/15相位一致。",
      "wholeLegAxisObservation": "前摆鞋尖右上，支撑靴朝右，保留自然踝背屈。",
      "adjacentFrames": [
        12,
        14
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/14.png",
      "action": "run",
      "direction": "E",
      "frame": 14,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "本轮主窗口修正：右肩肘继续后摆，腕不再单帧前收，左牌保持原位。",
      "wholeLegAxisObservation": "原前摆与后撑腿姿态保持，膝胫踝鞋轴无新增偏转。",
      "adjacentFrames": [
        13,
        15
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    },
    {
      "file": "runtime/run/E/15.png",
      "action": "run",
      "direction": "E",
      "frame": 15,
      "frameDurationMs": 60,
      "actualVisualInspection": true,
      "anatomicalRightObject": "雷杖",
      "anatomicalLeftObject": "无柄矩形符牌",
      "upperLimbObservation": "右后摆开始回收接00，左牌前侧；一整圈有肩肘前后变化。",
      "wholeLegAxisObservation": "前脚准备落地、后脚蹬离，靴尖均随E方向，与00承接。",
      "adjacentFrames": [
        14,
        0
      ],
      "recommendation": "保留当前帧；本报告仅判断已实看的静态与相邻相位，整圈60ms播放由主窗口验收。",
      "unresolvedBlockingIssues": []
    }
  ],
  "unresolvedBlockingIssues": [],
  "limitations": [
    "本代理未播放整圈动态，不能代替主窗口60ms预览验收。",
    "本机客户端未接入。",
    "袖口/衣摆遮挡的肘、髋和膝按可见连接与轮廓推断，不宣称看见隐藏关节。",
    "未确认实际模型/质量；内置入口目标GPT Image 2.5 Sunburst/max，无选择器时实际提交及返回型号/质量记录为null。"
  ]
}''')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seen=[]
issues=[]
for f in report['frames']:
 p=ROOT/f['file'];r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p);s=sha(p)
 f['sha256']=s;seen.append(s);f['runtimeGenerationRecord']=f['file']+'.generation.json';f['derivedFrom']=r.get('derivedFrom',[])
 f['technicalChecks']={'shaMatchesGenerationRecord':s==r.get('sha256'),'rgba1024Transparent':im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0}
 for k,v in f['technicalChecks'].items():
  if not v: issues.append(f['file']+':'+k)
for h in report['historicalFindings']:
 h['resolvedBy']=[{'file':p,'sha256':sha(ROOT/p)} for p in h['resolvedFiles']]
report['recordedAt']=datetime.now(timezone.utc).isoformat();report['technicalSummary']={'frames':len(seen),'uniqueImageHashes':len(set(seen)),'issues':issues};assert len(seen)==64 and len(set(seen))==64 and not issues
out=ROOT/'review/upper_limb_run_N_NE_NW_E_20261005.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
own=[f for f in report['frames'] if f['direction']=='N' and f['frame'] in (0,1,14,15)]
(ROOT/'review/run_N_00_01_14_15_arms_20261005.json').write_text(json.dumps({'reviewDate':'2026-10-05','reviewer':'/root/finish_n_nw','frameDurationMs':60,'cycleDurationMs':960,'frames':own,'unresolvedBlockingIssues':[],'dynamicPlaybackReviewed':False,'clientIntegrated':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':out.name,'sha256':sha(out),'frames':len(seen),'technicalIssues':issues,'unresolvedBlockingIssues':report['unresolvedBlockingIssues']}))
