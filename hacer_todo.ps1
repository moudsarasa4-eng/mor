# Motor de Jackpots — comando integral.
# Busca solo la carpeta del proyecto en esta PC (no hace falta saber donde esta),
# actualiza el codigo, instala dependencias y genera la lista de empresas a contactar.
# Uso: pegar en PowerShell ->  irm <url-raw>/hacer_todo.ps1 | iex      (o correr este archivo)

$ErrorActionPreference = "Continue"

function Buscar-Proyecto {
    # 1) Si ya estamos parados adentro, listo.
    $aqui = Get-Location
    if ((Test-Path (Join-Path $aqui "main.py")) -and (Test-Path (Join-Path $aqui "app\keywords.py"))) {
        return $aqui.Path
    }
    # 2) Lugares probables primero (rapido), despues el disco entero (lento).
    $raices = @(
        $HOME,
        (Join-Path $HOME "Desktop"), (Join-Path $HOME "Escritorio"),
        (Join-Path $HOME "Documents"), (Join-Path $HOME "Documentos"),
        (Join-Path $HOME "Downloads"), (Join-Path $HOME "Descargas"),
        "C:\", "D:\"
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

    foreach ($raiz in $raices) {
        Write-Host "Buscando el proyecto en $raiz ..."
        $hit = Get-ChildItem -Path $raiz -Filter "keywords.py" -Recurse -File -Force -ErrorAction SilentlyContinue |
               Where-Object {
                   $_.Directory.Name -eq "app" -and
                   (Test-Path (Join-Path $_.Directory.Parent.FullName "main.py"))
               } | Select-Object -First 1
        if ($hit) { return $hit.Directory.Parent.FullName }
    }
    return $null
}

$proyecto = Buscar-Proyecto
if (-not $proyecto) {
    Write-Host ""
    Write-Host "No encontre la carpeta del proyecto en esta PC." -ForegroundColor Red
    Write-Host "Si sabes donde esta, abri PowerShell ahi adentro y volve a correr esto."
    Read-Host "Enter para cerrar"
    exit 1
}

Write-Host ""
Write-Host "Proyecto encontrado en: $proyecto" -ForegroundColor Green
Set-Location $proyecto

# Python
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue) }
if (-not $py) {
    Write-Host "Python no esta instalado. Bajalo de https://python.org y marca 'Add to PATH'." -ForegroundColor Red
    Read-Host "Enter para cerrar"
    exit 1
}

# Codigo al dia (si falla, seguimos igual con lo que hay)
if (Test-Path ".git") {
    Write-Host "Actualizando el codigo..."
    git pull 2>&1 | Out-Host
}

# Entorno virtual + dependencias
if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..."
    & $py.Source -m venv .venv
}
$pyv = Join-Path $proyecto ".venv\Scripts\python.exe"
if (-not (Test-Path $pyv)) { $pyv = $py.Source }

Write-Host "Instalando dependencias..."
& $pyv -m pip install -q --upgrade pip
& $pyv -m pip install -q -r requirements.txt

# El trabajo de verdad
Write-Host ""
& $pyv main.py procesar-todo

Write-Host ""
Write-Host "Listo. Los archivos quedaron en tu carpeta Descargas:" -ForegroundColor Green
Write-Host "  empresas_a_contactar_<fecha>.md   <- la lista para contactar (pasale esta a Claude)"
Write-Host "  motor_jackpots_candidatas_<fecha>.txt  <- el detalle completo"
try { Start-Process (Join-Path $HOME "Downloads") } catch {}
Read-Host "Enter para cerrar"
