# Start Cloudflare Tunnel and capture URL
$logFile = "C:\Users\Administrator\tianyuan\tunnel.log"
$errorFile = "C:\Users\Administrator\tianyuan\tunnel_error.log"

# Start cloudflared in background
$process = Start-Process -FilePath "C:\Users\Administrator\tianyuan\cloudflared.exe" -ArgumentList "tunnel", "--url", "http://localhost:5000" -RedirectStandardOutput $logFile -RedirectStandardError $errorFile -WindowStyle Hidden -PassThru

Write-Host "Cloudflared started with PID: $($process.Id)"
Write-Host "Waiting for tunnel URL..."

Start-Sleep -Seconds 10

# Read log file to find URL
if (Test-Path $logFile) {
    $content = Get-Content $logFile -Raw
    if ($content -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
        $url = $matches[0]
        Write-Host "Tunnel URL: $url"
        
        # Save URL to file
        $url | Out-File "C:\Users\Administrator\tianyuan\tunnel_url.txt" -Encoding UTF8
        Write-Host "URL saved to tunnel_url.txt"
    } else {
        Write-Host "No URL found in log. Content:"
        Write-Host $content
    }
}

if (Test-Path $errorFile) {
    $errorContent = Get-Content $errorFile -Raw
    if ($errorContent -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
        $url = $matches[0]
        Write-Host "Tunnel URL (from error log): $url"
        $url | Out-File "C:\Users\Administrator\tianyuan\tunnel_url.txt" -Encoding UTF8
    }
}
