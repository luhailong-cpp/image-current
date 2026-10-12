from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'delivery-current.json').read_text(encoding='utf-8'))
current={f['file']:f['sha256'] for fs in d['groups'].values() for f in fs}
assert len(current)==196
checks=[]
for name in ['index.html','timing-grounding.html']:
    p=R/'preview'/name;text=p.read_text(encoding='utf-8')
    embedded=json.loads(text.split('const DATA=',1)[1].split(',onlyRun=',1)[0])
    assert embedded['orders']=={} and embedded['runFrameMs']==60 and embedded['runCycleMs']==960
    count=0
    for group,frames in embedded['groups'].items():
        for f in frames:
            target=(p.parent/f['candidateUrl'].split('?',1)[0]).resolve()
            assert target.is_relative_to((R/'runtime').resolve()) and target.exists()
            assert sha(target)==f['sha256']==current[target.relative_to(R.resolve()).as_posix()]
            count+=1
    assert count==196
    for href in re.findall(r'href="([^"#]+)"',text):
        if '://' not in href:assert (p.parent/href).exists(),href
    checks.append({'page':p.relative_to(R).as_posix(),'runtimeReferences':count,'brokenReferences':0})
p=R/'preview/all-directions.html'
overview=p.read_text(encoding='utf-8')
groups=json.loads(overview.split('const GROUPS=',1)[1].split(',PLAN=',1)[0])
assert len(groups)==8 and all(len(urls)==16 for urls in groups.values())
for urls in groups.values():
    for url in urls:
        target=(p.parent/url.split('?',1)[0]).resolve()
        assert target.is_relative_to((R/'runtime').resolve()) and target.exists()
        assert sha(target)==current[target.relative_to(R.resolve()).as_posix()]
checks.append({'page':p.relative_to(R).as_posix(),'runtimeReferences':128,'brokenReferences':0})
for p in (R/'preview').glob('*-contact.jpg.generation.json'):
    if not Path(str(p).removesuffix('.generation.json')).exists():continue
    rec=json.loads(p.read_text(encoding='utf-8'))
    for item in rec['derivedFrom']:assert sha(R/item['file'])==item['sha256']
retention=json.loads((R/'retention-report.json').read_text(encoding='utf-8'))
after_cleanup=retention['status']=='applied' and all(not (R/row['file']).exists() for row in retention['files']) and not any((R/'run-axis-revision-20261004').rglob('native.png')) and not any((R/'full-limb-review-20261004').rglob('native.png'))
report={'status':'passed','afterNativeImageCleanup':after_cleanup,'pages':checks,'currentRuntimeFiles':196,'clientRuntimeTested':False}
(R/'preview/reference-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
