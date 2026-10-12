$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl').Path
$chosen = (Get-Content -LiteralPath (Join-Path $taskRoot 'run-selection.json') -Raw | ConvertFrom-Json).frames
$rejects = @('generation/run/E/09-v2.png','generation/run/E/11-v1.png','generation/run/E/11-v2.png','generation/run/E/03-v2.png','generation/run/E/05-v2.png','generation/run/E/10-v4.png','generation/run/E/12-v2.png')
$validated = @()
foreach ($rel in $rejects) {
  $full = [IO.Path]::GetFullPath((Join-Path $taskRoot $rel))
  if (-not $full.StartsWith($taskRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Deletion path outside role root' }
  if ($chosen.source -contains $rel) { throw "Selected source cannot be deleted: $rel" }
  if (-not (Test-Path -LiteralPath $full)) { continue }
  $recordPath = $full + '.generation.json'
  $record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
  $hash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($record.sha256 -ne $hash) { throw "Source hash mismatch: $rel" }
  $validated += [pscustomobject]@{path=$rel;sha256=$hash;record=$recordPath;full=$full;removed=$false}
}
$reportPath = Join-Path $taskRoot 'provenance/run-rejected-cleanup.json'
$report = [pscustomobject]@{status='validated_before_deletion';reason='Rejected PNGs superseded by current selected native candidates; original prompt, returned metadata, SHA and review text retained';items=$validated}
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding utf8
foreach ($item in $validated) {
  $record = Get-Content -LiteralPath $item.record -Raw | ConvertFrom-Json
  $record | Add-Member -NotePropertyName fileRetention -NotePropertyValue ([pscustomobject]@{status='rejected_png_removed';reason='No longer current candidate; text provenance retained';cleanupRecord='provenance/run-rejected-cleanup.json'}) -Force
  $record | ConvertTo-Json -Depth 60 | Set-Content -LiteralPath $item.record -Encoding utf8
  Remove-Item -LiteralPath $item.full
  $item.removed = $true
}
$report.status='completed'
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding utf8
[pscustomobject]@{removed=$validated.Count;scope=$taskRoot} | ConvertTo-Json

