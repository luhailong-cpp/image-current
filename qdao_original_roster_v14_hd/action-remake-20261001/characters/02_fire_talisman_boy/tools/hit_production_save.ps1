param([Parameter(Mandatory=$true)][string]$RecordPath)
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/02_fire_talisman_boy'
$record = Get-Content -Raw -LiteralPath $RecordPath | ConvertFrom-Json -AsHashtable
$source = $record.evidence.sourcePath
$nativePath = Join-Path $taskRoot $record.file
$exportPath = Join-Path $taskRoot $record.export.file
foreach ($path in @($RecordPath,$nativePath,$exportPath)) { if (-not [IO.Path]::GetFullPath($path).StartsWith([IO.Path]::GetFullPath($taskRoot),[StringComparison]::OrdinalIgnoreCase)) { throw 'Output escaped role directory' } }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $nativePath),(Split-Path -Parent $exportPath) | Out-Null
if (Test-Path -LiteralPath $nativePath) {
    $existingNativeSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $nativePath).Hash
    $actualHostSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash
    if ($existingNativeSha -ne $actualHostSha) { throw 'Native filename collision: existing PNG differs from actual host output. Use a unique generation attempt; never reuse cached native.' }
} else { Copy-Item -LiteralPath $source -Destination $nativePath }
Add-Type -AssemblyName System.Drawing
$native = [System.Drawing.Bitmap]::new($nativePath)
if ($native.Width -lt 1024 -or $native.Height -lt 1024) { $native.Dispose(); throw 'Native frame below 1024' }
$record.nativeDimensions = @{width=$native.Width;height=$native.Height;format='PNG';mode='RGBA'}
$record.native_size = @($native.Width,$native.Height)
$record.sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $nativePath).Hash.ToLowerInvariant()
$record.nativeAlphaAtTopLeft = $native.GetPixel(0,0).A
$output = [System.Drawing.Bitmap]::new(1024,1024,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($output)
$g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
$g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.Clear([System.Drawing.Color]::Transparent)
$g.DrawImage($native,[System.Drawing.Rectangle]::new(0,0,1024,1024),0,0,$native.Width,$native.Height,[System.Drawing.GraphicsUnit]::Pixel)
$output.Save($exportPath,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $output.Dispose(); $native.Dispose()
$record.export.sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $exportPath).Hash.ToLowerInvariant()
$record.export.width = 1024
$record.export.height = 1024
$record.export.operation = 'uniform full-canvas downsample; no bbox scaling; no per-frame ground translation; original canvas preserved'
$record.export.derivedFrom = @{file=$record.file;sha256=$record.sha256;record=($RecordPath.Replace('\','/').Substring($taskRoot.Length+1))}
$zone = [TimeZoneInfo]::FindSystemTimeZoneById('Eastern Standard Time')
$record.generatedAt = [TimeZoneInfo]::ConvertTime([DateTimeOffset]::UtcNow,$zone).ToString('o')
$record | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $RecordPath -Encoding utf8
$inventoryPath = Join-Path $taskRoot 'inventory-hit.json'
$inventory = if(Test-Path -LiteralPath $inventoryPath){Get-Content -Raw -LiteralPath $inventoryPath | ConvertFrom-Json -AsHashtable}else{@{root_anchor=@(512,920);owner='hit_key';frames=@()}}
$entry = @{action=$record.action;direction=$record.direction;frame=$record.frame;path=$record.export.file;native_size=$record.native_size;native_path=$record.file;native_sha256=$record.sha256;native_evidence=$record.export.derivedFrom.record;source_record=$record.export.derivedFrom.record;sha256=$record.export.sha256;visual_status=$record.visual_status}
$inventory.frames = @($inventory.frames | Where-Object { -not($_.action -eq $entry.action -and $_.direction -eq $entry.direction -and $_.frame -eq $entry.frame) }) + @($entry)
$inventory | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $inventoryPath -Encoding utf8
$entry | ConvertTo-Json -Depth 10
