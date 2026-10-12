"""Record the completed primary-agent visual review; this script does not perform it."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
manifest=read(BASE/'manifest.json')
assert manifest['summary']['completeTechnicalPass']
now=datetime.now(timezone.utc).isoformat()
groups={
 'hit-E':'正面受击压身、闭眼护翼、反冲及恢复可辨，六帧独立，卷轴在画左、砚包在画右。',
 'hit-W':'保持背羽与后脑朝向，原地反冲收翼，无镜像正面代替背面；挂件侧别稳定。',
 'attack-E':'短促低头啄击后回收；第07帧已修正提前收翼及脚位偏移，第11帧已修正二次低头。',
 'attack-W':'背向压身啄击再回位，两翼与两鸟足保持物种结构，卷轴画右、砚包画左。',
 'cast-E':'由凝神到伸翼聚光、施放、收翼回位；修正稿已纳入最终全帧表及连播。',
 'cast-W':'真正斜后视角，微光释放后逐步收翼；第12帧重新AI编辑为中间收翼姿态，11至13帧过渡已复查。'
}
frames=[]
for item in manifest['frames']:
    assert sha(BASE/item['file'])==item['sha256']
    row={'file':item['file'],'sha256':item['sha256'],'sourceRecord':item['sourceRecord'],'status':'visually_reviewed_in_final_group_sequence'}
    frames.append(row)
    rp=BASE/item['sourceRecord'];r=read(rp)
    r['finalDeliveryReview']={'reviewedAt':now,'status':'accepted_for_art_delivery','sha256':item['sha256'],'record':'qa/visual-review-final.json','method':'individual generation result review, full final contact sheets and browser playback/step controls; not an engine test'}
    if item['id']=='cast_W_12':r['visualReview']['status']='native_and_final_export_reviewed_accepted'
    write(rp,r)
review={'schemaVersion':1,'reviewedAt':now,'reviewer':'primary Codex agent','status':'reviewed_and_accepted_for_art_delivery','automatedVisualReview':False,'framesReviewed':68,'groupsReviewed':list(groups),'methods':['Native generated results individually viewed during generation and editing','All 68 final exported frames viewed in six complete contact sheets','Browser six-group simultaneous and sequential playback inspected at normal speed and 0.25x','Pause, frame grid and next-frame controls exercised; cast W12 repair checked in final group and full-size browser display','Ivory, navy and checker backgrounds used to inspect transparent edges'], 'playback':{'normalSpeed':True,'quarterSpeed':True,'stepControls':True,'allSixGroups':True,'preview':'preview.html','lastChangedFrame':'runtime/cast/W/12.png'},'observations':groups,'checks':{'identityAndMaterials':'暮紫猫头鹰、象牙领、玉金饰物沿用原有身份和批准风格','anatomy':'两翼、两鸟足；未见人手、增生肢体或突然换侧挂件','directions':'E斜前右下；W斜后左上，背羽、后脑及后足为主要特征','framing':'全身、展开翼、尾羽和挂件均在透明画布内','motion':'原地受击、啄击、施法与回收；无位移循环，无镜像或插值补帧','transparency':'浅底、深底和棋盘可读，技术检查四边全透明'},'technicalSnapshot':{'maximumEdgeAlpha':max(x['edgeAlphaMax'] for x in manifest['frames']),'minimumVisibleMarginPixels':min(min(x['visibleBBox'][0],x['visibleBBox'][1],1024-x['visibleBBox'][2],1024-x['visibleBBox'][3]) for x in manifest['frames']),'duplicatePixelGroups':0},'limitations':['固定方向基准点由人工像素目测，约有±15工作像素误差；未逐帧硬锁足点。','独立AI绘制存在细小羽片与饰物形状变化；以本次逐帧与连播视觉检查验收。','浏览器预览检查不等于游戏引擎接入；未读取或修改客户端。','实际生成模型及质量未由宿主披露，仍为null。'],'frames':frames}
write(BASE/'qa/visual-review-final.json',review)
(BASE/'CHECKSUMS.sha256').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in frames),encoding='ascii')
print('Recorded completed primary visual review and checksums for',len(frames),'frames')
