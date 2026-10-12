"""Record root's completed visual review; never alter image pixels.

Run only after actual static, normal-speed, slow and stepped playback review.
This records the explicit review decision; technical checks cannot make it.
"""
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

B=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--confirm-completed-visual-review',action='store_true')
    args=p.parse_args()
    if not args.confirm_completed_visual_review: p.error('Explicit completed visual review required')
    m=read(B/'manifest.json'); selection=B/m['selectionSource']['file']
    assert digest(selection)==m['selectionSource']['sha256']
    frames=[f for s in m['sequences'] for f in s['frames']]
    assert len(frames)==196 and len(m['sequences'])==14
    for f in frames: assert digest(B/f['file'])==f['sha256']
    reviewed=datetime.now(timezone.utc).isoformat()
    notes={
        'run':'对照09当前成品动作逻辑，逐帧检查连续支撑、四个位置段各两帧、膝踝鞋轴和近远手持物；正常与慢放检查循环及08→09/16→01换脚。',
        'hit':'检查两脚、握笔持卷轴、受击收回和首尾恢复；正式输出正常与慢放检查。',
        'attack':'检查抬笔、06接触和收势、膝踝及双手持物；正式输出正常与慢放检查。',
        'cast':'检查抬笔、10释放、笔尾流苏、双手持物及13→14收势；正式输出正常与慢放检查。',
    }
    seqs=[{'action':s['action'],'direction':s['direction'],'visualApproval':'passed',
           'dynamicApproval':'passed','reviewNote':notes[s['action']],
           'frames':[{'slot':f['slot'],'sha256':f['sha256']} for f in s['frames']]}
          for s in m['sequences']]
    approval={'schemaVersion':1,'character':B.name,'status':'passed',
              'visualApproval':'passed','dynamicApproval':'passed','reviewedAt':reviewed,
              'reviewer':'root assistant visual review; not user acceptance',
              'previewManifestSha256':digest(selection),
              'runtimeFrameSha256':{f['slot']:f['sha256'] for f in frames},
              'reviewMethods':['full-sequence contact sheets','browser normal playback',
                               'browser quarter-speed playback','stepped critical transitions'],
              'reviewedDisplay':'whole canvas, 240px and larger inspection',
              'reference':'09_bamboo_archer_girl current runtime and manifest; mechanics reference',
              'sequences':seqs,'clientRuntimeAcceptance':'not_tested','clientIntegrated':False,
              'limits':['素材制作与本地预览验收；不等同用户最终审美确认。',
                        '未接入客户端，游戏内统一枢轴和实际位移仍需集成核验。',
                        '内置生成工具未披露实际型号/质量，记录保持null。']}
    revision=m.get('fullBodyRevision') or m.get('axisRevision')
    full_body=bool(m.get('fullBodyRevision'))
    history='provenance/full-body-revision-20261005' if full_body else 'provenance/axis-revision-20261004'
    playback_file='review/full-body-playback-review-20261005.json' if full_body else 'review/axis-playback-review.json'
    if revision:
        changed=set(revision['changedSlots'])
        affected={x.rsplit('-',1)[0] for x in changed}
        if m.get('timingRevision'):
            affected.update('run-'+d for d in m['timingRevision']['directions'])
        playback=read(B/playback_file)
        assert playback['status']=='passed' and set(playback['changedSlots'])==changed
        assert playback['runtimeFrameSha256']=={f['slot']:f['sha256'] for f in frames}
        assert set(playback['reviewedSequences'])==affected
        if m.get('timingRevision'):
            assert playback['runTiming']=={'frameMs':60,'cycleMs':960,'frameCount':16}
        approval['fullBodyRevisionReview' if full_body else 'axisRevisionReview']={'changedSlots':sorted(changed),'changedSequences':sorted(affected),
            'referenceObservation':'review/axis-video/observations.json',
            'actualPlaybackEvidence':{'file':playback_file,'sha256':digest(B/playback_file)},
            'selectionEvidence':m['selectionSource'],
            'unchangedFramesVerifiedAgainst':history+'/manifest-before.json',
            'method':'All newly timed run sequences and changed combat sequences reviewed again at normal/quarter speed and stepped through affected neighboring frames; other sequences inherit prior review with identical image hashes.',
            'timingRevision':m.get('timingRevision')}
        for s in approval['sequences']:
            if f"{s['action']}-{s['direction']}" not in affected:
                s['reviewNote']='本轮像素未改，逐帧SHA与上一轮一致；本轮手脚静态复核记录另存，继承此前实际播放审查。'
                s['carriedForwardFrom']=history+'/acceptance-before.json'
    write(B/'acceptance.json',approval)
    write(B/'review/final-sequence-review.json',approval)
    m['status']='passed'
    m['counts']['visualPassedSlots']=196;m['counts']['dynamicPassedSequences']=14
    m['acceptance']={'file':'acceptance.json','sha256':digest(B/'acceptance.json'),'record':approval}
    for f in frames: f['status']='passed'
    write(B/'manifest.json',m)
    req=read(B/'review/contact-pairs-current-20261004.json')
    req['status']='implemented_and_sequence_review_passed'
    req['acceptance']='../acceptance.json'
    req['supportByDirection']={d:{'firstHalf':('LEFT' if d in ('NW','SW') else 'RIGHT'),
                                    'secondHalf':('RIGHT' if d in ('NW','SW') else 'LEFT')}
                               for d in ('N','NE','E','SE','S','SW','W','NW')}
    write(B/'review/contact-pairs-current-20261004.json',req)
    (B/'STATUS.md').write_text('''# 17 灵篆书生 · 已完成素材制作

196张1024×1024透明PNG已导出，14组动作通过本地逐帧与播放检查。跑步八方向的脚步、膝踝鞋轴和摆臂过渡已按09竹弓少女当前动作规律修正。每个位置段两张独立姿态，16帧各60ms，一轮960ms。

以 [正式清单](manifest.json)、[验收记录](acceptance.json) 和 [交付说明](DELIVERY.md) 为当前状态。[完整动作预览](preview/delivery.html) 支持正常、慢放和逐帧。

受击6×40ms、普攻12×30ms（06接触）、施法16×45ms（10释放），均含E/W。所有PNG整画布统一缩为1024，没有逐帧裁切、平移、复制帧或插值补帧。

本地素材验收不等同游戏内验收；本次未接入客户端，也未提交或推送Git。统一枢轴与实际位移由客户端集成时验证。实际生成型号和质量未由内置工具披露，来源记录保持null。

旧review、inventory及manifest-preview为制作历史，包含当时待审/拒稿状态与已清理的源图片路径，不代表当前状态。不要再次运行旧audit_inventory.py或build_preview.py覆盖正式结果。清理详情见cleanup-report.json。
''',encoding='utf-8')
    (B/'MERGE_HANDOFF.md').write_text('''# 17 灵篆书生 · 素材交接

本角色制作完成。只交付本目录的runtime、manifest.json、acceptance.json及DELIVERY.md；正式离线预览位于preview/delivery.html。共196帧、14组动作，每帧1024×1024 RGBA。完整时长、事件、逐图来源和哈希见manifest.json。

八方向跑步16×60ms；01–08同一脚连续支撑，09–16换另一脚，各半轮四个位置段、每段两帧。N/NE/E/SE/S/W先右后左，NW/SW先左后右，按角色解剖侧。

来源PNG只作一次整画布LANCZOS缩放；导出偏移为0。客户端统一枢轴未标定，不能按逐帧最低脚点自动吸附地面。旧预览参考(0.5104,0.92105)仅为检查参考。

本次没有客户端接入、Git暂存、提交或推送。其他角色和旧正式素材保持原状。按用户素材保留规则清除本批原图、拒稿及加工图，逐图模型/质量/时间/来源文字记录保留。runtime旁的generation.json内嵌完整来源记录。

当前结论以acceptance.json和review/final-package-verification.json为准；早期制作检查文件保留历史用途，勿将其pending状态覆盖最终验收。工具未披露的实际型号/质量仍为null。
''',encoding='utf-8')
    (B/'preview/README.md').write_text('''# 灵篆书生完整动作预览

直接用浏览器打开 [delivery.html](delivery.html)，无需服务器。保持preview与runtime目录相对关系；全部196帧从runtime读取。支持八方向跑步和E/W受击、普攻、施法，正常播放、四分之一慢放、暂停和逐帧检查。

[八方向跑步动图](run-current-960ms.webp)为16帧各60ms，共960ms，240px整画布显示。

旧入口重定向到正式预览。manifest-preview.json只保留导出时的选图/来源历史快照；其中staging路径可能已按素材保留规则清理，正式预览不读取这些路径。不要再用旧build_preview.py覆盖入口。
''',encoding='utf-8')
    if revision:
        revision_note='\n本次全动作手脚复核与局修：'+ '、'.join(revision['changedSlots'])+'。检查髋膝踝鞋尖轴向、肩肘腕、握持与回收衔接；其余'+str(196-len(revision['changedSlots']))+'张正式帧SHA保持不变。修改方向已重新正常播放、四分之一慢放及关键帧逐张检查。\n'
        for name in ('STATUS.md','MERGE_HANDOFF.md'):
            target=B/name
            target.write_text(target.read_text(encoding='utf-8')+revision_note,encoding='utf-8')
    print(json.dumps({'status':'passed','frames':196,'sequences':14,'reviewedAt':reviewed}))

if __name__=='__main__': main()
