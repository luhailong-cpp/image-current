from pathlib import Path
Z=Path(__file__).resolve().parent.parent
source=(Z/'qa/r10c03-production-v1.py').read_text(encoding='utf-8-sig')
source=source.replace("tile='r10_c03'","tile='r11_c03'")
old="[(Q/'block2x2-r09r10c04c05-v1-r10_c04-context-native.png',[12173,36749,16499,41075],'latest accepted east neighbor block2x2 native geometry and material anchor'),(Q/'pair-r09c03-c04-v1-r09_c03-context-native.png',[8077,32653,12403,36979],'latest accepted north neighbor after east join; highest-priority corner anchor')]"
new="[(Q/'block2x2-r09r10c03c04-v1-r10_c03-context-native.png',[8077,36749,12403,41075],'latest native north neighbor after 2x2 QA; highest-priority north continuity anchor')]"
assert old in source
source=source.replace(old,new)
p=Z/'qa/r11c03-production-v1.py'
assert not p.exists()
p.write_text(source,encoding='utf-8')
print(str(p))
