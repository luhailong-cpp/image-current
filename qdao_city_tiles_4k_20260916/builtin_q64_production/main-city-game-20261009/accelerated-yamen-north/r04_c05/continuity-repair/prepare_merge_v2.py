from pathlib import Path
d=Path(__file__).parent
s=(d/'merge_native.py').read_text()
s=s.replace("O=D/'merged-v1'","O=D/'merged-v2'").replace('>26','>45').replace('diff<70','diff<100').replace('2)<70','2)<100')
s=s.replace('# Archive compact local weight maps',(d/'stairs_merge_addition.txt').read_text()+'\n# Archive compact local weight maps')
(d/'merge_native_v2.py').write_text(s)

