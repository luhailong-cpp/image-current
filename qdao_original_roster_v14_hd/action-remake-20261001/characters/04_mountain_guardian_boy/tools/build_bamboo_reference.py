"""Bind current 04 and user-approved 09 files for a read-only side-by-side review."""
from timing_profile import RUN_FRAME_MS
if RUN_FRAME_MS != 75:
    raise SystemExit('历史75ms竹弓对照构建已停用；当前入口为preview/gallery.html。')
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT.parent/'09_bamboo_archer_girl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
manifest=read(REF/'manifest.json'); timing=read(ROOT/'runtime_timing.json'); sequences=[]; bindings=[]
for sequence in manifest['sequences']:
    a,d=sequence['action'],sequence['direction']; left=[];right=[]
    for frame in sequence['frames']:
        n=frame['frame']; ref=REF/frame['file']; own=ROOT/f'frames/{a}/{d}/frame_{n:02d}.png'
        assert ref.is_relative_to(REF) and sha(ref)==frame['sha256']
        own_sha=sha(own)
        left.append('../'+own.relative_to(ROOT).as_posix()+'?sha='+own_sha[:16])
        right.append('../../'+REF.name+'/'+frame['file']+'?sha='+frame['sha256'][:16])
        bindings.append({'action':a,'direction':d,'frame':n,'ownFile':own.relative_to(ROOT).as_posix(),'ownSha256':own_sha,'referenceFile':frame['file'],'referenceSha256':frame['sha256']})
    durations=timing['run']['offlineFrameDurationsMs'] if a=='run' else [timing[a]['frameMs']]*len(left)
    sequences.append({'key':a+'/'+d,'left':left,'right':right,'durationsLeft':durations,'durationsRight':[75 if a=='run' else sequence['ms']]*len(right),'referenceOriginalFrameMs':sequence['ms']})
out=ROOT/'preview/bamboo-reference-data.js'
out.write_text('const referenceSequences='+json.dumps(sequences,ensure_ascii=False)+';\n',encoding='utf-8')
record={'createdAt':datetime.now(timezone.utc).isoformat(),'referenceCharacter':REF.name,'referenceAuthority':'用户2026-10-03明确确认竹弓少女当前版，并授权其他角色同向参照。','referenceManifestSha256':sha(REF/'manifest.json'),'referenceTimingSha256':sha(REF/'animation-timing.json'),'ownTimingSha256':sha(ROOT/'runtime_timing.json'),'bindings':bindings,'note':'依用户最新要求，本对照页两侧跑步均按75ms/帧共1200ms；仅本地播放只读09图片，没有改09参数。同帧号未必同解剖相位，不复制像素。'}
(ROOT/'provenance/audit/bamboo_reference_bindings_20261003.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sequences':len(sequences),'frameBindings':len(bindings),'referenceHashMatches':len(bindings)},ensure_ascii=False))
