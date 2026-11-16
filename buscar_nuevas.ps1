# buscar_nuevas.ps1
# El solucionador esta encendido si:
#   - estado.txt dice ON (o ACTIVO), escrito a mano o con el acceso directo, o
#   - la hora actual esta dentro de un intervalo de horario.txt (fuerza encendido).
# Si esta encendido, muestra las fotos nuevas (sin procesar)
# entre las 4 ultimas fotos del celular, de la carpeta fotos y de OneDrive.

$carpetaBase = "C:\Users\argus\Desktop\Claudio\solucionador"
$estado = (Get-Content "$carpetaBase\estado.txt" -ErrorAction SilentlyContinue | Select-Object -First 1)
if ($estado) { $estado = $estado.Trim().ToUpper() }

function Test-DentroDeHorario {
    param([string]$rutaHorario)
    $nombresDias = @('domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado')
    $ahora = Get-Date
    $diaHoy = $nombresDias[[int]$ahora.DayOfWeek]
    $minutosAhora = $ahora.Hour * 60 + $ahora.Minute
    $lineas = Get-Content $rutaHorario -ErrorAction SilentlyContinue
    foreach ($linea in $lineas) {
        $texto = $linea.Trim().ToLower()
        if ($texto -eq '' -or $texto.StartsWith('#')) { continue }
        if ($texto -match '^(\S+)\s+(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$') {
            if ($matches[1] -ne $diaHoy) { continue }
            $minutosInicio = [int]$matches[2] * 60 + [int]$matches[3]
            $minutosFin = [int]$matches[4] * 60 + [int]$matches[5]
            if ($minutosAhora -ge $minutosInicio -and $minutosAhora -lt $minutosFin) { return $true }
        }
    }
    return $false
}

$encendido = ($estado -eq "ON") -or ($estado -eq "ACTIVO")
if (-not $encendido) { $encendido = Test-DentroDeHorario "$carpetaBase\horario.txt" }
if (-not $encendido) { "DESACTIVADO"; exit }

$procesadas = Get-Content "$carpetaBase\procesadas.txt" -ErrorAction SilentlyContinue
$extensiones = '.jpg', '.jpeg', '.png', '.heic', '.webp'
$carpetas = @(
    "C:\Users\argus\CrossDevice\POCO X6 Pro 5G\storage\DCIM\Camera",
    "$carpetaBase\fotos",
    "C:\Users\argus\OneDrive\Pictures\Camera Roll"
)
foreach ($carpeta in $carpetas) {
    Get-ChildItem $carpeta -File -ErrorAction SilentlyContinue |
        Where-Object { $extensiones -contains $_.Extension.ToLower() } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 4 |
        Where-Object { $procesadas -notcontains $_.Name } |
        ForEach-Object { $_.FullName }
}
