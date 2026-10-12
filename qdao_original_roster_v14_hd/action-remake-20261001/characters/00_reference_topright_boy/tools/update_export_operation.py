from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools/export_selected.py'
s=p.read_text(encoding='utf-8')
s=s.replace("'scaledCanvas':[901,901]", "'scaledCanvas':list(scaled),'calibrationFile':'export-settings.json','calibrationStatus':transforms['status'],'nativeRoot':transform['nativeRoot']")
p.write_text(s,encoding='utf-8')

