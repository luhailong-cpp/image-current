import json, hashlib, datetime
from pathlib import Path
from PIL import Image, ImageChops
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before={(x['direction'],x['frame']):x['sha256'] for x in load(R/'reviews/video-axis-N-W-before-20261004.json')}
replaced={1,2,3,6,7,8,15}
nreasons={
1:'右脚承重鞋跟朝镜头、鞋尖向北；左脚后屈露底属正常回收，膝踝同轴。',
2:'右脚承重与01同位置段；左脚后抬露底，未见脚尖横向外张。',
3:'右脚承重向第二位置段过渡，左膝后屈与鞋长轴一致。',
4:'右脚承重第二位置段；左脚后屈的鞋底透视合理，无突然外扭。',
5:'右脚承重第三位置段，鞋跟朝后；左脚回收仍沿北向运动面。',
6:'与05同承重位置段；左脚踝、鞋长轴连续，无外翻。',
7:'右脚承重第四位置段，左脚回收；左右腿分离清楚且轴线合理。',
8:'与07同承重位置段；北向鞋跟和抬脚鞋底透视延续。',
9:'左脚换为承重，右脚后抬露底，膝踝沿北向，正常屈膝保留。',
10:'与09同承重位置段，右脚底面来自后屈，无横向扭转。',
11:'左脚承重第二位置段，右脚回收与膝同轴。',
12:'与11连续；右脚底略倾为正常回收透视，未见突变外张。',
13:'左脚承重第三位置段；右脚鞋跟转为更直立，是回收踝屈伸而非外扭。',
14:'与13同位置段；右脚跟朝镜头且鞋尖向北，保留正常前后屈伸。',
15:'左脚承重第四位置段；右脚底面露出随回收变化，鞋长轴仍向北。',
16:'与15同位置段；右脚踝和鞋轴连续，循环换脚前无外翻。'
}
wkeep={
4:'抬起左鞋仅窄幅底边可见，膝踝与西向一致；作为本轮中立鞋轴参照保留。',
5:'左脚自然前摆、膝盖屈曲，鞋面/侧面透视合理；右脚承重未外撇。',
9:'左脚承重、右脚后屈，鞋尖与西向同一运动平面，未见外翻。',
10:'右脚后屈加深，鞋跟抬高属正常踝屈伸；与09衔接可读。',
11:'右脚回收前移，鞋尖向西且主要见鞋面/侧面，无多余底面朝镜头。',
12:'与11同位置段；右脚膝踝鞋轴一致，未见横向外扭。',
13:'右脚向前摆，鞋轴持续向西，左支撑脚前后推进正常。',
14:'与13同位置段；抬脚侧面与承重脚方向连续，保留正常透视。',
16:'右脚前摆结束，鞋底基本朝下、鞋尖向西，与新15连续。'
}
frames=[]
for d in ['N','W']:
 for f in range(1,17):
  rel=f'frames/run/{d}/{f:02}.png'; p=R/rel; hs=sha(p)
  side=load(p.with_suffix('.png.generation.json'))
  assert side['sha256']==hs,(d,f,'sidecar hash')
  im=Image.open(p)
  assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255),(d,f,'image format')
  changed=d=='W' and f in replaced
  assert (hs!=before[d,f])==changed,(d,f,'decision mismatch')
  if changed:
   reason=('修正抬起'+('右' if f==15 else '左')+'鞋向镜头过度翻底的角度，保留鞋中心、膝弯、步幅和承重脚；鞋尖沿西向、主要呈鞋侧面，底面缩至正常透视。')
   if f==8:reason+='第一稿踝边误生白色伪影，a02已用内置image_gen清除后复核。'
   rec=load(R/side['generationRecord']); nat=R/rec['native']['file']
   assert sha(nat)==rec['native']['sha256']
   assert rec['actualModel'] is None and rec['actualQuality'] is None
   ni=Image.open(nat).resize((1024,1024),Image.Resampling.LANCZOS)
   assert ImageChops.difference(ni,im).getbbox() is None
  else:reason=nreasons[f] if d=='N' else wkeep[f]
  frames.append(dict(path=rel,sha256=hs,direction=d,frame=f,decision='replaced' if changed else 'retained',reason=reason,previousSha256=before[d,f],generationRecord=side['generationRecord'],supportFoot='RIGHT' if f<=8 else 'LEFT',supportPositionSegment=((f-1)%8)//2+1,frameDurationMs=75,visualReview='pass_static_frame_and_adjacent_sequence'))
report={
 'reviewId':'video-axis-N-W-20261004','reviewedAt':now,'reviewer':'finish_north',
 'scope':'本轮视频腿脚外翻反馈后的新复核；非沿用旧完成报告。',
 'summary':{'frameCount':32,'replaced':7,'retained':25,'N':'16帧保留','W':'01/02/03/06/07/08/15修正抬脚踝鞋过度翻底，其余9帧保留'},
 'frames':frames,'knownUnresolvedArtFailures':[],
 'evidence':{'viewed':['../..//reference-motion-review-20261004/video-contact.jpg','../..//reference-motion-review-20261004/character-detail.jpg','C:/Users/luyua/AppData/Local/Temp/codex-clipboard-7cc4bf22-e4cf-4c35-8ac6-a37fd85f4037.png','work/video-axis/reference-continuous-0.jpg','work/video-axis/reference-continuous-1.jpg','work/video-axis/reference-continuous-2.jpg','work/video-axis/reference-continuous-3.jpg','reviews/video-axis-N-legs-20261004.jpg','reviews/video-axis-W-legs-20261004.jpg','reviews/video-axis-W-legs-after-20261004.jpg','work/run-W/contact-current.png'],
 'limits':'视频低分辨率且有UI遮挡，仅用于观察连续步态、动作平面和正常屈膝；用户截图为另一角色，仅作诊断。鞋轴判断以本角色正式1024图逐帧和相邻帧为准。未把后视抬脚露底或正常膝弯一概认定为错误。',
 'motionReferenceSampling':'reviews/video-reference-sampling-20261004.json',
 'QACompositeOperation':'统一固定区域裁切后等比缩放，仅审图用途；正式图未裁切或逐帧位移。'},
 'gait':{'support':'RIGHT01-08; LEFT09-16','positionSegments':'每只支撑脚4位置段，各2独立姿态','framesPerDirection':16,'frameDurationMs':75,'cycleDurationMs':1200},
 'verification':{'currentFormalSHAAndSidecar':32,'format1024RGBAAlpha':32,'newNativeToFormalExactUniformResize':7,'staticReview':'32帧全量腿部放大及新7帧全图、W全序列实看通过','dynamicPlayback':'由root统一最终浏览器核验；本报告未冒充客户端或动态播放验收'},
 'modelEvidence':{'configurationTargetModel':'gpt-image-2.5-sunburst','configurationTargetQuality':'max','route':'builtin image_gen','submittedModel':None,'submittedQuality':None,'returnedModel':None,'returnedQuality':None,'confirmation':'未确认；宿主管理入口未披露型号/质量，详见每张request/receipt/record。'},
 'rejectedCandidate':{'key':'video-axis-north-20261004-W08-a01','reason':'踝边有小白色伪影，未正式导入，a02替代。'}
}
report['evidence']['viewed'][0]='../../reference-motion-review-20261004/video-contact.jpg'
report['evidence']['viewed'][1]='../../reference-motion-review-20261004/character-detail.jpg'
out=R/'reviews/video-axis-N-W-20261004.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
ip=R/'inventory-run-north.json'; iv=load(ip)
rows={(x['direction'],x['frame']):x for x in frames}
for x in iv['frames']:
 k=(x.get('direction'),x.get('frame'))
 if k in rows:
  q=rows[k];assert x['sha256']==q['sha256']
  x['visual_status']='video_axis_static_review_pass_pending_root_dynamic_review'
  x['video_axis_review']={'report':'reviews/video-axis-N-W-20261004.json','decision':q['decision'],'reviewedAt':now,'reason':q['reason']}
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2),encoding='utf-8')
se=[]
for f in range(9,17):
 p=R/f'frames/run/SE/{f:02}.png'
 se.append({'path':p.relative_to(R).as_posix(),'sha256':sha(p),'direction':'SE','frame':f,'finding':'未见膝踝鞋轴外撇硬问题；11–14修正后鞋尖沿SE方向，09–16相邻动作连续。'})
seReport={'reviewedAt':now,'reviewer':'finish_north','reviewType':'independent read-only static review','viewed':['previews/run-SE-video-axis-detail.png','frames/run/SE/11.png','frames/run/SE/13.png'],'frames':se,'knownUnresolvedArtFailures':[],'limits':'未修改SE；动态播放由root统一验证。'}
(R/'reviews/video-axis-SE-independent-north-20261004.json').write_text(json.dumps(seReport,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(out),'frames':len(frames),'replaced':7,'retained':25,'sidecarChecks':32,'newNativeChecks':7,'SEindependent':8},ensure_ascii=False))

