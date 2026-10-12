from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'audit/run-NE-paired-ground-review.json';d=read(p)
extra={r['frame']:r for r in read(ROOT/'audit/run-NE-09-10-axis-finish-review.json')['frames']}
extra[8]=read(ROOT/'audit/NE08-boot-axis-final-review.json')
for f in [11,12]:
 extra[f]={'frame':f,'sha256':sha(ROOT/f'runtime/run/NE/{f:02d}.png'),'status':'static_boot_axis_corrected_dynamic_pending',
 'evidence':'ROOT实际查看原生结果和当前1024原图：支撑右靴缩短侧向鞋尖、朝右上纵深收回；同侧膝踝/另一脚悬空与上身手弓保留。',
 'footOrientation':'鞋跟近、鞋尖远右上，侧向长鞋掌已收短；没有用整图位移替代靴轴修正。'}
coords={8:[746,949],9:[714,956],10:[735,950],11:[626,951],12:[670,952]}
for r in d['frames']:
 f=r['frame'];current=sha(ROOT/r['file'])
 if f in extra:
  e=extra[f];assert e['sha256']==current
  r.update(sha256=current,status=e.get('status','static_boot_axis_corrected_dynamic_pending'),staticStatus='boot_axis_corrected_contact_pose_reviewed',evidence=e['evidence'],footOrientation=e['footOrientation'],approxSupportBootCenter1024=coords[f],inspection='Current 1024 PNG and native result independently inspected by ROOT; NE09/10 also reviewed by finish_sw_nw.')
 else:assert current==r['sha256'],f
for pair in d['spatialPairs']:
 for i,f in enumerate(pair['frames']):
  if f in coords:pair['actualApproxBootCenters'][i]=coords[f]
 pair['meanX']=sum(x[0] for x in pair['actualApproxBootCenters'])/2
 pair['sameFootRoots']='后视斜向沿可见裤口与大腿/膝踝连续观察；NE08–12只窄修承重右靴方向，未更换腿。'
d['reviewedAt']=datetime.now(timezone.utc).isoformat()
d['reviewer']='finish_e_ne plus finish_sw_nw and ROOT final boot-axis inspection'
d['bootAxisRepairs']={'frames':[8,9,10,11,12],'actualSourceHashesCurrent':True,'method':'Builtin imagegen narrow boot rotation; native full canvas downsample only','dynamicVisualAcceptance':False}
d['status']='current_paired_contact_and_boot_axis_repairs_saved_dynamic_pending'
d['remainingNotPassed']=[
 '每对是两张独立连续姿态，不是固定同一几何坐标；03/04及11/12仍有约40–55px投影差异，世界坐标锁脚没有验证。',
 '左脚前位15/16到近身01/02的头髋高度变化、鞋跟透视接缝仍需实播复核；08–12外向鞋尖已实际窄修，不再沿用旧侧向靴图。',
 '透明单帧支持姿态接触推断；真实地面承重/滑步、正常1200ms循环及慢放视觉验收尚未完成。']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('NE08-12 current boot-axis revisions merged; all 16 frame hashes current.')

