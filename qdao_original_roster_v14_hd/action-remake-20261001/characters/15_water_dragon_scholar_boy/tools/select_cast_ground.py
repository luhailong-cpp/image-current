from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone
b=Path(__file__).resolve().parents[1]
p=b/'audit/cast-selection.json'
d=json.loads(p.read_text(encoding='utf-8'))
old={(f['direction'],f['frame']):f['sha256'] for f in d['frames']}
ap=b/'audit/cast-foot-review.json';a=json.loads(ap.read_text(encoding='utf-8'))
now=datetime.now(timezone.utc).isoformat()
keys={6:'cast-E-06-ground-v3',7:'cast-E-07-ground-v4',9:'cast-E-09-ground-v1'}
review={'reviewedAt':now,'reviewer':'continue_cast','status':'three_ground_edits_static_checked_parent_playback_pending','scope':['E06','E07','E09'],'method':'逐张看完整原图和E05-10同坐标足部连图；只通过内置imagegen局部重画膝/小腿/踝/脚位，未整体移动、缩放或贴靴。','evidence':['audit/cast-E-ground-contact.png','audit/cast-final-review/E-contact.png'],'frames':[],'model':a['model']}
def lower_bounds(path):
 im=Image.open(path).convert('RGBA');aa=im.getchannel('A').point(lambda x:255 if x>=128 else 0)
 boxes=[]
 for x1,x2 in [(0,627),(627,1254)]:
  bb=aa.crop((x1,1140,x2,1254)).getbbox()
  boxes.append([bb[0]+x1,bb[1]+1140,bb[2]+x1,bb[3]+1140] if bb else None)
 return boxes
for n,key in keys.items():
 src=f'sources/new/{key}.png';rec=f'provenance/generation/{key}.json';fp=b/src
 assert fp.exists() and (b/rec).exists()
 im=Image.open(fp);assert im.size==(1254,1254) and im.mode=='RGBA'
 f=next(f for f in d['frames'] if f['direction']=='E' and f['frame']==n)
 prior={'source':f['source'],'sha256':f['sha256'],'generationRecord':f['generationRecord'],'reason':'连帧复核发现E06/07后脚内缩、E09双脚左滑，专项修复下肢脚位，手诀和持扇相位保留'}
 priorboxes=lower_bounds(b/f['source'])
 if f['source']!=src:
  f.setdefault('supersedes',[]).append(prior)
  f.update(source=src,sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),generationRecord=rec)
  f['review']['notes'].append('2026-10-03脚位稳定专项：膝踝连接与后脚/双脚脚位局部修复；双鞋头继续朝E。完整图与相邻帧足部同坐标目检通过；原手诀及右手扇相位保留。残余鞋底高差和轻微轮廓差异列入cast-ground-review，动态交根线程复核。')
  f['review']['reviewedAt']=now
 af=next(f for f in a['frames'] if f['direction']=='E' and f['frame']==n)
 af.update(source=src,sha256=f['sha256'],grounding='corrected_static_checked_parent_playback_pending')
 review['frames'].append({'direction':'E','frame':n,'source':src,'sha256':f['sha256'],'generationRecord':rec,'supersedes':prior,'oldBootLowerAlphaBounds':priorboxes,'newBootLowerAlphaBounds':lower_bounds(fp),'bootBoundsMeasurement':'各半幅y>=1140处alpha>=128非透明范围，仅用于同坐标比较，不能代替手工鞋跟/鞋头判断。','staticPass':['两靴鞋跟在左、鞋头朝右(E)，没有外八','两条下肢与膝踝连接完整','后脚内缩/双脚左滑幅度明显减小，相邻E05/E08落脚区重新接近','右手扇与左手诀原相位保留、未整帧平移或缩放']})
unchanged=[f for f in d['frames'] if not(f['direction']=='E' and f['frame'] in keys)]
assert len(unchanged)==29 and all(old[(f['direction'],f['frame'])]==f['sha256'] for f in unchanged)
review['other29Unchanged']=True
review['limitations']=['E07后靴相对E05/E08仍约20px偏右，E06/07鞋底相对1191参考线仍约15-25px偏下；不声称像素锁地。','E06末次局部生成仍有轻微衣缘/面部轮廓变化，角色大小、朝向和手扇动作相位未改变。','本代理未完成正常/慢速实际浏览器播放，最终连续观感由根线程检查。']
review['rejectedOrSupersededCandidates']={'cast-E-06-ground-v1':'后靴修正向左过约30px','cast-E-06-ground-v2':'后靴偏右约40px','cast-E-07-ground-v1':'网络失败，无图','cast-E-07-ground-v2':'后靴向左过约90px，拒选','cast-E-07-ground-v3':'后靴偏右约40px，后续小范围调整'}
a['updatedAt']=now;a['groundingFollowup']='audit/cast-ground-review.json'
a['finalStaticReview']['limitations'][0]='E06/E07后靴内缩与E09双脚左滑已另行局部修复，见cast-ground-review.json；仍保留相邻帧约20px小幅脚位/鞋底差，需连续播放判断。'
a['evidence']=list(dict.fromkeys(a['evidence']+['audit/cast-E-ground-contact.png']))
for pp,dd in [(p,d),(ap,a),(b/'audit/cast-ground-review.json',review)]:
 pp.write_text(json.dumps(dd,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':keys,'other29Unchanged':True,'bounds':[{k:r[k] for k in ['frame','oldBootLowerAlphaBounds','newBootLowerAlphaBounds']}for r in review['frames']]},ensure_ascii=False))

