$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$batchPath = Join-Path $taskRoot 'provenance/contact-pairs-20261004'
$plan = Get-Content -LiteralPath (Join-Path $batchPath 'cleanup-plan.json') -Raw | ConvertFrom-Json
if ($plan.status -ne 'ready_after_technical_verification') { throw 'Cleanup plan is not ready.' }
$manifestPath = Join-Path $taskRoot 'manifest.json'
if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.manifestSha256) {
    throw 'Manifest changed after cleanup plan was prepared.'
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.frames.Count -ne 196 -or $manifest.contactPairsRevision.status -ne 'exported_and_offline_reviewed') {
    throw 'Final delivery is incomplete.'
}
foreach ($frame in $manifest.frames) {
    $runtimePath = (Resolve-Path -LiteralPath (Join-Path $taskRoot $frame.file)).Path
    if (-not $runtimePath.StartsWith((Join-Path $taskRoot 'runtime') + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Unexpected runtime path: $runtimePath"
    }
    if ((Get-FileHash -LiteralPath $runtimePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frame.sha256) {
        throw "Runtime hash mismatch: $runtimePath"
    }
    $sourceRecord = Join-Path $taskRoot $frame.derivedFrom.generationRecord
    if ((Get-FileHash -LiteralPath $sourceRecord -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frame.derivedFrom.generationRecordSha256) {
        throw "Missing or changed source text record: $sourceRecord"
    }
}
$allowedRoots = @(
    'generation/contact4-20261004', 'generation/contact-pairs-20261004',
    'provenance/contact4-20261004', 'provenance/contact-pairs-20261004'
) | ForEach-Object { (Resolve-Path -LiteralPath (Join-Path $taskRoot $_)).Path + '\' }
$resolvedTargets = foreach ($entry in $plan.items) {
    $candidatePath = (Resolve-Path -LiteralPath (Join-Path $taskRoot $entry.file)).Path
    $insideAllowed = $false
    foreach ($allowedRoot in $allowedRoots) {
        if ($candidatePath.StartsWith($allowedRoot, [StringComparison]::OrdinalIgnoreCase)) { $insideAllowed = $true }
    }
    if (-not $insideAllowed -or [IO.Path]::GetExtension($candidatePath).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.gif')) { throw "Unsafe cleanup target: $candidatePath" }
    $item = Get-Item -LiteralPath $candidatePath
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing link target: $candidatePath" }
    if ((Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Changed candidate: $candidatePath" }
    $candidatePath
}
if ($resolvedTargets.Count -ne $plan.count) { throw 'Cleanup count mismatch.' }
foreach ($candidatePath in $resolvedTargets) { Remove-Item -LiteralPath $candidatePath }
$result = [ordered]@{
    completedAt = [DateTime]::UtcNow.ToString('o')
    status = 'completed'
    removedImageCount = $resolvedTargets.Count
    removedBytes = $plan.bytes
    retainedRuntimePNGCount = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'runtime') -Filter '*.png' -File -Recurse).Count
    retainedPreviewPNGCount = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'preview') -Filter '*.png' -File).Count
    textRecordsPreserved = $true
    removed = $plan.items
}
$result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $batchPath 'cleanup-result.json') -Encoding utf8
[pscustomobject]$result | Select-Object status,removedImageCount,removedBytes,retainedRuntimePNGCount,retainedPreviewPNGCount | ConvertTo-Json
