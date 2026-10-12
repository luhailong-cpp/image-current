from pathlib import Path
B=Path(__file__).resolve().parent
src=B/'work-r04_c02/assemble_base.py'
out=B/'work-r05_c02/assemble_base.py'
s=src.read_text(encoding='utf-8')
start=s.index('# Whole-post ownership')
end=s.index('def sample(',start)
s=s[:start]+s[end:]
s=s.replace("O=W/'base-v1';O.mkdir(exist_ok=True)","O=W/(sys.argv[1] if len(sys.argv)>1 else 'base-v1');O.mkdir(exist_ok=True)")
s=s.replace("origin=[3981,12173]","origin=[3981,16269]")
s=s.replace("idx['r03_c02']","idx['r04_c02']").replace("idx['r04_c03']","idx['r05_c03']")
s=s.replace('[3981,12173,8307,12403]','[3981,16269,8307,16499]').replace('[8077,12173,8307,16499]','[8077,16269,8307,20595]').replace('[3981,12173,8307,16499]','[3981,16269,8307,20595]').replace('[4096,12288,8192,16384]','[4096,16384,8192,20480]').replace("'r04_c02.candidate'","'r05_c02.candidate'").replace("'r04_c02.candidate.png'","'r05_c02.candidate.png'").replace(",'wholePostOwnership':post","")
assert 'wholePost' not in s and "idx['r04_c02']" in s and "idx['r05_c03']" in s
assert not out.exists()
out.write_text(s,encoding='utf-8')
compile(s,str(out),'exec')
print(str(out))
