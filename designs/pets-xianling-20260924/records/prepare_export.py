import json,hashlib,datetime
from pathlib import Path
root=Path(r'E:/work/image/designs/pets-xianling-20260924')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=json.loads(r'''[{"slug":"01-zhuling","identitySummary":"靛蓝灵鸦，铜红翼斑，琥珀云冠、象牙绢领与青瓷烛坠","portrait":{"direction":"E","crop":[490,170,1030,710],"reviewed":true},"anchors":{"E":[690,1202],"W":[645,1180]},"findings":{"originality":"以短尾鸦、铜红翼内斑、绢领和青瓷烛坠重构；与原游戏全身火焰鸟的轮廓、羽色、伴生物不同。","E":"斜前朝右下，双眼、喙、胸羽清楚，两翼和尾完整；主体最右余4px，统一缩小导出。","W":"独立生成斜后朝左上；后脑冠带、翼背与背羽、尾上覆羽为主，仅左侧眼缘可见。","style":"精细羽丝、绢纱、金丝描边和玉坠细节。","integrity":"低Alpha彩色边点已独立诊断，不对蓝紫羽毛做全局去色；主体未触原生画布边缘。"}},{"slug":"02-jiangling","identitySummary":"墨黑短发折绢仙灵，象牙绛红折瓣衣、青玉丝带与三铃折扇","portrait":{"direction":"E","crop":[365,45,995,675],"reviewed":true},"anchors":{"E":[690,1155],"W":[680,1138]},"findings":{"originality":"短墨发、折瓣绢衣、金折叶发饰、三铃折扇形成独立身份；与长棕发粉长裙仙女不同。","E":"斜前朝右下，右手折扇三铃位于画面左侧，两脚完整。","W":"斜后朝左上，后脑、后斗篷、腰扣和鞋底为主；右手扇转到画面右侧，没有镜像前脸。","style":"半透绢袖、温润白绛配色与细金纹，保留活泼Q版表情。","integrity":"发饰、折扇、铃穗、绢带与两脚完整。"}},{"slug":"04-guideng","identitySummary":"栗发桂灯仙童，金脉叶帽、象牙杏青丝衣、桂花枝与六角木灯","portrait":{"direction":"E","crop":[320,40,955,675],"reviewed":true},"anchors":{"E":[665,1145],"W":[705,1138]},"findings":{"originality":"男童、叶帽、灯与枝、短宽裤作为全新造型，避开原女仙的蓝黑长发与层叠粉裙。","E":"斜前朝右下，右手灯在画面左侧，左手桂花枝在右侧。","W":"真正斜后朝左上，帽背、后脑、披肩、后腰带结、宽裤和鞋底清楚；手持两物解剖侧一致。","style":"杏色绢披肩、金脉叶帽、浅玉腰带及含蓄灯光营造仙气。","integrity":"灯帽、花枝、流苏与双脚均完整，灯光未烘焙成地面光圈。"}},{"slug":"15-landuoxian","identitySummary":"墨靛发无翼玉衣仙童，象牙青玉杏色绢袍，三玉铎金环与玉槌","portrait":{"direction":"E","crop":[365,0,1015,650],"reviewed":true},"anchors":{"E":[665,1225],"W":[632,1200]},"findings":{"originality":"墨靛发半髻侧辫、无翼衣袍、三玉铎与玉槌替代原白发蓝翼长枪男仙；未复制羽舟少女的坐姿或羽舟。","E":"斜前朝右下，右手三铎在画面左侧，左手玉槌在右侧；全身完整。","W":"真斜后朝左上，后髻、辫背、后袍和鞋跟为主，三铎转到画面右侧而玉槌在左侧。","style":"精细青玉纱袖、杏色内衬、象牙绢袍和轻金桂花纹。","integrity":"顶髻、长绢带、三铎、槌与双靴全部完整，独立背视可辨。"}}]''')
config=read(root/'asset-config.json')
for row in data:
    slug=row['slug']; pet=next(p for p in config['pets'] if p['slug']==slug)
    proposal={**pet,**{k:v for k,v in row.items() if k!='findings'},'originalityReview':'assistant-reviewed-original-design'}
    write(root/f'records/{slug}-config-proposal.json',proposal)
    review={'schemaVersion':1,'slug':slug,'name':pet['name'],'status':'passed-agent-visual-review','findings':row['findings'],'portrait':row['portrait'],'anchors':row['anchors'],'sourceHashes':{d:hashlib.sha256((root/f'source/{slug}-{d}.png').read_bytes()).hexdigest() for d in ['E','W']},'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'userApproval':False,'clientIntegrated':False,'scope':'Native source and crop proposal review; final exported composite review separate.'}
    write(root/f'records/{slug}-visual-review.json',review)
for pet in config['pets']:
    prop=read(root/f"records/{pet['slug']}-config-proposal.json")
    pet.update(prop)
config['originalDesignPolicy']['status']='assistant-reviewed-new-ethereal-sources'
write(root/'asset-config.json',config)
audit={'schemaVersion':1,'status':'assistant-reviewed','userApproved':False,'legalConclusion':None,'scope':'Original visual redesign compared with reference-slot identity, not a legal conclusion.','pets':[]}
for pet in config['pets']:
    rv=read(root/f"records/{pet['slug']}-visual-review.json")
    audit['pets'].append({'slug':pet['slug'],'name':pet['name'],'slotReferenceName':pet['slotReferenceName'],'newIdentity':pet['identitySummary'],'elementsToAvoid':pet['avoidReferenceIdentity'],'actualImageAudit':rv.get('findings',{}).get('originality',rv.get('originality')),'reviewRecord':f"records/{pet['slug']}-visual-review.json"})
write(root/'records/originality-review.json',audit)
print('Merged',len(config['pets']),'fresh observed crop/anchor proposals')

