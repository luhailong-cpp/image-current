param([ValidatePattern('^retention-executed[-a-z0-9]*\.json$')][string]$RecordName = 'retention-executed-video-axis-20261005.json')
$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$expectedRoot = [System.IO.Path]::GetFullPath('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy').TrimEnd('\')
if ($taskRoot -ne $expectedRoot) { throw 'Unexpected character root' }
$recordPath = Join-Path (Join-Path $taskRoot 'audit') $RecordName
if (Test-Path -LiteralPath $recordPath) { throw 'Batch record already exists; do not overwrite deletion history' }
$priorRecords = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'audit') -File -Filter 'retention-executed*.json' | ForEach-Object { 'audit/' + $_.Name })
$plan = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'audit/retention-plan.json') | ConvertFrom-Json
$check = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'audit/final-delivery-check.json') | ConvertFrom-Json
$manifest = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'manifest.json') | ConvertFrom-Json
if (-not $check.summary.technicalPass) { throw 'Technical check must pass' }
if ($manifest.animationApproval -ne 'pending_final_dynamic_review') { throw 'Unexpected current review status' }
$currentManifestSha = (Get-FileHash -LiteralPath (Join-Path $taskRoot 'manifest.json') -Algorithm SHA256).Hash.ToLower()
if ($currentManifestSha -ne $plan.manifestSha256 -or $currentManifestSha -ne $check.manifestSha256) { throw 'Plan or check is stale' }
$staticPath = [System.IO.Path]::GetFullPath((Join-Path $taskRoot $manifest.staticReview.record))
if (-not $staticPath.StartsWith($taskRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Static review path outside character root' }
if ((Get-FileHash -LiteralPath $staticPath -Algorithm SHA256).Hash.ToLower() -ne $manifest.staticReview.sha256) { throw 'Static review changed' }
$protected = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($frame in $manifest.frames) { [void]$protected.Add($frame.source); [void]$protected.Add($frame.output) }
$targets = @($plan.images | Where-Object { $_.presentAtPlanTime -and $_.decision -eq 'delete_after_final_verification' })
# Validate every exact file before deleting any. No recursive operations.
foreach ($item in $targets) {
    $full = [System.IO.Path]::GetFullPath((Join-Path $taskRoot $item.file))
    if (-not $full.StartsWith($taskRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Path escapes character root' }
    if ($protected.Contains($item.file) -or $full.StartsWith((Join-Path $taskRoot 'runtime') + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw ('Refusing current input/output deletion: ' + $item.file) }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw ('Planned image missing: ' + $item.file) }
    if ((Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLower() -ne $item.sha256) { throw ('Image changed: ' + $item.file) }
}
$entries = [System.Collections.Generic.List[object]]::new()
try {
    foreach ($item in $targets) {
        $full = [System.IO.Path]::GetFullPath((Join-Path $taskRoot $item.file))
        Remove-Item -LiteralPath $full
        $entries.Add([PSCustomObject]@{file=$item.file;sha256=$item.sha256;bytes=$item.bytes;deletedAt=[DateTime]::UtcNow.ToString('o');reason=$item.reason})
    }
} finally {
    $record = [PSCustomObject]@{character='15_water_dragon_scholar_boy';executedAt=[DateTime]::UtcNow.ToString('o');scope=$taskRoot;policy='User AGENTS.md 2026-09-23; current runtime, previews, selected native designs and text provenance retained';manifestSha256=$currentManifestSha;priorExecutionRecords=$priorRecords;deletedCount=$entries.Count;deleted=$entries;sourceRecordsPreserved=$true;dynamicApproval='pending_final_dynamic_review';gitModifiedByThisScript=$false}
    [System.IO.File]::WriteAllText($recordPath,($record | ConvertTo-Json -Depth 12),[System.Text.UTF8Encoding]::new($false))
}
Write-Output ('Deleted superseded images: ' + $entries.Count)
