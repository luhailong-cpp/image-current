from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
p=R/'audit/player-code-review.json';j=json.loads(p.read_text(encoding='utf-8'))
j['status']='fixed_source_and_browser_verified'
j['browserReview']={'reviewedAt':datetime.now(timezone.utc).isoformat(),'main':'196导出/196视觉通过可见；定位E08后1/4速恢复，连续到E09；正常/慢速、分组和尺寸控件可用。','comparison':'切换W后使用W的landing/support_passing相位与45/60ms；四档定位08后按各自时长续播，没有倒跳到旧位置。','spriteReview':'八方向240px正常播放和480px慢放，所有14动作组静态/离线播放器复核。','scope':'browser visual behavior checked; timing exactness verified by controlled source tests, not browser hardware FPS measurement'}
j['finalSourceSHA256']={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['tools/preview_template.html','timing-grounding.html','index.html','all-directions.html','manifest.json']}
j['postAgentChange']='Root changed only comparison status copy from pending to completed offline review after asset approval.'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
