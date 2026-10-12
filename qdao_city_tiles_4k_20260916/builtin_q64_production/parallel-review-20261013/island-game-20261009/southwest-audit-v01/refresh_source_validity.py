from pathlib import Path
import json,hashlib,datetime,re
O=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
p=O/'inventory.json';d=json.loads(p.read_text(encoding='utf-8'));checks=[];changed=[]
for f in d['snapshotInputFiles']:
 q=Path(f['path']);h=sha(q) if q.is_file() else None;x={'path':f['path'],'initialSha256':f.get('sha256'),'finalSha256':h,'unchanged':h==f.get('sha256')};checks.append(x)
 if not x['unchanged']:changed.append(x)
changePaths={x['path'] for x in changed};metadataChanged=any(Path(x).name in ('current-native-map.json','progress.json') for x in changePaths)
for t in d['tiles']:
 relevant=[t.get('file')]+[s['path'] for s in t.get('nativePixelValidation',{}).get('sources',[])]+[c['file'] for c in t['selectedCores']]
 t['snapshotStale']=any(x in changePaths for x in relevant)
for a in d['currentVisualReview']['assemblies']:
 a['snapshotStale']=any(T.get('snapshotStale') for T in d['tiles'] if T['tileId'] in a['tiles'])
for a in d['currentVisualReview']['seams']+d['currentVisualReview']['junctions']:
 a['snapshotStale']=any(T.get('snapshotStale') for T in d['tiles'] if T['tileId'] in a.get('pair',a.get('tiles',[])))
d['sourceChangeAudit']={'checkedAtUtc':now(),'checkedFileCount':len(checks),'changedFiles':changed,'allSnapshotInputsUnchanged':not changed,'snapshotStale':bool(changed),'coverageMetadataStale':metadataChanged,'rule':'Changed candidate/source pixels invalidate affected crops/assemblies; changed selection/progress metadata invalidates live coverage totals while unchanged frozen local evidence remains usable.'}
d['ruleUpdate']={'readAtUtc':now(),'rootAgLeafPath':'D:/work/image/AGENTS.md','rootAgSha256':sha('D:/work/image/AGENTS.md'),'generationRule':'Existing free/builtin route: prefer 2.5, allow 2.0 fallback. No paid API or credential changes. This independent audit still invokes no image generation.'}
for x in d['normalizedRepairQueue']:
 if x.get('status'):x['status']='open recorded issue; production owner may repair under current root AGENTS; this independent audit invokes no generation'
d['completedAtUtc']=now();p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'final-rehash.json').write_text(json.dumps({'checkedAtUtc':now(),'files':checks},ensure_ascii=False,indent=2),encoding='utf-8')
(O/'assembly-review-manifest.json').write_text(json.dumps(d['currentVisualReview'],ensure_ascii=False,indent=2),encoding='utf-8')
r=O/'review.md';s=r.read_text(encoding='utf-8');s=s.replace('新 AI 返修在核实 GPT Image 2.5 路线前继续停止。','后续生产由原制作窗口按最新根 AGENTS 执行：现有免费入口 2.5 优先，不可用可用内置 2.0；本独立审计没有调用生图。');s=re.sub(r'最终复 hash：[^\n]+',f"最终复 hash：{len(checks)} 个快照输入，变更 {len(changed)} 个；{'输入稳定' if not changed else '覆盖快照已标过期，逐局部证据有效性见 inventory.json 的 snapshotStale 字段'}。",s);s+='\n已重读用户 2026-10-13 最新根指令。原制作窗口已恢复；本报告为固定输入快照审核，不取代原制作 progress，也不声明全项目暂停。\n';r.write_text(s,encoding='utf-8')
f=O/'finalize.py';s=f.read_text(encoding='utf-8');s=s.replace('新 AI 返修在核实 GPT Image 2.5 路线前继续停止。','后续生产遵循最新根 AGENTS：现有免费 2.5 优先，不可用可用内置 2.0；本审计零生图。');f.write_text(s,encoding='utf-8')
print(json.dumps({'changedFiles':changed,'coverageMetadataStale':metadataChanged,'staleTiles':[t['tileId'] for t in d['tiles'] if t['snapshotStale']]},ensure_ascii=False))
