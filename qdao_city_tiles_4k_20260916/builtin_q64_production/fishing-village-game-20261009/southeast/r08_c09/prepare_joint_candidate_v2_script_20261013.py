from pathlib import Path
T=Path(__file__).resolve().parent
s=(T/'build_joint_candidate_finish_20261013.py').read_text()
s=s.replace("dest=T/'native/p31-ne-joint-v1.png';assert not dest.exists();dest.write_bytes(raw.read_bytes())","dest=T/'native/p31-ne-joint-v1.png';assert sha(dest)==sha(raw)")
s='\n'.join(x for x in s.splitlines() if not x.startswith("write(str(dest)+'.generation.json'"))
s=s.replace("processed/p31-ne-joint-finish-20261013-v1","processed/p31-ne-joint-finish-20261013-v2").replace("joint-selected-finish-20261013-v1.json","joint-selected-finish-20261013-v2.json")
s=s.replace("protect=np.array", "gold[:690]=0;gold[:,370:]=0\nprotect=np.array")
s=s.replace("Warm gold/red pixels plus8px protective dilation of mask only; no art smoothing","Gold finial ROI x0..370,y690..1254 only;8px mask dilation. Stone grout not excluded. No art smoothing.")
p=T/'build_joint_candidate_finish_20261013_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8')

