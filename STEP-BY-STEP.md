# STEP-BY-STEP: levantar login_app desde cero

Guía paso a paso para montar el servicio **localmente** con **MySQL/MariaDB**,
sin depender de servicios en la nube (Render, Netlify, etc.).

Al final de esta guía tendrás la app funcionando en
`http://localhost:5000` con su base de datos `login_app`.

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Obtener el proyecto](#2-obtener-el-proyecto)
3. [Crear el entorno virtual (venv)](#3-crear-el-entorno-virtual-venv)
4. [Instalar dependencias](#4-instalar-dependencias)
5. [Levantar la base de datos](#5-levantar-la-base-de-datos)
6. [Crear base de datos y usuario](#6-crear-base-de-datos-y-usuario)
7. [Cargar el esquema del laboratorio](#7-cargar-el-esquema-del-laboratorio)
8. [Arrancar la aplicación](#8-arrancar-la-aplicación)
9. [Probar el servicio](#9-probar-el-servicio)
10. [Detener el servicio](#10-detener-el-servicio)
11. [Solución de problemas](#11-solución-de-problemas)
12. [Extra: variante con Docker](#12-extra-variante-con-docker)

---

## 1. Requisitos previos

Necesitas instalado en tu sistema:

- **Python 3** con `pip` (incluye `venv`)
- **MySQL** o **MariaDB** (servidor y cliente)
- **Git** (para clonar el repositorio)

Para comprobar que ya están instalados:

```bash
python3 --version        # versión de Python
mysql --version          # versión de MySQL/MariaDB
git --version            # versión de Git
```

Si algún comando falla, instala el paquete correspondiente con tu gestor:

```bash
# Fedora / RHEL
sudo dnf install python3 python3-pip mariadb-server git

# Debian / Ubuntu
sudo apt install python3 python3-venv python3-pip mariadb-server git

# Arch Linux
sudo pacman -S python python-pip mariadb git
```

---

## 2. Obtener el proyecto

Clona el repositorio (o entra en tu copia local si ya la tienes):

```bash
git clone https://github.com/oramirez13/login_app.git
cd login_app
```

---

## 3. Crear el entorno virtual (venv)

El **entorno virtual** aísla las dependencias de Python del resto del sistema,
para que cada proyecto tenga sus propias versiones de librerías.

```bash
# crear el entorno virtual dentro de la carpeta venv/
python3 -m venv venv

# activarlo (cambia el prompt de la terminal)
source venv/bin/activate
```

Después de activarlo verás `(venv)` al inicio del prompt.

Para desactivarlo en cualquier momento:

```bash
deactivate
```

---

## 4. Instalar dependencias

Con el entorno virtual **activo**, instala las librerías del proyecto:

```bash
pip install -r requirements.txt
```

Esto instala:

- `Flask` — el framework web
- `mysql-connector-python` — conector para hablar con MySQL/MariaDB
- `gunicorn` — servidor WSGI para producción (opcional en desarrollo)

Para ver qué se instaló:

```bash
pip list
```

---

## 5. Levantar la base de datos

### 5.1 Enciende el servidor MariaDB/MySQL

```bash
sudo systemctl start mariadb      # sistem actual (usando systemd)
```

Para que arranque automáticamente al encender el equipo:

```bash
sudo systemctl enable mariadb
```

### 5.2 Verifica que esté activo

```bash
systemctl status mariadb
```

Debe mostrarse `active (running)`.

---

## 6. Crear base de datos y usuario

La app se conecta usando estas credenciales (definidas en `DB_CONFIG`
dentro de `app.py`):

- Host: `localhost`
- Usuario: `labuser`
- Contraseña: `labpass`
- Base de datos: `login_app`

Crea la base de datos, el usuario y los permisos:

```bash
sudo mariadb
```

Dentro del cliente SQL ejecuta:

```sql
-- crear la base de datos
CREATE DATABASE login_app;

-- crear el usuario de la app
CREATE USER 'labuser'@'localhost' IDENTIFIED BY 'labpass';

-- dar permisos a la base de datos login_app
GRANT ALL PRIVILEGES ON login_app.* TO 'labuser'@'localhost';

-- aplicar restricciones de inmediato
FLUSH PRIVILEGES;

-- salir del cliente SQL
EXIT;
```

> Nota: si tu servidor es MySQL (no MariaDB) el comando para entrar es
> `sudo mysql` y los comandos SQL son los mismos.

---

## 7. Cargar el esquema del laboratorio

El archivo `database.sql` crea las tablas `users` y `secret_flags` e inserta
los datos de prueba (credenciales y flags del CTF).

Sitúate en la carpeta del proyecto y carga el archivo:

```bash
cd /ruta/a/login_app
sudo mariadb < database.sql
```

Para confirmar que quedó cargado, entra al cliente y revisa las tablas:

```bash
sudo mariadb
```

```sql
USE login_app;
SHOW TABLES;            -- debe listar: users, secret_flags
SELECT * FROM users;    -- debe listar: admin y orami
EXIT;
```

---

## 8. Arrancar la aplicación

Con el entorno virtual **activo** y dentro de la carpeta del proyecto:

```bash
python app.py
```

Deberías ver algo como:

```
 * Running on http://127.0.0.1:5000
```

La app queda escuchando en el **puerto 5000** de tu equipo.

Abre el navegador:

```
http://localhost:5000
```

---

## 9. Probar el servicio

### 9.1 Login normal

Usa las credenciales de prueba:

| Usuario | Contraseña |
|---------|------------|
| admin   | 1234       |
| orami   | hackme     |

Al entrar accedes a `/dashboard` y puedes navegar por `/blog`, `/acerca`,
`/contacto` y `/buscar`.

### 9.2 Login con SQL Injection (auth bypass)

En el formulario de login, escribe en **Usuario**:

```sql
' OR '1'='1' --
```

y cualquier contraseña. El ataque hace que la consulta siempre devuelva un
resultado y el login se completa sin credenciales válidas.

### 9.3 Buscar con SQL Injection (exfiltración)

Estando logueado, en `/buscar` prueba el payload clásico:

```sql
' UNION SELECT id, flag FROM secret_flags -- 
```

Esto une la consulta original con la tabla oculta `secret_flags`, donde están
las flags del laboratorio.

### 9.4 Contacto con XSS

Estando logueado, en `/contacto` escribe en el campo mensaje:

```html
<script>alert('XSS');</script>
```

El script se ejecuta en el navegador porque el mensaje se renderiza con `|safe`.

---

## 10. Detener el servicio

Para **detener la app**: pulsa `Ctrl + C` en la terminal donde se ejecuta.

Para **detener la base de datos**:

```bash
sudo systemctl stop mariadb
```

---

## 11. Solución de problemas

| Problema | Causa probable | Solución |
|----------|----------------|----------|
| `Can't connect to MySQL server` | MariaDB no está corriendo | `sudo systemctl start mariadb` |
| `Access denied for user 'labuser'` | El usuario no fue creado correctamente | Repite el [paso 6](#6-crear-base-de-datos-y-usuario) |
| `Unknown database 'login_app'` | La base no fue creada | `CREATE DATABASE login_app;` |
| `Table 'login_app.users' doesn't exist` | No se cargó `database.sql` | Ejecuta `sudo mariadb < database.sql` |
| `Address already in use` | El puerto 5000 está ocupado | Cierra el proceso anterior o cambia el puerto en `app.py` |
| `ModuleNotFoundError` | Dependencias no instaladas | `pip install -r requirements.txt` con el venv activo |

---

## 12. Extra: variante con Docker

Si en lugar de MariaDB nativo prefieres levantar la base en un **contenedor Docker**
(sin tocar el MariaDB del sistema), puedes hacerlo así.

```bash
# crear el contenedor con la base y el usuario esperados
docker run -d --name login_app_db \
  -e MARIADB_DATABASE=login_app \
  -e MARIADB_USER=labuser \
  -e MARIADB_PASSWORD=labpass \
  -e MARIADB_ROOT_PASSWORD=rootpass \
  -p 3306:3306 \
  mariadb:latest

# copiar y ejecutar el esquema dentro del contenedor
docker cp database.sql login_app_db:/database.sql
docker exec login_app_db mariadb -u labuser -plabpass login_app < database.sql
```

Para detenerla:

```bash
docker stop login_app_db
```