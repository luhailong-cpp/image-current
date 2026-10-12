$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$batchPath = Join-Path $taskRoot 'provenance/axis-20261004'
$plan = Get-Content -LiteralPath (Join-Path $batchPath 'cleanup-plan.json') -Raw | ConvertFrom-Json
$manifestPath = Join-Path $taskRoot 'manifest.json'
if ($plan.status -ne 'ready_after_technical_verification') { throw 'Cleanup plan is not ready' }
if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.manifestSha256) { throw 'Manifest changed' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.frames.Count -ne 196 -or $manifest.axisRevision.status -ne 'exported_and_offline_reviewed') { throw 'Final review incomplete' }
foreach ($frame in $manifest.frames) {
    $runtimePath = (Resolve-Path -LiteralPath (Join-Path $taskRoot $frame.file)).Path
    if (-not $runtimePath.StartsWith((Join-Path $taskRoot 'runtime') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected runtime path' }
    if ((Get-FileHash -LiteralPath $runtimePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frame.sha256) { throw "Changed runtime: $runtimePath" }
    $recordPath = Join-Path $taskRoot $frame.derivedFrom.generationRecord
    if ((Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frame.derivedFrom.generationRecordSha256) { throw "Changed source record: $recordPath" }
}
$allowedRoots = @('generation/axis-20261004','provenance/axis-20261004') | ForEach-Object { (Resolve-Path -LiteralPath (Join-Path $taskRoot $_)).Path + '\' }
$targets = foreach ($entry in $plan.items) {
    $resolved = (Resolve-Path -LiteralPath (Join-Path $taskRoot $entry.file)).Path
    $allowed = $false
    foreach ($prefix in $allowedRoots) { if ($resolved.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { $allowed = $true } }
    if (-not $allowed -or [IO.Path]::GetExtension($resolved).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.gif')) { throw "Unsafe cleanup target: $resolved" }
    if ((Get-Item -LiteralPath $resolved).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Link target refused: $resolved" }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Changed candidate: $resolved" }
    $resolved
}
if ($targets.Count -ne $plan.count) { throw 'Cleanup count mismatch' }
foreach ($resolved in $targets) { Remove-Item -LiteralPath $resolved }
$result = [ordered]@{
    completedAt = [DateTime]::UtcNow.ToString('o')
    status = 'completed'
    removedImageCount = $targets.Count
    removedBytes = $plan.bytes
    retainedRuntimePNGCount = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'runtime') -Filter '*.png' -File -Recurse).Count
    retainedPreviewPNGCount = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'preview') -Filter '*.png' -File).Count
    textRecordsPreserved = $true
    sourceUserVideoUntouched = $true
    removed = $plan.items
}
$result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $batchPath 'cleanup-result.json') -Encoding utf8
[pscustomobject]$result | Select-Object status,removedImageCount,removedBytes,retainedRuntimePNGCount,retainedPreviewPNGCount | ConvertTo-Json
