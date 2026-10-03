-- Script de inicialización de la base de datos 'domicilios'
-- Taller MCP - Semana 07

-- Limpieza de tablas previas si existen
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

-- Creación de la tabla de clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    ciudad VARCHAR(50) NOT NULL,
    barrio VARCHAR(50) NOT NULL,
    antiguedad_meses INT NOT NULL DEFAULT 0 CHECK (antiguedad_meses >= 0),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creación de la tabla de pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    monto_total DECIMAL(10,2) NOT NULL CHECK (monto_total >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_camino', 'entregado', 'cancelado')),
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos de prueba iniciales para clientes
INSERT INTO clientes (nombre, email, telefono, ciudad, barrio, antiguedad_meses) VALUES
('Carlos Mendoza', 'carlos.mendoza@email.com', '3001234567', 'Medellín', 'El Poblado', 14),
('Ana María Gómez', 'ana.gomez@email.com', '3109876543', 'Medellín', 'Laureles', 8),
('Juan Pablo Ríos', 'juan.rios@email.com', '3204567890', 'Bogotá', 'Chapinero', 24),
('Laura Restrepo', 'laura.restrepo@email.com', '3016549870', 'Medellín', 'Bello', 2),
('Sofía Torres', 'sofia.torres@email.com', '3153216549', 'Cali', 'Granada', 18);

-- Datos de prueba iniciales para pedidos
INSERT INTO pedidos (cliente_id, monto_total, estado) VALUES
(1, 150000.00, 'entregado'),
(1, 45000.50, 'entregado'),
(2, 89900.00, 'en_camino'),
(3, 230000.00, 'entregado'),
(3, 12000.00, 'cancelado'),
(4, 35000.00, 'pendiente'),
(5, 185000.00, 'entregado');
