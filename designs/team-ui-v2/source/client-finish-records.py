from pathlib import Path
import json
from fontTools.ttLib import TTFont
font=TTFont('C:/Windows/Fonts/Noto Sans SC (TrueType).otf')
ids={0:'copyright',1:'family',2:'style',5:'version',8:'manufacturer',9:'designer',13:'license',14:'license_url'}
record={ids[i]:font['name'].getDebugName(i) for i in ids}
record['source_file']='C:/Windows/Fonts/Noto Sans SC (TrueType).otf'
Path('E:/work/mmorpg-client/Docs/team-ui-font.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in record.items() if k!='license'},ensure_ascii=False))
p=Path('E:/work/mmorpg-client/Assets/Editor/TeamUiVerification.cs')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('_previewSnapshot = CreateSnapshot();','_previewSnapshot = CreateSnapshot();\n            _previewSnapshot.Applications.RemoveRange(2, _previewSnapshot.Applications.Count - 2);')
s=s.replace('var populated = CreateSnapshot();','var few = CreateSnapshot();\n            few.Applications.RemoveRange(2, few.Applications.Count - 2);\n            Display(few, "dual-lists-two-applicants");\n\n            var populated = CreateSnapshot();')
s=s.replace('snapshot.Members.Add(Role(13, "长街听笛", 69, 2, 1));','snapshot.Members.Add(Role(13, "长街听笛", 69, 2, 1));\n        snapshot.Members[2].IsOnline = false;')
p.write_text(s,encoding='utf8')
