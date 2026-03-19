-- Crear base de datos
CREATE DATABASE login_app;

-- Usar la base de datos
USE login_app;

-- Crear tabla de usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY, -- ID único
    username VARCHAR(50),              -- usuario
    password VARCHAR(50)               -- contraseña (vulnerable: texto plano)
);

-- Insertar usuario admin
INSERT INTO users (username, password) VALUES ('admin', '1234');

-- Otro usuario
INSERT INTO users (username, password) VALUES ('orami', 'hackme');

-- Tabla oculta de flags (el jugador debe descubrirla con SQLi)
CREATE TABLE secret_flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),   -- nombre de la flag
    flag VARCHAR(100)      -- valor de la flag
);

-- Flags del CTF
INSERT INTO secret_flags (nombre, flag) VALUES ('flag_1', 'FLAG{union_select_master}');
INSERT INTO secret_flags (nombre, flag) VALUES ('flag_2', 'FLAG{information_schema_pro}');
INSERT INTO secret_flags (nombre, flag) VALUES ('flag_3', 'FLAG{blind_sqli_hunter}');
INSERT INTO secret_flags (nombre, flag) VALUES ('flag_4', 'FLAG{database_enum_complete}');