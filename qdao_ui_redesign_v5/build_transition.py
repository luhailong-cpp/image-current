"""Export the accepted transition and true-alpha clouds, retaining old paths."""
from pathlib import Path
import hashlib, json, os, shutil
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SIZE = (2560,1080)

def metadata(path):
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        result = {'path':os.path.relpath(path,ROOT).replace('\\','/'),'size':list(im.size),
                  'mode':im.mode,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        if 'A' in im.getbands():
            a=im.getchannel('A'); hist=a.histogram()
            result.update(alpha_range=list(a.getextrema()),transparent_pixels=hist[0],opaque_pixels=hist[255])
        return result


def guard_superseded_full_export():
    manifest_path=ROOT/'manifest.json'
    if manifest_path.exists():
        current=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        if current.get('festival_scene_sync') or current.get('prelogin_refinement'):
            raise RuntimeError('Legacy whole export is superseded: historical source/05 and source/06 must not overwrite current festival scenes or regenerate preserved clouds. Verify current files with: python qdao_ui_redesign_v5/export_ui.py --check. Reproduce accepted scene outputs only inside the task folder with: python qdao_festival_refinement_20260910/scenes-sync/build_scene_sync.py reproduce. See qdao_festival_refinement_20260910/scenes-sync/README.md for current source and server composition records.')

def export_transition():
    guard_superseded_full_export()
    src=ROOT/'source/06_battle_entry_clouds_fg.png'
    dst=ROOT/'06_battle_entry_clouds_fg_2560x1080.png'
    with Image.open(src) as original:
        assert original.mode=='RGBA' and original.getchannel('A').getextrema()==(0,255)
        assert abs((original.width/original.height)/(SIZE[0]/SIZE[1])-1)<0.01
        fitted=ImageOps.fit(original,SIZE,method=Image.Resampling.LANCZOS)
        fitted.putalpha(fitted.getchannel('A').point(lambda value: 0 if value <= 1 else value))
        fitted.save(dst,optimize=True)
    with Image.open(dst) as cloud:
        # The focal area must be genuinely empty, including the top-centre.
        assert cloud.getchannel('A').crop((512,0,2048,810)).getextrema()==(0,0)
    for source,target in [
        ('06_battle_entry_loading_2560x1080.png','qdao_battle_entry_loading_2560x1080_v2.png'),
        ('06_battle_entry_clouds_fg_2560x1080.png','qdao_battle_entry_clouds_fg_2560x1080_v2.png'),
        ('05_battle_scene_2560x1080.png','qdao_battle_arena_forest_bridge_2560x1080_v1.png')]:
        shutil.copyfile(ROOT/source,REPO/target)
    shutil.copyfile(REPO/'qdao_chibi_game_pack_v4/main-city_2560x1080.png',REPO/'q_daoist_scene_bg_2560x1080.png')
    records={
        'schema':'qdao.transition.v1','purpose':'battle entry / loading artwork; not battle arena or engine implementation',
        'cloud_source':metadata(src),'cloud_export':metadata(dst),
        'cloud_processing':'generated true RGBA preserved; proportional centered LANCZOS cover; no color-key removal needed; alpha<=1 quantization speckles cleared',
        'dim_overlay':metadata(REPO/'qdao_battle_dim_overlay_2560x1080_v1.png'),
        'dim_code_equivalent':{'color_rgb':[0,0,0],'alpha_8bit':178,'opacity':178/255,'blend':'straight alpha source-over'},
        'replacement_map':[
            {'old':'../qdao_battle_entry_loading_2560x1080_v2.png','new':'06_battle_entry_loading_2560x1080.png','policy':'same-size compatibility copy'},
            {'old':'../qdao_battle_entry_clouds_fg_2560x1080_v2.png','new':dst.name,'policy':'replace old hero-bearing overlay with pure clouds'},
            {'old':'../qdao_battle_dim_overlay_2560x1080_v1.png','new':'../qdao_battle_dim_overlay_2560x1080_v1.png','policy':'reuse exact uniform RGBA black mask'}],
        'suggested_composition':['entry artwork','optional animated pure cloud foreground','optional dim mask','client-owned dynamic text'],
        'no_baked_loading_text':True,'runtime_timing_or_progress_not_implemented':True,
        'qa':{'central_cloud_alpha_is_zero':True,'cloud_contains_no_legacy_hero':True,'entry_nine_tail_tips_visually_counted':9,'original_accepted_v5_screens_preserved':True}}
    (ROOT/'transition_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for stem,cache_name,refs in [
        ('06_battle_entry_loading','exec-1df826be-3196-40fe-9cbd-4761d4a0ec4a.png',['../../qdao_chibi_game_pack_v4/hero-transparent_1024.png','../pet/ling_yue_nine_tailed_fox.png','../01_login_2560x1080.png','../05_battle_scene_2560x1080.png']),
        ('06_battle_entry_clouds_fg','exec-516d0ab5-d41d-4f13-a38b-936bcaf25152.png',[])]:
        info=metadata(ROOT/'source'/f'{stem}.png')
        record={'generator':'built-in image_gen','generated_file':cache_name,'prompt':f'{stem}.prompt.txt',
                'native_size':info['size'],'mode':info['mode'],'sha256':info['sha256'],
                'requested_canvas':list(SIZE),'native_2560x1080_generation':False,'references':refs,
                'reference_delivery':'in-memory resized reference board via conversation image' if refs else 'text prompt, no attached reference',
                'local_path_attachment_failed':'Windows sandbox apply deny-read ACLs' if refs else None}
        (ROOT/'source'/f'{stem}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return records

def check_transition():
    records=json.loads((ROOT/'transition_manifest.json').read_text(encoding='utf8'))
    for key in ('cloud_source','cloud_export','dim_overlay'):
        assert metadata(ROOT/records[key]['path'])==records[key],key
    for row in records['replacement_map']:
        assert metadata(ROOT/row['old'])['sha256']==metadata(ROOT/row['new'])['sha256']
    return records

if __name__=='__main__':
    export_transition(); check_transition(); print('Transition/cloud/dim compatibility exports verified')
