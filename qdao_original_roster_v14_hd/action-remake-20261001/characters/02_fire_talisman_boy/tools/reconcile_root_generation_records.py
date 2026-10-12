from pathlib import Path
import hashlib,json
from PIL import Image
from inventory_sources import current_slots
R=Path(__file__).resolve().parents[1]
current={f.get('native_evidence') or f.get('source_record') for _,f in current_slots(R)}
reasons={'run-E-04-20261004-position-pairs-01':'拒用：生成时多出一只手臂并改变道具位置。','run-SE-12-20261004-position-pairs-01':'拒用：腿部支撑归属不连续。','run-SE-13-20261004-position-pairs-02':'未选用：支撑高度和相邻帧不连贯。','run-SE-13-20261004-position-pairs-03':'被后续修订替代：第四支撑位置未继续向后推进。','run-SE-14-20261004-position-pairs-02':'被后续修订替代：第四支撑位置未继续向后推进。'}
count=0
for p in sorted((R/'records').glob('*.receipt.json')):
    if not ('position-pairs' in p.name or 'grounding-v2' in p.name or 'video-axis' in p.name or '-20261005-full-limb-' in p.name):continue
    recp=p.with_name(p.name.replace('.receipt.json','.json'))
    if not recp.exists():continue
    rec=json.loads(recp.read_text(encoding='utf-8-sig'));receipt=json.loads(p.read_text(encoding='utf-8-sig'))
    native=Path(receipt.get('nativePath',''))
    if not native.is_file():continue
    with Image.open(native) as im:
        nativeinfo={'file':str(native),'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'width':im.width,'height':im.height,'mode':im.mode}
    rec.setdefault('returnedAt',receipt.get('returnedAt'))
    rec.setdefault('unverifiedReason','宿主管理，工具未披露实际型号或质量。')
    rec.setdefault('evidence',{})['receipt']=p.relative_to(R).as_posix()
    if recp.relative_to(R).as_posix() not in current:
        rec['native']=nativeinfo
        rec['selectionStatus']='generated_not_current'
        rec['selectionReason']=reasons.get(recp.stem,'当前正式槽位已由另一张经过复核的独立图片占用；本图不进入游戏资源。')
    recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');count+=1
print({'reconciledRootReceipts':count})
