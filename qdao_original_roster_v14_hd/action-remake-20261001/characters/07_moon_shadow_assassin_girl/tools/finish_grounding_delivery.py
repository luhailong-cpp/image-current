"""Finalize reviewed 20261004 revisions; preserve textual evidence when cleaning sources."""
import argparse
from pathlib import Path
from revise_feet_20261003 import ROOT, read, save, sha, now, scoped
from build_preview import main as build_html

REVISIONS = ['direction-alignment-20261004', 'direction-combat-20261004', 'run-grounding-20261004']
REV = ROOT / 'review' / REVISIONS[-1]

def phases():
    m = read(ROOT / 'manifest.json')
    assert len(read(REV / 'replacement-ledger.json')['replacements']) == len(read(REV / 'selection.json')['selected'])
    plans = {p['direction']: p for p in read(REV / 'plan.json')['directions']}
    labels = ['contact', 'absorb', 'support', 'support', 'drive', 'drive', 'toe_off', 'toe_off']
    positions = ['front_landing', 'under_body', 'rear_drive', 'final_forefoot']
    evidence = {}
    for f in m['frames']:
        if f['action'] != 'run': continue
        i = f['index']; half = 'A' if i < 8 else 'B'; phase = labels[i % 8] + '_' + half
        f['phase'] = phase
        f['events'] = ['contact_' + half] if i in (0,8) else ['toe_off_' + half] if i in (7,15) else []
        f['support'] = {'halfCycle': half, 'foot': plans[f['direction']]['support' + half],
                        'position': positions[(i % 8) // 2], 'pairNumber': i // 2 + 1,
                        'scope': 'drawn support phase only; no collision or automatic foot locking'}
        evidence.setdefault(f['direction'], []).append({'frame': i+1, 'phase': phase,
            'support': f['support'], 'sha256': f['sha256']})
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/run-phase-review.json', {'updatedAt': now(), 'frameNumbering': '1-based filenames; index in manifest is 0-based',
        'basis': 'Actual native edits and full per-direction sequence review; support persists through four pairs, with perspective retained.',
        'pattern': '01-02 front landing;03-04 under body;05-06 rear drive;07-08 final forefoot.09-16 opposite foot repeats.',
        'sourceReview': 'review/run-grounding-20261004/plan.json', 'directions': evidence,
        'clientTested': False, 'scope': 'offline visual phase labels; not physics or collision events'})
    assert build_html() == 0
    print('Updated actual-frame support labels and landing/toe-off markers.')

def prompt_indexes():
    for name in REVISIONS:
        rev = ROOT / 'review' / name; stage = ROOT / 'staging' / name
        chosen = {scoped(p) for p in read(rev / 'selection.json')['selected'].values()}
        records = []
        for p in sorted(stage.rglob('*.png.generation.json')):
            native = Path(str(p).removesuffix('.generation.json'))
            stem = str(native).removesuffix('.png')
            request, receipt = Path(stem+'.request.json'), Path(stem+'.receipt.json')
            assert request.is_file() and receipt.is_file(), str(p)
            nr = read(p)
            records.append({'candidate': native.relative_to(stage).as_posix(),
                'request': request.relative_to(ROOT).as_posix(), 'receipt': receipt.relative_to(ROOT).as_posix(),
                'nativeRecord': p.relative_to(ROOT).as_posix(), 'nativeSHA256': nr['sha256'],
                'selectedAtRevision': native in chosen})
        save(rev / 'prompt-index.json', {'route':'builtin image_gen.imagegen', 'actualModel':None, 'actualQuality':None,
             'configuredBatch':'20261001 continuing batch; see per-image snapshots; actual version/quality not exposed', 'candidates':records})

