CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO users (username, password)
SELECT 'admin', '1234'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'admin' AND password = '1234'
);

INSERT INTO users (username, password)
SELECT 'orami', 'hackme'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'orami' AND password = 'hackme'
);

CREATE TABLE IF NOT EXISTS secret_flags (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    flag VARCHAR(100)
);

INSERT INTO secret_flags (nombre, flag)
SELECT 'flag_1', 'FLAG{union_select_master}'
WHERE NOT EXISTS (
    SELECT 1 FROM secret_flags WHERE nombre = 'flag_1'
);

INSERT INTO secret_flags (nombre, flag)
SELECT 'flag_2', 'FLAG{information_schema_pro}'
WHERE NOT EXISTS (
    SELECT 1 FROM secret_flags WHERE nombre = 'flag_2'
);

INSERT INTO secret_flags (nombre, flag)
SELECT 'flag_3', 'FLAG{blind_sqli_hunter}'
WHERE NOT EXISTS (
    SELECT 1 FROM secret_flags WHERE nombre = 'flag_3'
);

INSERT INTO secret_flags (nombre, flag)
SELECT 'flag_4', 'FLAG{database_enum_complete}'
WHERE NOT EXISTS (
    SELECT 1 FROM secret_flags WHERE nombre = 'flag_4'
);
