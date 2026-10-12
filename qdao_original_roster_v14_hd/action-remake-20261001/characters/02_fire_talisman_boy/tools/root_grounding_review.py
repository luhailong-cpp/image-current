"""Current E/SE grounding notes. Only writes its review, never moves images."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
FRAME_MS=75
durations=[FRAME_MS]*16
# These exact images were visually read on2026-10-04. A later replacement does
# not inherit that static observation merely because this tool is rerun.
observed={
 'E':{1:'f1938933ec90fdfde84817c4ba0b8a7340da2d3340fa358412d194fb36ad6cc2',7:'cf613ae5a2fbc5247234d7a366e144356099cd662e9c01582eee07043553bd52',8:'6923561c69f130cf61f9653c2409cedd9c575514156a8a52048902f74cd23512',9:'e0fbacec091e4d152539c93e690858b758b01b0f03889e54f123ec194f454f1d',15:'467e62f467726c82bd063d8b63c61a4a9174339ba0b39fbd628e8315afef6c2e',16:'8400c9ed706ddbb5150d45240b74faecb6a1ff229c36822be5c709d17f593b55'},
 'SE':{1:'8c8c67c03c43f886bae533f47dacb680f7d2f3556d4d0c1e7fa8e94fa1d30b60',7:'aca85a82a207fa53355c4c7d0842b93005ec65c47872b66365b322d99fc1695e',8:'fdb6cb89794a3be4037f008af83c30c60e3cadc8b39a172eb1032f60c7d35858',9:'471c8a3822162318bee177d4271a20563878e49e96704a0c1f4afa51c53f5ca5',15:'68d59c758bc9c353489cc301e6cc22f7f6067046f700078ec6e97d9835a4d9db',16:'1b41a2905f5ee890054ea446417d70fbaee85ee69dcd797cb80c83e79fba3ab7'}
}
notes={
 'E':{1:'右腿在前、左腿后折；接续16的支撑候选，鞋底俯仰和首尾承重连续性仍待整圈复核。',7:'左腿向前下放，左鞋低位且底边较平，右腿在后折起；落脚候选，不再标为腾空下降。',8:'左支撑膝较07屈曲、鞋底近平，右腿回收；压缩承重候选，07→08共同地面高度仍待实播。',9:'左腿在前、右腿后折，接续08；保留支撑候选，避免把09重复写成已确认的新落脚事件。',15:'右腿前伸、右鞋跟低且鞋尖稍抬，左腿后折；右脚落脚候选。',16:'右膝屈曲、右鞋底趋平，左腿折起；右脚压缩承重候选，16→01待复核。'},
 'SE':{1:'右腿在viewer左低位，左腿后折；接续16支撑候选，透视下的脚掌接地未作客户端确认。',7:'左腿在viewer右前下伸，左鞋露部分底面；为落脚候选，露底不等于外撇或已确认悬空。',8:'左膝更屈曲、左鞋由前伸转承重候选，右腿后收；鞋底仍有SE俯仰投影，需同地面实播。',9:'左腿前低、右腿后收，接续08支撑候选；鞋底角度与重心连续性待整圈复核。',15:'右腿在viewer左前下伸、右鞋跟低，左鞋高收；右脚落脚候选。',16:'右支撑膝屈曲、右鞋趋平，左腿后收；右脚压缩承重候选，透视与首尾连接仍待实播。'}
}
phases=['右脚支撑延续候选','右脚屈膝承重候选','右脚中支撑，左膝前摆候选','右前掌蹬离候选','左腿前摆，短暂腾空候选','左腿前伸腾空候选','左脚落脚候选','左脚压缩承重候选','左脚支撑延续候选','左脚屈膝承重候选','左脚中支撑，右膝前摆候选','左前掌蹬离候选','右腿前摆，短暂腾空候选','右腿前伸腾空候选','右脚落脚候选','右脚压缩承重候选']
result={'character':'02_fire_talisman_boy','reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'uniform_timing_adopted_full_cycle_grounding_review_pending','cycles_ms':[1200],'adopted_cycle_ms':1200,'frame_ms':FRAME_MS,'uniform':True,'phase_weights_applied':False,'timingAuthority':'最新人类明确正常跑步1200ms＝16×75ms均匀；慢放、暂停与逐帧仍保留。','client_validation':'未接入，未完成位移速度及滑步验收','root':{'reference':[512,920],'calibrated':False,'definition':'固定虚拟地面诊断标记，不读取最低alpha点做逐帧贴地。支撑鞋实际地面投影和比例仍需统一复核。'},'display':{'canvas_css_px':160,'client_size_confirmed':False,'large_css_px':384},'directions':{}}
for d in ['E','SE']:
    frames=[]
    for n in range(1,17):
        p=R/'frames'/'run'/d/f'{n:02}.png'
        current=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        reviewed=observed[d].get(n)
        frames.append({'frame':n,'path':p.relative_to(R).as_posix(),'sha256':current,'exists':p.is_file(),'actualPhase':phases[n-1],'phaseConfidence':'static_candidate_full_cycle_pending','durationMs':FRAME_MS,'trialDurationMs':FRAME_MS,'visualStatus':'candidate_not_final_pass','observation':notes[d].get(n,'延续既有相位候选，未由本轮局部实图检查扩大为整段通过。'),'observedSha256':reviewed,'observationMatchesCurrentPixels':current==reviewed if reviewed else None,'needsNewStaticReview':reviewed is not None and current!=reviewed})
    result['directions'][d]={'complete':all(f['exists'] for f in frames),'timing':{'cycleMs':1200,'frameMs':FRAME_MS,'durationsMs':durations,'uniform':True,'phaseWeightsApplied':False,'status':'user_requested_uniform_1200ms_client_unconfirmed'},'frames':frames,'remaining':['整体比例与虚拟地面校准','正常1200ms与慢放下检查16→01、08→09及总循环','05→06→07落脚→08压缩、13→14→15落脚→16压缩的连续性','局部道具及手腕返修后按当前SHA复核，单帧观察不自动升为整段通过']}
for d in ['W','N','NW','NE','S','SW']:
    paths=list((R/'work'/('run-'+d)).glob('*grounding*.json'))
    if paths:
        p=sorted(paths,key=lambda x:x.stat().st_mtime)[-1]
        result['directions'][d]={'reviewReference':p.relative_to(R).as_posix(),'status':'由逐图审阅表读取；默认1200ms均匀，动态尚待总循环复核'}
(R/'reviews'/'run-grounding-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({'phaseRows':32,'originalResolutionFramesViewedThisUpdate':12,'cycleMs':sum(durations),'frameMs':FRAME_MS,'uniform':True})
