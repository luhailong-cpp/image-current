from pathlib import Path
R=Path(__file__).resolve().parents[1]
(R/'timing-grounding.html').write_text((R/'tools/timing_template.html').read_text(encoding='utf-8'),encoding='utf-8')