def accept():
    m = read(ROOT / 'manifest.json'); review = read(REV / 'final-review.json')
    assert review['passed'] is True and review['scope'] == 'offline'
    assert review['frameSHA256'] == {f['id']: f['sha256'] for f in m['frames']}
    assert read(REV / 'timing-verification.json')['passed']
    assert read(REV / 'browser-check.json')['passed']
    assert read(ROOT / 'review/direction-combat-20261004/browser-check.json')['passed']
    for f in m['frames']:
        f['visualApproved'] = True
        f['visualReviewScope'] = 'Current direction and support sequence review; native edits, final contact sheets and browser state checks; offline only. See run-grounding final-review.json.'
        rec = read(ROOT / f['sourceRecord']); rec['visualApproved'] = True; save(ROOT / f['sourceRecord'], rec)
    revisions = {n: sorted(read(ROOT/'review'/n/'selection.json')['selected']) for n in REVISIONS}
    m.update({'formalAccepted':True, 'updatedAt':now(),
        'currentReview':{'status':'offline_complete','record':'review/run-grounding-20261004/final-review.json',
            'revisions':revisions,'referenceCharacter':'09_bamboo_archer_girl','client':'not_tested'},
        'note':f"196 independent frames; direction-axis and combat corrections plus{len(revisions[REVISIONS[-1]])} run-support edits; normal run1200ms/16x75ms; offline acceptance only."})
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/final-visual-review.json', {'reviewedAt':now(),'offlineAccepted':True,'scope':review['method'],
        'acceptedSHA256':review['frameSHA256'],'revisionReview':'review/run-grounding-20261004/final-review.json','clientTested':False})
    save(ROOT / 'preview/progress.json', {'frames':196,'offlineAccepted':196,'clientIntegrated':0})
    prompt_indexes()
    assert build_html() == 0
    print('Current196-frame offline review accepted. Client remains untested.')

