import json,hashlib
from pathlib import Path
from PIL import Image
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/legacy-yun-jiu-jiu')
notes={
'hit-W-01':'轻缩颈警觉；双翼收拢，两足承重，W后脑/背面可辨。',
'hit-W-02':'缩颈闭眼压缩，双翼开始展开；两足仍支撑。冠羽随压缩前摆。',
'hit-W-03':'反冲峰值，头颈后弧，双翼张开；单尾束可辨，双足抓云。',
'hit-W-04':'颈部回弹，双翼下降半收；头部较前帧向左回正，连播需检查摆幅。',
'hit-W-05':'颈部近回正，翼羽近收拢，两腿恢复。',
'hit-W-06':'独立近中性收势，颈部略抬，翼羽完全收回。',
'attack-W-01':'警觉准备；背面身份稳定，右侧翼略抬作准备。',
'attack-W-02':'腿部屈曲，肩翼开始回收；两足未交替踏步。',
'attack-W-03':'缩颈蓄力明显，腿部压缩，尾束保持单束。',
'attack-W-04':'双翼后掠蓄力；颈部S形，身体后仰支撑。',
'attack-W-05':'头颈向左上伸出，后脑与后领仍占主面，双翼后掠。',
'attack-W-06':'加速前刺，颈线前伸，双足支撑，肢翼尾数正确。',
'attack-W-07-r1':'攻击最大伸展；定点AI修复原07云垫/足点右偏，偏移减小。仍须动态核验。',
'attack-W-08':'头颈回拉，双翼收拢；回收较快，需按30ms连播看07到08节奏。',
'attack-W-09':'颈部近回正，翼羽完全靠体，尾束回收。',
'attack-W-10':'双腿回弹至近直立，颈部恢复直立，云垫仍是单个。',
'attack-W-11':'注意力恢复、肩翼放松，冠羽小幅摆动。',
'attack-W-12':'独立最终近中性收势，翼羽全收，冠羽和颈身安定。'
}
rows=[]
for id,note in notes.items():
    rp=root/'records'/f'{id}.json'
    d=json.loads(rp.read_text(encoding='utf-8'))
    path=root/d['file']
    with Image.open(path) as im:
        alpha=im.getchannel('A')
        lo,hi=alpha.getextrema()
        bbox=alpha.getbbox()
        technical={'size':[im.width,im.height],'mode':im.mode,'alphaExtrema':[lo,hi],'alphaBbox':bbox,'recordShaMatches':hashlib.sha256(path.read_bytes()).hexdigest()==d['sha256']}
    d['visualStatus']='individual static review complete; playback and final export pending'
    d['individualVisualReview']={'method':'inspected every actual image_gen returned image at generation time','note':note,'identityDirectionAnatomy':'rear W view, two wings, two golden feet, one tail bundle, no chest medallion on back','limitation':'Static observation does not certify temporal continuity, stable support, final 1024 export or client integration.'}
    d['technicalSourceCheck']=technical
    rp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows.append({'id':id,'source':d['file'],'record':f'records/{id}.json','note':note,**technical,'sha256':d['sha256']})
rp=root/'records'/'attack-W-07.json'
d=json.loads(rp.read_text(encoding='utf-8'))
d['visualStatus']='rejected - cloud and both feet drifted right relative to adjacent frames'
d['replacedBy']='records/attack-W-07-r1.json'
d['cleanupAfterFinalReferenceValidation']=True
rp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result={'schemaVersion':1,'scope':'W hit 6 and attack 12','selectedFrameCount':len(rows),'selectedSourceFilesUnique':len({x['sha256'] for x in rows})==len(rows),'individualStaticReview':'all selected actual generated images inspected','playbackReview':'pending parent-thread unified normal/slow/frame preview','final1024Export':'pending parent thread','selectedOverride':{'attack/W/07':'source/attack-W-07-r1.png'},'failedCalls':[{'id':'hit-W-05','stage':'initial generation','result':'network error: error sending request','imageReturned':False,'resolution':'same saved prompt retried successfully'}],'rejectedCandidates':[{'source':'source/attack-W-07.png','record':'records/attack-W-07.json','reason':'support cloud and both feet shifted approximately 40-50 native pixels right from preceding frame','replacement':'source/attack-W-07-r1.png'}],'remainingVisualChecks':['AI-generated cloud outline and foot positions show small frame-to-frame changes; inspect playback without per-frame reanchoring.','Check hit03 to04 head rebound amplitude.','Check attack07-r1 to08 fast recovery at30ms.','Check head/torso scale consistency across attack09 to12 and exact final transparency margins.'],'frames':rows}
(root/'records'/'W-hit-attack-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(rows),'all1254RGBA':all(x['size']==[1254,1254] and x['mode']=='RGBA' for x in rows),'allAlphaHasTransparentAndOpaque':all(x['alphaExtrema']==[0,255] for x in rows),'allSHA':all(x['recordShaMatches'] for x in rows),'uniqueSHA':result['selectedSourceFilesUnique'],'review':'records/W-hit-attack-review.json'},ensure_ascii=False))

