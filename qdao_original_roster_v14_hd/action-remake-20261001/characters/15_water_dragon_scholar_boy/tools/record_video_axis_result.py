"""Bind the video-feedback repair result to exact before/after runtime hashes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before = read(ROOT/'audit/video-direction-20261004/before-repair.json')
    manifest = read(ROOT/'manifest.json')
    old = {r['slot']: r for r in before['frames']}
    changes, retained = [], []
    for row in manifest['frames']:
        assert sha(ROOT/row['output']) == row['sha256']
        prior = old[row['slot']]
        item = {'slot':row['slot'], 'beforeSource':prior['source'], 'beforeSourceSha256':prior['sourceSha256'],
                'beforeOutputSha256':prior['outputSha256'], 'source':row['source'],
                'sourceSha256':row['derivedFrom']['sha256'], 'output':row['output'], 'outputSha256':row['sha256']}
        if prior['outputSha256'] != row['sha256']:
            assert 'video-axis' in row['source'] or 'video-hands' in row['source']
            item['generationRecord'] = row['derivedFrom']['generationRecord']
            item['generationRecordSha256'] = row['derivedFrom']['generationRecordSha256']
            changes.append(item)
        else:
            assert prior['sourceSha256'] == row['derivedFrom']['sha256']
            retained.append(item)
    report = {'character':ROOT.name, 'updatedAt':datetime.now(timezone.utc).isoformat(),
              'beforeRecord':'audit/video-direction-20261004/before-repair.json',
              'beforeRecordSha256':sha(ROOT/'audit/video-direction-20261004/before-repair.json'),
              'changedCount':len(changes), 'runFootRepairs':sum(r['slot'] in before['targetSlots'] for r in changes),
              'runHandRepairs':sum(r['slot'].startswith('run-') and 'video-hands' in r['source'] for r in changes),
              'combatHandRepairs':sum(not r['slot'].startswith('run-') for r in changes),
              'unchangedCount':len(retained), 'changes':changes, 'retained':retained,
              'reviewNotes':[
                  'root实际查看参考视频四段连续抽样、截图、身份和画法图；游戏录像角色小且部分遮挡，只用于动作轴线参照，未宣称从录像判定每帧鞋掌细节。',
                  'root逐张查看17张脚向新原生图；正式导出沿用完整1254画布统一缩放940，固定偏移42/49，没有最低像素贴地、镜像、插值或扭曲。',
                  '本轮手部复核新增普攻W03解剖持扇手臂问题；before记录中的全部战斗保留是手部复核前结论，以当前changes为准。',
                  'root实际查看普攻W03手臂v2原生图并与旧W03、W02和W04比较：近左臂跨胸空掌、远右臂举扇连接成立；v1未解决肩侧连接，拒用。',
                  '后续交叉审查将持扇解剖与摆臂弧线分别核对：N11、NW03、E03、W03补过渡。N11同时属于脚向与摆臂修正，分类数量有重叠；以changedCount表示相对本轮开始的独立槽数。',
                  '跑步同一支撑足沿行进轴在连续相对位置各两张独立姿态，每位置120ms，整圈960ms；膝关节保留自然弯曲。'],
              'dynamicReview':'pending_final_dynamic_review', 'clientIntegration':'not_integrated',
              'model':{'configuredTarget':'GPT Image 2.5 Sunburst', 'configuredQuality':'max',
                       'actualModel':None, 'actualQuality':None, 'route':'builtin_host_managed',
                       'reason':'内置工具没有型号/质量选择器，返回未披露，详见逐图请求和回执。'}}
    path = ROOT/'audit/video-direction-20261004/repair-result.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['changedCount','runFootRepairs','runHandRepairs','combatHandRepairs','unchangedCount']}))
if __name__ == '__main__': main()
