from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parent.parent
owned=json.loads((root/'inventory-hit.json').read_text(encoding='utf-8-sig'))
global_inv=json.loads((root/'inventory.json').read_text(encoding='utf-8-sig'))
frames=[f for f in owned['frames'] if f['action']=='hit' and f['direction']=='W']
global_frames={(f['action'],f['direction'],f['frame']):f for f in global_inv['frames']}
for f in frames:
    current=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
    f['sha_matches_disk']=current==f['sha256']
    f['global_preview_manifest_matches']=global_frames.get(('hit','W',f['frame']),{}).get('sha256')==current
gifs=[]
for name in ('hit-W-normal.gif','hit-W-slow.gif'):
    p=root/'previews'/name
    if not p.exists():
        gifs.append({'path':str(p.relative_to(root)),'exists':False});continue
    with Image.open(p) as im:
        durations=[]
        for i in range(im.n_frames):
            im.seek(i);durations.append(im.info.get('duration',0))
        gifs.append({'path':str(p.relative_to(root)),'exists':True,'frames':im.n_frames,'durations_ms':durations,'total_ms':sum(durations),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'time':datetime.now(ZoneInfo('America/New_York')).isoformat(),'action':'hit','direction':'W','frames':sorted(frames,key=lambda f:f['frame']),'gifs':gifs,'pose_review':{'status':'真实独立六阶段逐帧图像已看，持手与方向通过','sequence':['初始惊觉','加深后仰','冲击极点','胸肩前屈缓冲','起身恢复','收势'],'identity':['右手五符扇','左手铜铃红穗','双腿双鞋清楚','未烘焙离体光效'],'pending':['跨帧头部尺度/解剖根点统一标定','正常速度与慢速实际播放视验','完整E/W身份与相机对照']},'browser_review':{'status':'未验证','attempts':['cua.createBrowserTab(iab,http://127.0.0.1:8752/previews/index.html,visible=false): Browser is not available: iab','cua.getBrowser({url}): No browser is available']},'bbox_policy':'最低alpha像素和bbox仅作诊断，不能代替解剖根锚点判定，不做逐帧最低脚贴地。'}
(root/'records/hit-W-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'gifs':gifs,'sha_matches':all(f['sha_matches_disk'] for f in frames),'global_manifest_matches':all(f['global_preview_manifest_matches'] for f in frames),'browser_review':'未验证'},ensure_ascii=False))
