# Remove drive letters from all SD card partitions so Windows releases the disk
Get-Partition -DiskNumber 1 | ForEach-Object {
    $_ | Remove-PartitionAccessPath -AccessPath ($_.AccessPaths | Where-Object { $_ -match '^[A-Z]:\\$' }) -ErrorAction SilentlyContinue
}

Set-Disk -Number 1 -IsOffline $true

$src = [System.IO.File]::OpenRead("C:\dev\Green\linuxVM\yoctoWslWindows\images\jetson-nano\core-image-minimal.sdcard")
$dst = [System.IO.File]::Open("\\.\PhysicalDrive1", [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)

if ($dst -eq $null) { Write-Error "Could not open PhysicalDrive1 - check admin rights"; $src.Close(); exit 1 }

$buf = New-Object byte[] 4194304
$written = 0
while (($read = $src.Read($buf, 0, $buf.Length)) -gt 0) {
    $dst.Write($buf, 0, $read)
    $written += $read
    Write-Host -NoNewline "`rWritten: $([math]::Round($written/1GB,2)) GB   "
}

$dst.Flush()
$dst.Close()
$src.Close()
Set-Disk -Number 1 -IsOffline $false
Write-Host "`nDone - SD card ready"
