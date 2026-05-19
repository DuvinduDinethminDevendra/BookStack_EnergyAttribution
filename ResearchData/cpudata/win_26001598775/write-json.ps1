function Write-Utf8JsonNoBom($Path, $Value) {
  $json = $Value | ConvertTo-Json -Compress
  $encoding = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $json, $encoding)
}
