"""Export the explicitly selected review pixels; preserve their provenance.

No pose editing, per-frame registration, mirroring, or interpolation happens here.
Run build_preview.py first whenever the source selection changes. This exporter
also works after source-image cleanup because it reads the fixed review export.
After candidate cleanup, verify_delivery.py verifies the shipped files directly.
"""
from pathlib import Path
import datetime, hashlib, json, re, shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, obj: p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
review = json.loads((ROOT/'review-manifest.json').read_text(encoding='utf-8'))
selection = json.loads((ROOT/'review-selection.json').read_text(encoding='utf-8-sig'))
assert review['reviewExported'] == 196
assert len(selection) == 14 and sum(map(len, selection.values())) == 196
frames, groups = [], []
for original in review['frames']:
    item = json.loads(json.dumps(original))
    src = ROOT/item['file']
    assert sha(src) == item['sha256'], src
    with Image.open(src) as im:
        assert im.size == (1024,1024) and im.mode == 'RGBA'
        assert im.getchannel('A').getextrema() == (0,255)
    dest = ROOT/'runtime'/Path(*item['slot'].split('/')).with_suffix('.png')
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src,dest)
    item['file'] = dest.relative_to(ROOT).as_posix()
    item['status'] = 'exported_for_integration_review'
    item['staticPoseReviewed'] = True
    item['visualAccepted'] = False
    item['dynamicAccepted'] = False
    item['clientIntegrated'] = False
    item['acceptanceNote'] = '逐帧静态核查及浏览器播放检查完成；仍不等于完整离线动态美术通过或客户端验收。具体未解决项见MERGE_HANDOFF.md。'
    write(Path(str(dest)+'.generation.json'), item)
    frames.append(item)
assert len({x['sha256'] for x in frames}) == 196
assert len({x['derivedFrom']['sha256'] for x in frames}) == 196
for key, sources in selection.items():
    action, direction = key.split('/')
    ms = {'run':45,'hit':40,'attack':30,'cast':45}[action]
    fs = [x for x in frames if x['slot'].rsplit('/',1)[0] == key]
    assert len(fs) == len(sources)
    group = {'key':key, 'ms':ms, 'frames':['../'+x['file']+'?v='+x['sha256'][:12] for x in fs]}
    groups.append(group)
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest = {'character':'08_alchemy_prodigy_boy','updatedAt':now,
    'targetFrames':196,'generatedSelectedFrames':196,'exportedFrames':196,
    'staticPoseReviewedFrames':196,'visualAcceptedFrames':0,'dynamicAcceptedFrames':0,
    'clientIntegrated':False,'clientValidated':False,'canvas':[1024,1024],
    'rootPx':[512,942],'rootMeaning':'logical placement reference; not a measured flat ground for every foot',
    'transform':{'wholeCanvasTo':[940,940],'offset':[42,50],'perFrameFit':False},
    'timing':{'run':{'previewDefaultCycleMs':720,'comparisonCycleMs':[480,640,720,800],
                     'previewFrameMs':[45]*16,'clientFinalized':False,'weightedTiming':False},
              'hit':{'frameMs':[40]*6,'cycleMs':240},
              'attack':{'frameMs':[30]*12,'cycleMs':360,'contactMarker':{'E':6,'W':6}},
              'cast':{'frameMs':[45]*16,'cycleMs':720,'releaseMarker':{'E':9,'W':10}}},
    'sourceImages':'Historical native inputs; cleanup inventory records removals after closed export references.',
    'frames':frames}
write(ROOT/'manifest.json',manifest)
data = ROOT/'preview/data.js'
data.write_text('window.PREVIEW_DATA='+json.dumps(groups,ensure_ascii=False)+';',encoding='utf-8')
html = ROOT/'preview/index.html'
source = html.read_text(encoding='utf-8')
source = re.sub(r'src="data\.js(?:\?v=[^"]*)?"','src="data.js?v='+sha(data)[:12]+'"',source)
html.write_text(source,encoding='utf-8')
print(json.dumps({'exported':len(frames),'uniqueSources':len({x['derivedFrom']['sha256'] for x in frames}),'groups':len(groups)}))
