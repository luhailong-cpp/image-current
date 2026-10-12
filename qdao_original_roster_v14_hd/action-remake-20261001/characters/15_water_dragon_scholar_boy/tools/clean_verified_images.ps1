$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$expectedRoot = [System.IO.Path]::GetFullPath('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy').TrimEnd('\')
if ($taskRoot -ne $expectedRoot) { throw 'Unexpected character root' }
$plan = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'audit/retention-plan.json') | ConvertFrom-Json
$check = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'audit/final-delivery-check.json') | ConvertFrom-Json
$manifest = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'manifest.json') | ConvertFrom-Json
if (-not $check.summary.technicalPass -or $manifest.animationApproval -ne 'offline_reviewed') { throw 'Final checks are not complete' }
$currentManifestSha = (Get-FileHash -LiteralPath (Join-Path $taskRoot 'manifest.json') -Algorithm SHA256).Hash.ToLower()
if ($currentManifestSha -ne $plan.manifestSha256 -or $currentManifestSha -ne $check.manifestSha256) { throw 'Plan or check is stale' }
$targets = @($plan.images | Where-Object { $_.presentAtPlanTime -and $_.decision -eq 'delete_after_final_verification' })
foreach ($item in $targets) {
    $full = [System.IO.Path]::GetFullPath((Join-Path $taskRoot $item.file))
    if (-not $full.StartsWith($taskRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Path escapes character root' }
    if ($full.StartsWith((Join-Path $taskRoot 'runtime') + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Refusing runtime deletion' }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw ('Planned image is missing: ' + $item.file) }
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
    $record = [PSCustomObject]@{character='15_water_dragon_scholar_boy';executedAt=[DateTime]::UtcNow.ToString('o');scope=$taskRoot;policy='User AGENTS.md 2026-09-23; final runtime and provenance text retained';manifestSha256=$currentManifestSha;deletedCount=$entries.Count;deleted=$entries;sourceRecordsPreserved=$true;gitModifiedByThisScript=$false}
    $json = $record | ConvertTo-Json -Depth 12
    [System.IO.File]::WriteAllText((Join-Path $taskRoot 'audit/retention-executed.json'),$json,[System.Text.UTF8Encoding]::new($false))
}
Write-Output ('Deleted verified intermediate images: ' + $entries.Count)