def cleanup():
    from verify_manifest import verify
    m = read(ROOT / 'manifest.json'); assert m['formalAccepted']
    pre = verify(m, True); assert pre['passed'], pre['errors']
    archive = REV / 'before-cleanup-structure-report.json'
    assert not archive.exists(), 'Cleanup already started; inspect before retry.'
    removed = []
    candidates = []
    for name in REVISIONS:
        stage = scoped('staging/'+name)
        candidates.extend(stage.rglob('*.png'))
        candidates.extend(scoped('review/'+name).glob('candidate-*-contact.jpg'))
        candidates.extend(scoped('review/'+name).glob('*-candidate-contact.png'))
    for p in sorted(set(candidates)):
        p = scoped(p)
        assert p.is_file() and (p.is_relative_to(ROOT/'staging') or (p.parent.parent==ROOT/'review' and (p.name.startswith('candidate-') or p.name.endswith('-candidate-contact.png'))))
        removed.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,
                        'reason':'verified final export retained; temporary native/rejected edit or QA contact sheet','at':now()})
    save(archive, read(ROOT/'review/pre-cleanup-structure-report.json'))
    save(ROOT/'review/pre-cleanup-structure-report.json', pre)
    ledger = read(ROOT/'review/cleanup-ledger.json')
    prior = {x['path'] for x in ledger['removed']}
    assert not prior.intersection(x['path'] for x in removed)
    ledger['removed'].extend(removed); ledger['lastRevisionCleanupAt']=now()
    ledger['verificationReports']=list(dict.fromkeys(ledger.get('verificationReports',[])+[archive.relative_to(ROOT).as_posix(),'review/pre-cleanup-structure-report.json']))
    save(ROOT/'review/cleanup-ledger.json',ledger)
    # A filename can have several historical contents. Match both path and SHA.
    historical = {}
    key = lambda p,d: (str(Path(p).resolve()).replace('\\','/').lower(), d)
    for name in REVISIONS:
        for x in read(ROOT/'review'/name/'replacement-ledger.json')['replacements']:
            historical[key(ROOT/x['path'],x['previousSHA256'])] = str(ROOT/x['previousSourceRecord'])
    for x in removed:
        p=ROOT/x['path']; rec=Path(str(p)+'.generation.json')
        historical[key(p,x['sha256'])] = str(rec) if rec.exists() else None
    external_history=[]
    def patch_history(obj,record):
        if isinstance(obj,list):
            for item in obj: patch_history(item,record)
        elif isinstance(obj,dict):
            if 'path' in obj and 'sha256' in obj:
                ref_path=Path(obj['path']) if Path(obj['path']).is_absolute() else ROOT/obj['path']
                pair=key(ref_path,obj['sha256'])
                if pair in historical:
                    obj['historicalPath']=obj.pop('path'); obj['historicalSource']=True
                    obj['disposition']='source replaced or removed after verified export; SHA and text retained'
                    if historical[pair]: obj['generationRecord']=historical[pair]
                elif not ref_path.resolve().is_relative_to(ROOT.resolve()):
                    current=sha(ref_path) if ref_path.is_file() else None
                    if current!=obj['sha256']:
                        external_history.append({'record':record,'path':obj['path'],'recordedSHA256':obj['sha256'],'observedCurrentSHA256':current})
                        obj['historicalPath']=obj.pop('path');obj['historicalSource']=True
                        obj['disposition']='external reference no longer matches recorded SHA at cleanup; original digest retained; external file untouched'
            for value in obj.values(): patch_history(value,record)
    texts = set(ROOT.rglob('*.png.generation.json'))
    for name in REVISIONS: texts.update((ROOT/'review'/name/'superseded-records').glob('*.json'))
    removed_paths = {x['path'] for x in removed}
    for p in texts:
        nr=read(p)
        native=Path(str(p).removesuffix('.generation.json'))
        if native.relative_to(ROOT).as_posix() in removed_paths:
            nr['assetDisposition']='source_removed_after_verified_export'; nr['cleanupLedger']='review/cleanup-ledger.json'
        patch_history(nr,p.relative_to(ROOT).as_posix()); save(p,nr)
    save(REV/'historical-external-references.json',{'at':now(),'entries':external_history,'policy':'Preserve original recorded digests; do not relabel old inputs using current external file contents.'})
    for f in m['frames']:
        native=f['nativeProvenance']
        if native['historicalPath'] in removed_paths:
            native['disposition']='removed_after_verified_export'; native['verifiedBeforeCleanup']=True
    save(ROOT/'manifest.json',m)
    for x in removed:
        p=scoped(x['path']); assert sha(p)==x['sha256']; p.unlink()
    report=verify(m,True); save(ROOT/'preview/structure-report.json',report); assert report['passed'],report['errors']
    assert build_html()==0
    save(REV/'cleanup-result.json',{'at':now(),'removedImages':len(removed),'totalLedgerEntries':len(ledger['removed']),'structurePassed':True})
    print(f'Cleaned{len(removed)} temporary images; all final frames and textual provenance retained.')

