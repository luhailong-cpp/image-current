from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
selection={
'hit': ['hit-E-01','hit-E-02','hit-E-03','hit-E-04-r2','hit-E-05','hit-E-06'],
'attack':['attack-E-01','attack-E-02','attack-E-03','attack-E-04-r2','attack-E-05-r3','attack-E-06-r2','attack-E-07-r2','attack-E-08-r2','attack-E-09-r3','attack-E-10','attack-E-11','attack-E-12']
}
notes={
'hit-E-01':'警觉轻缩颈、闭喙；两翼合拢，两足承重。',
'hit-E-02':'闭眼压缩，双翼初张，足趾未换步。',
'hit-E-03':'头颈明显后仰，双翼本能展开，两足抓云；最大反冲。',
'hit-E-04-r2':'保留后仰余量和展翼，眼神开始恢复；比初版直接站直更有过渡。',
'hit-E-05':'颈身回正，翼基本收拢，闭喙；接04的回位较快待播放判断。',
'hit-E-06':'独立中性收势，睁眼张喙，翼落定；未复制01。',
'attack-E-01':'目光与闭喙朝右下，起手轻屈腿；支撑基准。',
'attack-E-02':'双腿共同下压，翼松开；头颈略回收。',
'attack-E-03':'出现S形颈部和聚焦表情，近翼后掠；两足承重。',
'attack-E-04-r2':'低头紧S颈蓄力，双翼后掠；替换初版竖直颈。',
'attack-E-05-r3':'前伸起始，翼后掠；支撑位置较原版及r2接近起手01，仍非像素一致。',
'attack-E-06-r2':'主线程定点修；本子组仅纳入静态联系表，主线程负责该帧选择。',
'attack-E-07-r2':'主线程定点修峰值；本子组仅纳入静态联系表，主线程负责该帧选择。',
'attack-E-08-r2':'仍保持前刺伸展与后掠翼，避免初版直接站直；云足较起手偏高，必须动态复核。',
'attack-E-09-r3':'半回收，斜向颈开始折回、翼落下；支撑较初版改善，仍有小幅差异。',
'attack-E-10':'头颈回到胸上方、腿回弹，翼基本合拢；回位阶段。',
'attack-E-11':'警觉眼神恢复、微张喙、合翼；独立姿态。',
'attack-E-12':'近中性收势；金环红冠、单坠、两翼两足单尾保持。'
}
selected=set(sum(selection.values(),[]))
for action in selection:
    for rp in (ROOT/'records').glob(f'{action}-E-*.json'):
        data=json.loads(rp.read_text(encoding='utf-8-sig'))
        if action=='attack' and data.get('frame') in (6,7): continue
        yes=data['id'] in selected
        data['selected']=yes
        data['status']='selected-pending-playback' if yes else 'superseded'
        data['visualStatus']='individual static inspected; final playback pending' if yes else 'rejected/superseded candidate'
        if yes:data['individualVisualNote']=notes[data['id']]
        rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qa=ROOT/'qa'
qa.mkdir(exist_ok=True)
report={'scope':'E hit 6 + attack 12, static review by e_hit_attack agent','selected':selection,'playbackStatus':'not performed by this subagent; parent unified playback required','clientIntegration':'not performed','frames':[],'limitations':['云垫和支撑位置仍有生成级差异，attack-E-08-r2偏高最明显。','缩放/导出须同方向统一变换，不逐帧对脚或整图平移补偿。','模型/质量实际未披露，所有源图记录维持null。']}
for action,ids in selection.items():
    out=Image.new('RGB',(6*300,((len(ids)+5)//6)*330),(224,226,222))
    draw=ImageDraw.Draw(out)
    for i,ident in enumerate(ids):
        p=ROOT/'source'/f'{ident}.png'
        im=Image.open(p).convert('RGBA')
        alpha=im.getchannel('A')
        rec={'id':ident,'width':im.width,'height':im.height,'mode':'RGBA','alphaExtrema':list(alpha.getextrema()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'note':notes[ident]}
        report['frames'].append(rec)
        thumbnail=im.resize((296,296),Image.Resampling.LANCZOS)
        thumbBg=Image.new('RGBA',thumbnail.size,(224,226,222,255))
        thumbBg.alpha_composite(thumbnail)
        x=(i%6)*300;y=(i//6)*330
        out.paste(thumbBg.convert('RGB'),(x+2,y+25))
        draw.text((x+5,y+5),ident,fill=(20,30,25))
    out.save(qa/f'e-{action}-selected-contact.png')
report['uniqueSha256']=len({r['sha256'] for r in report['frames']})
report['all18Present']=len(report['frames'])==18
report['allNative1254RGBA']=all(r['width']==1254 and r['height']==1254 and r['mode']=='RGBA' for r in report['frames'])
report['allAlphaTransparentAndVisible']=all(r['alphaExtrema'][0]==0 and r['alphaExtrema'][1]>0 for r in report['frames'])
(ROOT/'records'/'e-hit-attack-static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['uniqueSha256','all18Present','allNative1254RGBA','allAlphaTransparentAndVisible']},ensure_ascii=False))

