# Script de configuración y despliegue de PostgreSQL en Docker para Windows (PowerShell)
# Taller MCP (Semana 07)

# === 1. Verificando estado de Docker ===
Write-Host "=== 1. Verificando estado de Docker ==="
$null = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker no se encuentra en ejecución. Inicie Docker Desktop o la plataforma Docker y vuelva a intentarlo." -ForegroundColor Red
    exit 1
}
Write-Host "Docker está en ejecución correctamente." -ForegroundColor Green

# Variables de configuración del contenedor y base de datos
$CONTAINER_NAME = "postgres-mcp"
$DB_USER = "curso"
$DB_PASSWORD = "curso"
$DB_NAME = "domicilios"
$PORT = "55432"

# === 2. Iniciando/reiniciando contenedor Docker ===
Write-Host "=== 2. Iniciando/reiniciando contenedor Docker ($CONTAINER_NAME) ==="
$existingContainer = docker ps -aq -f "name=^/${CONTAINER_NAME}$"
if ($existingContainer) {
    Write-Host "Removiendo contenedor previo '$CONTAINER_NAME'..."
    $null = docker rm -f $CONTAINER_NAME 2>&1
}

$null = docker run -d `
  --name $CONTAINER_NAME `
  -p "${PORT}:5432" `
  -e POSTGRES_USER=$DB_USER `
  -e POSTGRES_PASSWORD=$DB_PASSWORD `
  -e POSTGRES_DB=$DB_NAME `
  postgres:16-alpine

Write-Host "Contenedor '$CONTAINER_NAME' creado e iniciado en el puerto $PORT."

# === 3. Esperando a que PostgreSQL esté listo ===
Write-Host "=== 3. Esperando a que PostgreSQL esté listo ==="
do {
    $null = docker exec $CONTAINER_NAME pg_isready -U $DB_USER -d $DB_NAME 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Esperando conexión con PostgreSQL..."
        Start-Sleep -Seconds 1
    }
} while ($LASTEXITCODE -ne 0)

Write-Host "PostgreSQL responde adecuadamente." -ForegroundColor Green

# === 4. Ejecutando init_db.sql ===
Write-Host "=== 4. Ejecutando init_db.sql en la base de datos '$DB_NAME' ==="
$scriptDir = $PSScriptRoot
$sqlPath = Join-Path -Path $scriptDir -ChildPath "init_db.sql"

if (-not (Test-Path $sqlPath)) {
    Write-Host "ERROR: No se encontró el archivo init_db.sql en '$sqlPath'." -ForegroundColor Red
    exit 1
}

Get-Content -Raw -Encoding UTF8 $sqlPath | docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME > $null

# === 5. Resumen de registros creados ===
Write-Host "=== 5. Resumen de registros creados ==="
$query = "SELECT 'clientes' AS tabla, COUNT(*) AS total_registros FROM clientes UNION ALL SELECT 'pedidos' AS tabla, COUNT(*) AS total_registros FROM pedidos;"
docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c $query

Write-Host "Configuración finalizada con éxito." -ForegroundColor Green
