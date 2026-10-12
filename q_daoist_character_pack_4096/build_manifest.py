"""Validate and index all 24 final portraits without regenerating images."""
from pathlib import Path
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parent
NAMES={1:'冰剑少女',2:'火符少年',3:'莲花医者',4:'山岳守卫',5:'天音少女',6:'雷法少年',
       7:'月影少女',8:'炼丹童子',9:'竹弓少女',10:'赤枪少女',11:'玉拳少年',12:'铁刀少年',
       13:'风刃少女',14:'唤雪少女',15:'水龙书生',16:'金铃舞者',17:'灵篆书生',18:'沙海日轮少女',
       19:'御兽少年',20:'星阵少女',21:'厨道童子',22:'执刀小侍'}

def main():
    paths=sorted(ROOT.glob('*.png'))
    assert len(paths)==24,f'Expected 24 final portraits, found {len(paths)}'
    items=[]
    for path in paths:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            assert im.size==(4096,4096) and im.mode=='RGBA'
            alpha=im.getchannel('A'); bounds=alpha.getbbox()
            assert alpha.getextrema()==(0,255)
            assert bounds and min(bounds[0],bounds[1],4096-bounds[2],4096-bounds[3])>16
        number=int(path.name[:2]) if path.name[:2].isdigit() else 0
        record=ROOT/'records'/f'{path.stem}.json'
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        if number:
            assert record.exists()
            provenance=json.loads(record.read_text(encoding='utf8'))
            assert provenance['sha256']==sha,path.name
            assert (ROOT/provenance['prompt']).is_file()
        items.append({'id':path.stem,'name':NAMES.get(number,'金发带Q道童'),
            'path':path.name,'size':[4096,4096],'mode':'RGBA','alpha_range':[0,255],
            'subject_bounds':list(bounds),'sha256':sha,
            'creation_method':'individual built-in image_gen redraw + skill cleanup' if number else 'approved Q hero compatibility export',
            'record':record.relative_to(ROOT).as_posix() if number else '../qdao_asset_refresh_v6/hero_compat_manifest.json'})
    manifest={'schema':'qdao.portraits.v6','baseline_commit':'60134a6','final_count':24,
        'individually_redrawn_characters':22,'canonical_hero_aliases':2,
        'common_size':[4096,4096],'native_size_policy':'Native generation recorded per image; 4096 is compatibility export, not native AI resolution',
        'status':'static_art_only','engine_integration':False,'assets':items}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# 五行奇谈 · 4096 透明人物包','',
        '原24个PNG路径和4096×4096画布保持不变。22个职业人物逐张使用内置image_gen重绘，按新版大头、圆脸、短身Q比例统一，保留各人的法器、发型与属性身份。两张参考道童统一复用已确认金发带角色。','',
        '每张最终图均为真RGBA。原生生成通常1254×1254；通过generate2dsprite色键清理、脚底对齐后等比导出4096。4096是兼容画布，不代表原生4K细节。','',
        '[逐图清单](manifest.json)记录尺寸、Alpha、边界、哈希与生成记录。完整提示词在prompts/，来源ID、原始哈希和技能处理数据在records/。过程母图、裁格和GIF不作为交付；重新生成需运行内置生图并视觉验收，然后用[处理入口](process_portrait.py)导出。','',
        '```powershell','python q_daoist_character_pack_4096/build_manifest.py',
        'python q_daoist_character_pack_4096/process_portrait.py --raw <本轮内置生图输出> --id <原文件stem>','```','',
        '|角色|最终图片|','|---|---|']
    lines += [f"|{i['name']}|[{i['id']}]({i['path']})|" for i in items]
    lines += ['', '此包是静态人物；移动32帧见[八方向动作](../character_move_8dir/README.md)。未接入客户端、骨骼或战斗技能。']
    (ROOT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print('Verified 24 portraits: 22 redraws + 2 canonical hero exports; all 4096 RGBA')

if __name__=='__main__': main()
