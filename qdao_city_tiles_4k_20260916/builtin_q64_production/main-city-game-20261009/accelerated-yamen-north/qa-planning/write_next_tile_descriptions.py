from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
TEXT={
'r04_c05':[
'深棕门边与朱褐竖向框柱占主体，灰金色窄边沿着红色竖面延续上下；这是门柱局部，不含整扇门。',
'红柱位于左侧，大红灯笼的发亮圆腹跨向右邻格，下方露出金黄色连接结与悬垂饰件上端。',
'左侧延续红灯笼外缘，右侧转入朱褐窗框与金棕格栅区域，竖向木框延续至下边。',
'主体为金棕色几何格栅窗和深棕凹部，外围朱褐窗框跨向右侧与下方；总览不能可靠辨读其中文字。',
'左侧深棕门边与橙褐细框向下延伸，中间为灰石面及阴影，右边切入红柱下段。',
'左侧红柱在下缘接金黄圆形柱脚，右侧可见灯笼下垂金黄饰件局部，后方为灰褐石基。',
'灰褐石基横板占主体，上边接朱褐窗墙框，左下有金黄悬垂饰件边缘，右侧向白石狮头轮廓过渡。',
'上边是朱褐窗框下沿，下方进入白石狮的圆额和双眼上部；狮头向右和下方继续，不能画成完整狮身。',
'浅色石台上散有红纸或爆竹碎片，右上切入红金柱脚，底边是石台前缘及其灰色阴影。',
'左上为红金圆柱脚，浅石台面与零散红纸覆盖中部，下边进入竖向浅石栏杆顶端及左侧台阶。',
'浅石台面和红色碎纸位于上部，底部是灰色立面，右缘逐渐被白石狮侧面和阴影占据。',
'白石狮面部占主体，口鼻与暗色张口跨过中下部，下面连到颈胸；头部与身体均被格边裁切。',
'主体是向下延续的宽石阶，浅色踏面亮边与灰褐踢面形成连续横向带，左右不出现独立柱体。',
'中部浅色石栏杆纵向穿过画面，左边为横向台阶，右边为栏杆侧面的深灰阴影。',
'左部为台基附近灰暗石面，右边进入白石狮前腿轮廓，左下小片绿色的具体对象在总览中不可可靠辨认。',
'白石狮的胸腹和前腿局部进入画面，下方为腿间深色阴影与底部窄绿色区域，整只狮子超出当前裁片。'
],
'r03_c04':[
'青绿色瓦面占主体，左边裁入金色脊饰与窄竖边，瓦面和金饰均向相邻格继续。',
'整格主要是青绿色大屋面，细长近竖向瓦纹与明暗带贯穿上下，不含窗或门。',
'青瓦面铺满背景，右下角进入中央金色层叠脊饰，金饰向右上邻格和下格延续。',
'中央金色尖顶脊饰及层叠弯曲金边占主体，青瓦作背景，金色主体上下均被边界裁切。',
'上部是青绿色瓦面，下部出现横向深棕檐口、金棕支架与深色檐下阴影。',
'青瓦面延续至中下部，底边为深棕檐口和金棕托架，与左右格形成连续横向檐线。',
'金色斜脊边从左下向右上穿过，斜边下是青瓦与深色夹层，右上接中央金色脊饰。',
'中央山花顶部的金色结点和斜出两侧的金边檐线占主体，下方接赭金骨架与深色夹层。',
'深青屋面及其阴影占主体，下边和左下角开始进入前层上翘金色檐边。',
'金色上翘卷头由左中进入，粗金边向右上延伸，其下为青瓦窄带、深色檐下带和金棕构件。',
'斜向金边屋檐从左下向右上通过，深色檐下三角区域与赭金支架夹在相邻金边之间。',
'正面山花中部为圆形金棕装饰面，外有粗金色拱边和周围深色三角间隙；不要据模糊总览补写字。',
'宽金色上翘檐边在上部转弯，下方是青瓦、红棕檐下结构，底缘开始露出红灯笼的上部。',
'青瓦窄屋面占上部，下方为深棕横梁与红棕竖构件，局部金饰和红灯笼边缘被底边裁切。',
'上部连续青瓦檐面，下方接金棕支架和较暗的木构间隙，构件向左右延续。',
'上部青瓦与中央脊饰下垂部分相接，下方为金棕三角木构和深色檐下区，边界之外才继续进入立面。'
],
'r03_c05':[
'整格为青绿色大屋面，近竖向明暗条带贯穿上下，四边主要延续同一屋面。',
'青绿色屋面占主体，右侧出现较深的近竖向阴影带，右下边缘露出与相邻格相连的金色屋脊构件。',
'金色屋脊构件从左上侧进入，在左侧转接后斜向右下延伸，右上及下方均有青绿色屋面。',
'主体是青绿色屋面，顶边靠右有深色阴影，下边偏中位置露出下一格金色上翘端头的顶部。',
'上半部是青绿色屋面，下半部出现横向深棕檐口及木构，另有金色斜向脊边从左侧下行至底边。',
'青绿色屋面从顶边延续至中下部，下面为横向深棕檐口和金棕色支撑，其底部接深色檐下阴影。',
'上部金色脊边由左上向右侧倾斜穿过，中央为青绿色屋面，底部横向檐口及木构延续左右邻格。',
'上部是向上卷起的宽金色屋脊端头，中部下方接深色阴影与金棕支撑，右侧为青绿色屋面，另一条浅金脊边斜向右下出格。',
'多层屋檐斜穿画面，上方浅金脊边由左上走向右侧中部，其下依次为青绿色窄屋面、深色檐下带及另一道浅金边。',
'左上至中央有相邻格斜脊末端的金色上翘卷头，右侧主要为青绿色屋面，另一道金色弧形脊边从左下延伸至底边。',
'主体为青绿色屋面，上部覆盖大片深青阴影，底边偏左出现下一格金色上翘端头的顶部。',
'浅金脊边沿上方从左向右下斜穿，其下贴着深色阴影带，其余大部分为连续青绿色屋面。',
'上部为青绿色屋面及横向檐口，下部为红棕色建筑立面，偏左有亮金色竖向构件进入画面。',
'上部金色弧形脊边从左侧延伸到右侧，下面是深青阴影与青绿色屋面窄带，下半部为红棕色檐下建筑结构。',
'左上为金色脊边的上翘卷头及向下弯曲的端部，右上为青绿色屋面，屋面下缘接横向棕色檐口和下部木构立面。',
'上部为青绿色屋面，近水平下缘横贯左右，下面为深棕檐下带、竖向支撑及较大面积红棕色立面。'
]}
summary=[]
for tid,descs in TEXT.items():
 D=HERE/tid;idx=json.loads((D/'layout-index.json').read_text(encoding='utf-8'));assert len(descs)==16
 for item,desc in zip(idx['patches'],descs):item['description']=desc;item['descriptionBasis']='Viewed actual contracted overview and labeled 4x4 crop; visible layout only, no invented fine detail'
 record={'tile':tid,'tileWorldBox':idx['tileWorldBox'],'source':idx['source'],'sourceSha256':idx['sourceSha256'],'sourcePixels':idx['sourcePixels'],'layoutOnly':True,'gameArt':False,'coordinateSystem':'world pixel, half-open boxes','nativePatchPlan':[1254,1254],'core':1024,'haloEachSide':115,'sourceMapResolutionLimitation':'Each core spans about 19.6 overview pixels; these enlarged crops locate objects, not surface detail or exact lettering. Never use as generated tile art.','patches':idx['patches']}
 p=D/'content-index.json';p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');summary.append({'tile':tid,'worldBox':idx['tileWorldBox'],'contentIndex':str(p),'grid':str(D/(tid+'-grid-layout-only.png')),'haloContact':str(D/(tid+'-halo-contact-layout-only.png')),'patchCount':16})
(HERE/'next-three-tiles-index.json').write_text(json.dumps({'layoutOnly':True,'generatedGameArt':False,'tiles':summary},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
