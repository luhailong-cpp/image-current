from pathlib import Path
Q=Path(__file__).resolve().parent
text=(Q/'r09c03-production-v2.py').read_text(encoding='utf-8-sig').replace("tile='r09_c03'","tile='r10_c03'")
start=text.index(" anchor=Q/'r09c03-r09c04-east-anchor-native.png'")
end=text.index("\n out=L/(stem+'_continuity.png')",start)
anchors=""" for anchor,b,role in [(Q/'block2x2-r09r10c04c05-v1-r10_c04-context-native.png',[12173,36749,16499,41075],'latest accepted east neighbor block2x2 native geometry and material anchor'),(Q/'pair-r09c03-c04-v1-r09_c03-context-native.png',[8077,32653,12403,36979],'latest accepted north neighbor after east join; highest-priority corner anchor')]:
  inter=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
  if inter[0]<inter[2] and inter[1]<inter[3]:
   crop=Image.open(anchor).crop((inter[0]-b[0],inter[1]-b[1],inter[2]-b[0],inter[3]-b[1]));dst=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]];canvas.paste(crop,tuple(dst[:2]));sources.append({'path':anchor.as_posix(),'sha256':sha(anchor),'globalOverlapBox':inter,'targetBox':dst,'role':role})"""
text=text[:start]+anchors+text[end:]
out=Q/'r10c03-production-v1.py';assert not out.exists();out.write_text(text,encoding='utf-8')
print(out)