def handoff():
    m=read(ROOT/'manifest.json');assert m['formalAccepted']
    assert read(REV/'cleanup-result.json')['structurePassed']
    assert read(REV/'timing-verification.json')['passed']
    assert read(ROOT/'preview/structure-report.json')['passed']
    count=len(read(REV/'selection.json')['selected'])
    ledger_count=len(read(ROOT/'review/cleanup-ledger.json')['removed'])
    text=f'''# 07 月影少女 · 动作素材交付

2026-10-04：本轮脚向与接地修订已完成离线验收。当前交付为196张正式1024×1024透明RGBA PNG，以及42个配套连图/APNG预览。正式文件以manifest.json的frames[].path为准，当前验收记录为review/run-grounding-20261004/final-review.json；旧日期记录只代表历史版本。

直接打开[全部动作预览](http://127.0.0.1:8777/preview/index.html)，用页面下方14个动作组按钮切换。支持正常速度、¼慢放、暂停、逐帧、160px/256px/放大检查。页面的图片地址带当前SHA版本参数，避免加载旧帧。本机服务停止时，preview/index.html也可作为本地HTML打开，清单已嵌入页面。

## 本次修订

先按竹弓少女同方向参考修正29张跑步脚向，再修正60张受击/普攻/施法的脚向，最后补修{count}张跑步支撑与交叠。三轮有重叠帧，以最终SHA为准，不能相加当成不同成品数量。保留原先正确帧、人物身份、每手一把弯月匕首和各自摆臂。东南05/13追加修正髋部到膝踝的交叠，避免只改脚尖却提前换腿。

跑步八方向各16张，共128张；受击E/W各6张，共12张；普攻E/W各12张，共24张；施法E/W各16张，共32张。战斗动作范围是E/W，不应理解为八向战斗都已制作。

## 跑步接地和时长

正常跑步固定1200ms/圈，16帧均匀75ms；¼慢放为4800ms/圈、300ms/帧。受击40ms、普攻30ms、施法45ms每帧保持不变。

接地按最新确认的四个位置、每位置两张不同姿态组织：01–02前落地/缓冲，03–04身下承重，05–06后驱，07–08末端前掌蹬离；09–16换另一只脚重复。落地标记在01/09，末端蹬离标记在08/16。逐方向A/B腿别及128张实图SHA见review/run-phase-review.json；这些是画面相位描述，不是碰撞检测或物理锁脚。

脚跟到脚尖遵循各朝向，远近脚保持透视。统一画布根点[512,968]是近地参考，后方脚不能硬拉到前脚同一水平线。没有逐帧裁框缩放、整体平移、镜像、复制凑帧、插值或最低像素贴地。每张新原生图为1254×1254，再全画布等比缩至1024×1024。

## 验收范围

逐张查看新原生候选，并复核最终八组跑步与六组战斗连图的脚向、腿部衔接、手和双刀。浏览器实际验证各组正常播放的末帧、慢放和循环状态，记录见本轮browser-check.json及direction-combat-20261004/browser-check.json。实际APNG延时与页面播放函数的56项虚拟时钟检查均通过。浏览器检查是状态/画面采样，没有连续录屏；结构和计时测试不代替美术判断。

本次只交付角色素材和离线预览。没有修改、接入、启动或测试D:/work/mmorpg-client。世界位移、脚底阴影、游戏速度匹配、滑步和技能判定仍须在客户端接入时实测。

## 来源与保留

本轮使用宿主内置image_gen.imagegen。每张PNG的.generation.json指向原生SHA、真实提示词、参考用途和工具回执；模型/质量配置目标与实际返回值分开记录，工具未披露的实际型号/质量均为null。三轮提示词与请求索引分别在review/direction-alignment-20261004、review/direction-combat-20261004、review/run-grounding-20261004下的prompt-index.json。

按项目保留规则，最终文件及引用核验后已删除本角色过程原生图、拒稿和临时检查连图；当前删除台账共{ledger_count}条。仅保留196张游戏PNG和42个必要预览图片，来源文字不删除。其他角色后来更新的参考文件按原SHA标记为历史来源，没有用新SHA回填旧记录，也没有删除角色目录之外的文件或宿主缓存。

复核命令（Python需Pillow）：

```powershell
python -X utf8 -B tools/verify_manifest.py --require-complete --report
python -X utf8 -B tools/check_direction_delivery.py --revision review/run-grounding-20261004
python -X utf8 -B tools/check_final_previews.py
```

重建当前42个预览和HTML使用tools/rebuild_previews.py；仅重建HTML使用tools/build_preview.py。旧export_candidates、finalize_delivery、revise_feet和complete_*脚本是历史流程，不要重新运行覆盖当前成品。
'''
    (ROOT/'MERGE_HANDOFF.md').write_text(text,encoding='utf-8')
    print('Updated final handoff with current counts, paths and verification scope.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['phases','accept','cleanup','prompt_indexes','handoff'])
    globals()[p.parse_args().mode]()
