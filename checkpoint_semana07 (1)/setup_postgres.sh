#!/usr/bin/env bash
set -e

# Script de configuración y despliegue de PostgreSQL en Docker para el Taller MCP (Semana 07)

echo "=== 1. Verificando estado de Docker ==="
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker no se encuentra en ejecución. Inicie Docker Desktop o la plataforma Docker y vuelva a intentarlo."
    exit 1
fi
echo "Docker está en ejecución correctamente."

CONTAINER_NAME="postgres-mcp"
DB_USER="curso"
DB_PASSWORD="curso"
DB_NAME="domicilios"
PORT="55432"

echo "=== 2. Iniciando/reiniciando contenedor Docker ($CONTAINER_NAME) ==="
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Removiendo contenedor previo '$CONTAINER_NAME'..."
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1
fi

docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT":5432 \
  -e POSTGRES_USER="$DB_USER" \
  -e POSTGRES_PASSWORD="$DB_PASSWORD" \
  -e POSTGRES_DB="$DB_NAME" \
  postgres:16-alpine > /dev/null

echo "Contenedor '$CONTAINER_NAME' creado e iniciado en el puerto $PORT."

echo "=== 3. Esperando a que PostgreSQL esté listo ==="
until docker exec "$CONTAINER_NAME" pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
    echo "Esperando conexión con PostgreSQL..."
    sleep 1
done
echo "PostgreSQL responde adecuadamente."

echo "=== 4. Ejecutando init_db.sql en la base de datos '$DB_NAME' ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$SCRIPT_DIR/init_db.sql" > /dev/null

echo "=== 5. Resumen de registros creados ==="
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 'clientes' AS tabla, COUNT(*) AS total_registros FROM clientes
UNION ALL
SELECT 'pedidos' AS tabla, COUNT(*) AS total_registros FROM pedidos;
"

echo "Configuración finalizada con éxito."
