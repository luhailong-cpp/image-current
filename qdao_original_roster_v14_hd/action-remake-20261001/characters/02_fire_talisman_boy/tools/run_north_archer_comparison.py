"""Record read-only motion-reference review; never changes the archer or sprites."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
ARCHER=ROOT.parent/'09_bamboo_archer_girl'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(ZoneInfo('America/New_York')).isoformat()
manifest=read(ARCHER/'manifest.json')
originals={'W':[3,4,12],'N':[4,12],'NW':[3,4,9],'NE':[5,6,7,13,14,15]}
rows=[]
for seq in manifest['sequences']:
 if seq['action']!='run' or seq['direction'] not in originals:continue
 for item in seq['frames']:
  path=(ARCHER/item['file']).resolve()
  if not path.is_relative_to(ARCHER.resolve()):raise ValueError('unexpected reference path')
  actual=sha(path)
  rows.append({'direction':seq['direction'],'frame':item['frame'],'path':item['file'],'manifestSha256':item['sha256'],'actualSha256':actual,'matchesManifest':actual==item['sha256'],'originalResolutionViewed':item['frame'] in originals[seq['direction']]})
assert len(rows)==64
assert all(r['matchesManifest'] for r in rows)
notes={
 'W':{'observation':'09 W03承重鞋脚尖朝左、鞋底近平，另一腿屈膝回收；W04/12后蹬鞋趾向下、鞋跟抬，长轴顺W。02当前W16帧脚掌轴未见新增明确外撇。','decision':'保留当前鞋向；02步幅更大，双手持物的摆幅不照搬09长弓持臂。W接地和重心仍由root在共同画布实播。'},
 'N':{'observation':'09 N04右长脚鞋尖顺N纵深，鞋底纵向可见；N12反侧。02当前N的后跟/足底纵向投影相近，露鞋底本身不构成外撇。','decision':'未发现仅凭09对照就需要重画的确定外八槽。保留N鞋向，前掌接地和16→01俯仰连续性待动态。'},
 'NW':{'observation':'09 NW03/04鞋跟向右下、鞋尖向左上，两脚按深度先后；NW09一腿下放另一腿高回收。02此前八槽鞋轴修订已向NW纵深，未见新的明确侧向外转。','decision':'保留当前鞋轴；NW01→02铃臂大幅移动和部分髋遮挡仍列动态待验，不能以鞋轴通过代替腿侧相位通过。'},
 'NE':{'observation':'09 NE部分对应帧的左右腿起始相位与02不同，不能机械按同帧号复制。NE15可见一腿下前过、另一鞋高折的错位关节关系。02旧NE06双膝并蜷被root拒；新attempt06实际附09 NE15生成，现右膝高折、左腿下前过，双鞋高低错开。','decision':'仅将09 NE15作为关节/鞋轴参考，保留02身份和右扇左铃。当前02 NE06左伸距比07未明显缩短，05→06→07仍待root实播，不宣称整段通过。'}
}
doc={'reviewedAt':now,'referenceCharacter':'09_bamboo_archer_girl','authorization':'Root转达最新人类确认09竹弓少女动作正确并要求本角色参照。','referenceAuthority':'manifest.json的正式runtime路径','documentsRead':[{'file':f,'sha256':sha(ARCHER/f)} for f in ['manifest.json','animation-timing.json','MERGE_HANDOFF.md','preview/index.html']],'visualScope':{'contactSheetsViewed':64,'originalResolutionFramesViewed':sum(map(len,originals.values())),'originalResolutionFramesByDirection':originals,'browserPlaybackPerformedByThisAgent':False},'runtimeChecks':rows,'all64MatchManifest':True,'directionComparison':notes,'timing':{'source':'latest explicit user instruction for02','normalCycleMs':1200,'normalFrameMs':75,'uniform':True,'phaseWeightsApplied':False,'note':'09既有文档快档不覆盖用户最新要求；只读09，不改其时长。'},'current02NE06':{'file':'frames/run/NE/06.png','sha256':sha(ROOT/'frames/run/NE/06.png'),'record':'records/run-NE-06-attempt-06.json'},'limits':['其它角色只读，无写入','用户认可参考不等于已在本机客户端验收02','没有为调时长重画所有帧','整段动态由root浏览器实播，客户端未接入']}
dest=ROOT/'work/run-NW/archer-motion-comparison-20261003.json'
write(dest,doc)
print(json.dumps({'referenceRuntimeFrames':len(rows),'manifestMatches':sum(r['matchesManifest'] for r in rows),'originalResolutionViewed':sum(map(len,originals.values())),'record':dest.relative_to(ROOT).as_posix(),'recordSha256':sha(dest)},ensure_ascii=True))
