# login_app

Aplicación Flask de laboratorio orientada a prácticas de ciberseguridad.
Incluye vulnerabilidades intencionales (SQL Injection y XSS) para poder
practicar técnicas de ataque y defensa en un entorno controlado.

## Nota

La app mantiene vulnerabilidades intencionales para fines de laboratorio.
**No debe desplegarse en producción ni conectarse a datos reales.**

## Lo que hace esta app

- Login con `SQL Injection` para evadir la autenticación
- Página `/buscar` vulnerable a `SQL Injection` (sondeo y exfiltración)
- Página `/contacto` vulnerable a `XSS`
- Rutas protegidas por sesión (`/dashboard`, `/blog`, `/acerca`)
- Usa **MySQL/MariaDB** como única base de datos (configuración en `DB_CONFIG`)

## Puertos de base de datos en este equipo

| Puerto | Usuario                     | Motor          |
|--------|-----------------------------|----------------|
| 3306   | LAMPP (Apache + MySQL)      | MySQL          |
| 3307   | `sabd_mariadb` (contenedor) | MariaDB        |
| 3308   | **login_app** (servicio nativo) | MariaDB    |

La app se conecta al **puerto 3308** para no chocar con LAMPP ni con el
contenedor Docker.

## Requisitos

- Python 3
- MySQL o MariaDB corriendo en `localhost:3308`
- La base de datos y el usuario definidos en `DB_CONFIG`:
  - Host: `localhost`
  - Puerto: `3308`
  - Usuario: `labuser`
  - Contraseña: `labpass`
  - Base de datos: `login_app`

## Instalación rápida

```bash
# 0. Configurar MariaDB nativo en el puerto 3308 (3306 es de LAMPP, 3307 del contenedor)
sudo sed -i 's/^port=330[67]$/port=3308/' /etc/my.cnf
sudo systemctl start mariadb

# 1. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear la base de datos, el usuario y cargar el esquema
sudo mariadb
```

```sql
CREATE DATABASE login_app;
CREATE USER 'labuser'@'localhost' IDENTIFIED BY 'labpass';
GRANT ALL PRIVILEGES ON login_app.* TO 'labuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
sudo mariadb < database.sql

# 4. Ejecutar la app
python app.py
```

Abrir en el navegador: `http://localhost:5000`

## Credenciales de prueba

| Usuario | Contraseña |
|---------|------------|
| admin   | 1234       |
| orami   | hackme     |

## Rutas disponibles

| Ruta        | Acceso      | Vulnerabilidad               |
|-------------|-------------|------------------------------|
| `/`         | pública     | login (SQLi auth bypass)     |
| `/login`    | pública     | endpoint del login (SQLi)    |
| `/buscar`   | sesión      | SQL Injection                |
| `/contacto` | sesión      | XSS                          |
| `/dashboard`| sesión      | -                            |
| `/blog`     | sesión      | -                            |
| `/acerca`   | sesión      | -                            |
| `/logout`   | sesión      | cierra la sesión             |

## Estructura del proyecto

- `app.py` — aplicación Flask (rutas y lógica del laboratorio)
- `database.sql` — esquema MySQL con los datos del laboratorio
- `templates/` — plantillas HTML renderizadas por Flask
- `static/` — CSS, JavaScript e imágenes
- `STEP-BY-STEP.md` — guía completa para levantar el servicio desde cero

## Guía desde cero

Para montar el servicio completo paso a paso (dependencias, base de datos,
usuario, arranque y pruebas), consulta [`STEP-BY-STEP.md`](STEP-BY-STEP.md).

## Variables de entorno (opcional)

- `SECRET_KEY`: define una clave fija para firmar las sesiones. Si no se
  define, la app genera una clave aleatoria en cada arranque (las sesiones
  se invalidan al reiniciar el servidor).