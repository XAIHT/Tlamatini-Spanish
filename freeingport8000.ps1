$ErrorActionPreference = 'Continue'

# Result log — <install>\Temp when this ships next to Tlamatini.exe (the Temp
# directory policy), else the user's %TEMP%. Never a developer-specific path.
$appTemp = Join-Path $PSScriptRoot 'Temp'
if (Test-Path $appTemp) { $out = Join-Path $appTemp 'portfix_result.txt' }
else { $out = Join-Path $env:TEMP 'Tlamatini_portfix_result.txt' }
if (Test-Path $out) { Remove-Item $out -Force }

# Port to test — config.json's django_port when present (config.json ships next
# to the exe), else Tlamatini's default 8000. Fail-open: anything odd keeps 8000.
$port = 8000
try {
    $cfg = Join-Path $PSScriptRoot 'config.json'
    if (Test-Path $cfg) {
        $v = (Get-Content $cfg -Raw -Encoding UTF8 | ConvertFrom-Json).django_port
        if ($null -ne $v -and [int]$v -ge 1 -and [int]$v -le 65535) { $port = [int]$v }
    }
} catch { $port = 8000 }

function Log($m) { $m | Tee-Object -FilePath $out -Append | Out-Null; Write-Host $m }

Log "=== Tlamatini port-$port fix @ $(Get-Date) ==="
Log "Archivo de log: $out"
Log "Admin: $([bool](([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)))"

Log ""
Log "--- PASO 1: rango de puertos TCP de Windows a su valor original (49152/16384) ---"
Log (netsh int ipv4 set dynamicport tcp start=49152 num=16384 2>&1 | Out-String)
Log "--- PASO 1b: lo mismo para el rango de puertos UDP ---"
Log (netsh int ipv4 set dynamicport udp start=49152 num=16384 2>&1 | Out-String)

Log ""
Log "--- PASO 2: reiniciar WinNAT para que suelte cualquier reserva vieja de puertos bajos ---"
$deps = @()
try { $deps = (Get-Service winnat -ErrorAction Stop).DependentServices | Where-Object { $_.Status -eq 'Running' } | Select-Object -ExpandProperty Name } catch {}
Log ("Dependientes activos que se reinician al final: " + ($deps -join ', '))
Stop-Service winnat -Force -ErrorAction Continue
Start-Sleep -Seconds 1
Start-Service winnat -ErrorAction Continue
foreach ($d in $deps) { try { Start-Service $d -ErrorAction Stop; Log "  dependiente reiniciado: $d" } catch { Log "  no se pudo reiniciar el dependiente ${d}: $_" } }
Log "Status de WinNAT: $((Get-Service winnat).Status)"

Log ""
Log "--- PASO 3: verificar que los rangos excluidos ya no cubren el $port ---"
Log (netsh interface ipv4 show excludedportrange protocol=tcp 2>&1 | Out-String)
Log "--- rango de puertos actual ---"
Log (netsh int ipv4 show dynamicport tcp 2>&1 | Out-String)

Log ""
Log "--- PASO 4: prueba de bind en 127.0.0.1:$port (solo PowerShell, sin python) ---"
try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    $listener.Start()
    $listener.Stop()
    Log "BIND OK - puerto $port LIBRE"
} catch {
    $msg = if ($_.Exception.InnerException) { $_.Exception.InnerException.Message } else { $_.Exception.Message }
    Log ("EL BIND SIGUE FALLANDO -> " + $msg)
    Log "TIP: otra salida es mover Tlamatini a otro puerto - pon 'django_port' en config.json (junto a Tlamatini.exe) y reinicia."
}

Log "=== DONE - you can close this window ==="
Write-Host ""
Write-Host "Resultado guardado. Esta ventana se queda abierta para que la leas." -ForegroundColor Green