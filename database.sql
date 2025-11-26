-- ============================================
-- Script SQL para EcoTech Solutions
-- Base de Datos: pepe123
-- Asignatura: Programación Orientada a Objeto Seguro
-- ============================================

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS pepe123;

-- Seleccionar la base de datos
USE pepe123;

-- Eliminar tabla si existe (para desarrollo)
DROP TABLE IF EXISTS usuarios;

-- Crear tabla usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Longitud suficiente para hash bcrypt
    correo VARCHAR(100) NOT NULL UNIQUE,
    rol VARCHAR(20) NOT NULL DEFAULT 'usuario',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuario administrador inicial
-- CONTRASEÑA ORIGINAL: admin123
-- Hash generado con bcrypt (factor de costo 12)
INSERT INTO usuarios (nombre_usuario, password, correo, rol) VALUES
(
    'admin',
    '$2b$12$96a8CGK7RivIM6IkB8i78.YaTr3NCQ96M3PzxP7x.I2cO.pkpEsWO',
    'admin@ecotech.com',
    'administrador'
);

-- Verificar inserción
SELECT * FROM usuarios;

-- ============================================
-- NOTAS IMPORTANTES:
-- ============================================
-- 1. La contraseña del usuario admin es: admin123
-- 2. El hash almacenado fue generado con bcrypt
-- 3. Para generar nuevos hashes, ejecuta el script: generar_hash.py
-- 4. Asegúrate de tener MySQL corriendo antes de ejecutar este script
-- 5. Comando para ejecutar: mysql -u root -p < database.sql
-- ============================================
