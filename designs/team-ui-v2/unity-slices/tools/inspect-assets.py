import hashlib,json,re,struct
from pathlib import Path
from PIL import Image
ROOT=Path('E:/work/image/designs/team-ui-v2/unity-slices')
CLIENT=Path('E:/work/mmorpg-client/Assets/Resources/UI/Ugui/TeamV2')
SOURCE=ROOT.parent/'team-ui-v2.png'
# Source coordinates are the actual inputs in the successful official MCP slicing command.
specs=[
 ('main_frame',[81,51,1034,438],'Nine-part frame reconstructed from original clean paper, edges and corners.'),
 ('title_plate',[378,0,445,90],'Original cloud plaque silhouette; baked title/subtitle replaced with adjacent jade; boundary-connected pale sky removed through official MCP.'),
 ('section_plate',[107,75,269,45],'Original jade section plaque, text cleared with original jade.'),
 ('member_row',[121,386,529,60],'Original empty-member border, clean source paper replaces plus/text.'),
 ('application_card',[687,148,392,123],'Original application card border and source paper, portrait/text removed.'),
 ('button_primary',[914,222,140,41],'Original jade action skin with text removed and silhouette alpha.'),
 ('button_secondary',[771,222,137,41],'Original paper action skin with text removed and silhouette alpha.'),
 ('close',[1084,22,51,51],'Original fixed X button with circular alpha.'),
 ('portrait_frame',[149,326,57,57],'Gold rim from the empty-slot circle; inner pixels removed, transparent ring.'),
 ('empty_slot',[149,326,57,57],'Original fixed plus symbol with circular alpha.'),
 ('badge_leader',[377,143,77,28],'Original gold role badge, source material replaces baked label.'),
 ('badge_self',[459,143,57,27],'Original jade self badge, source material replaces baked label.'),
 ('status_online',[559,145,19,20],'Original fixed online indicator with circular alpha.'),
 ('status_offline',[559,280,19,19],'Original fixed offline indicator with circular alpha.')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
source_image=Image.open(SOURCE)
scale=source_image.width/1200
items=[]
for name,rect,processing in specs:
 p=ROOT/'png'/f'{name}.png'; cp=CLIENT/p.name
 im=Image.open(p).convert('RGBA')
 meta=Path(str(cp)+'.meta').read_text(encoding='utf-8')
 bd=re.search(r'spriteBorder: \{x: ([\d.]+), y: ([\d.]+), z: ([\d.]+), w: ([\d.]+)\}',meta)
 assert bd,name+' border missing'
 assert sha(p)==sha(cp),name+' differs from imported asset'
 assert im.getchannel('A').getextrema()[0]==0,name+' lacks exterior transparency'
 checks={'sprite':bool(re.search(r'textureType: 8\b',meta)),
  'singleSprite':bool(re.search(r'spriteMode: 1\b',meta)),
  'mipmapsDisabled':bool(re.search(r'enableMipMap: 0\b',meta)),
  'alphaTransparency':bool(re.search(r'alphaIsTransparency: 1\b',meta)),
  'nativeDimensions':im.size==(round((rect[0]+rect[2])*scale)-round(rect[0]*scale),round((rect[1]+rect[3])*scale)-round(rect[1]*scale)) if name!='main_frame' else im.size==(round(rect[2]*scale),round(rect[3]*scale))}
 assert all(checks.values()),(name,checks)
 items.append({'name':name,'file':'png/'+p.name,'sourceRectTopLeft1200':rect,
  'sourceRectNativeTopLeft':[round(rect[0]*scale),round(rect[1]*scale),round((rect[0]+rect[2])*scale)-round(rect[0]*scale),round((rect[1]+rect[3])*scale)-round(rect[1]*scale)],
  'width':im.width,'height':im.height,'borderLeftBottomRightTop':list(map(float,bd.groups())),
  'resourcePath':'UI/Ugui/TeamV2/'+name,'guid':re.search(r'^guid: ([a-f0-9]+)',meta,re.M).group(1),
  'sha256':sha(p),'processing':processing,'containsDynamicText':False,
  'containsFixedSymbol':name in ['close','empty_slot'],'checks':checks})
manifest={'tool':'Unity official MCP / Unity_RunCommand','unityVersion':'6000.6.0f1',
 'source':'../team-ui-v2.png','sourceSha256':sha(SOURCE),'sourceWidth':source_image.width,'sourceHeight':source_image.height,
 'coordinateSystem':'1200-wide top-left reference; crop edges mapped to native source pixels.',
 'provenance':'PNG export and Sprite import executed by official Unity MCP. This manifest was completed by a local metadata audit because Unity JsonUtility omitted dynamic class arrays.',
 'artwork':'Existing approved source crops and clean-pixel reconstruction; no image generation. Name, role, counts, levels, schools and actions remain native TMP text.',
 'sprites':items}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sprites':len(items),'sourceSize':source_image.size,'checks':'passed','bytes':sum((ROOT/i['file']).stat().st_size for i in items)},ensure_ascii=False))