-- Base de datos 'domicilios' - Taller guiado Semana 07 (MCP)
-- Sirve igual para Docker local (puerto 55432) o para Neon / Supabase:
-- en la nube basta con pegarlo en el SQL Editor y ejecutarlo.

CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(id),
    monto NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(30) NOT NULL,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO clientes (nombre, email, ciudad) VALUES
('Carlos Mendoza', 'carlos.mendoza@email.com', 'Bogotá'),
('Ana Gómez', 'ana.gomez@email.com', 'Medellín'),
('Luisa Fernanda', 'luisa.fernanda@email.com', 'Cali'),
('Roberto Silva', 'roberto.silva@email.com', 'Bogotá')
ON CONFLICT (email) DO NOTHING;

-- Solo siembra pedidos si la tabla esta vacia, para poder re-ejecutar el script
INSERT INTO pedidos (cliente_id, monto, estado)
SELECT * FROM (VALUES
    (1, 45000.00, 'ENTREGADO'),
    (1, 120000.00, 'ENTREGADO'),
    (2, 35000.00, 'EN_CAMINO'),
    (3, 89000.00, 'ENTREGADO'),
    (4, 150000.00, 'CANCELADO'),
    (2, 67000.00, 'ENTREGADO')
) AS v(cliente_id, monto, estado)
WHERE NOT EXISTS (SELECT 1 FROM pedidos);

-- Verificacion: 4 clientes y 6 pedidos
SELECT 'clientes' AS tabla, COUNT(*) FROM clientes
UNION ALL
SELECT 'pedidos', COUNT(*) FROM pedidos;
