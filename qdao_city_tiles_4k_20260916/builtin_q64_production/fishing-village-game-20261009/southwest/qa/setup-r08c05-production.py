import sys
sys.dont_write_bytecode=True
from pathlib import Path
Z=Path(__file__).resolve().parents[1]
src=(Z/'qa/r08c06-production.py').read_text(encoding='utf-8')
src=src.replace('r08_c06 native-only','r08_c05 native-only').replace("TILE='r08_c06'","TILE='r08_c05'")
old=" candidates=[{'file':(Z/'qa/pair-r09c06-c07-final-v5-r09_c06-context-native.png').as_posix(),'sha256':'c598286f95bb347fd52cc8288b81c9cd0357d3c9998fc364469715b0a8aead94','box':[20365,32653,24691,36979],'trace':(Z/'qa/pair-r09c06-c07-final-v5-trace.json').as_posix()}]"
new=" candidates=[{'file':(Z/'qa/r08c06-south-final-v7-r08_c06-context-native.png').as_posix(),'sha256':'98467349f519f6f494da047fffaca204c5da9ca85262d956ac16351b0984e7c6','box':[20365,28557,24691,32883],'trace':(Z/'qa/r08c06-south-final-v7-trace.json').as_posix()},{'file':(Z/'qa/pair-r09c05-c06-northupdate-v1-r09_c05-context-native.png').as_posix(),'sha256':'7baf8545917ec8a89fb22c5101cd7feb67120fd7485cd0412ce2af8aaed255a8','box':[16269,32653,20595,36979],'trace':(Z/'qa/pair-r09c05-c06-northupdate-v1-trace.json').as_posix()}]"
assert old in src;src=src.replace(old,new)
p=Z/'qa/r08c05-production.py';assert not p.exists();p.write_text(src,encoding='utf-8')

