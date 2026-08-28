# login_app

Aplicación Flask de laboratorio orientada a prácticas de ciberseguridad.
Incluye vulnerabilidades intencionales (SQL Injection y XSS) para poder
practicar técnicas de ataque y defensa en un entorno controlado.

## Nota importante (fines didácticos)

Esta aplicación es **exclusivamente un laboratorio de ciberseguridad**.

- Contiene **vulnerabilidades intencionales** creadas para estudiar ataques y defensa a nivel educativo.
- Debe ejecutarse **únicamente en un entorno aislado y controlado** (máquina local o VM).
- **SOLO con fines didácticos**: prueba los ataques de esta lista sobre *este proyecto*.
  Atacar sistemas sin autorización es ilegal y el uso fuera de un laboratorio es tu responsabilidad.
- **No** debe desplegarse en producción, exponerse a Internet ni conectarse a datos reales.

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

## Capturas del laboratorio

Vistas principales de la aplicación corriendo en local `(localhost:5000)`.

| Login | Dashboard tras autenticarse |
|-------|------------------------------|
| ![Login](screenshots/01_login.png?raw=true) | ![Dashboard](screenshots/02_dashboard.png?raw=true) |

| Blog | Contacto (formulario) |
|------|------------------------|
| ![Blog](screenshots/03_blog.png?raw=true) | ![Contacto](screenshots/05_contacto.png?raw=true) |

| SQLi con UNION en `/buscar` (exfiltra las flags) | XSS reflejado en `/contacto` |
|------|------------------------|
| ![SQLi UNION](screenshots/04_buscar.png?raw=true) | ![XSS reflejado](screenshots/06_xss_reflejado.png?raw=true) |

La última captura muestra el resultado del payload
`' UNION SELECT id, flag FROM secret_flags -- ` en el buscador y la del
contacto un `<script>` reflejado por `|safe`.

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

## Ataques del laboratorio (solo fines didácticos)

Cada ataque lista: dónde ocurre, cómo funciona, un payload de ejemplo y cómo
se mitiga en un escenario real. Todo se estudia sobre esta app, **en un
entorno controlado**.

---

### 1. SQL Injection — Bypass de autenticación en el login

- **Dónde:** `/login`, campo *Usuario* (`app.py:186`).
- **Cómo funciona:** la consulta se construye concatenando el input del usuario
  sin parametrizar:
  ```sql
  SELECT * FROM users WHERE username = '...' AND password = '...'
  ```
  Al inyectar una condición siempre verdadera, la consulta devuelve filas aunque
  las credenciales sean falsas.
- **Payload:**
  ```
  ' OR '1'='1' --
  ```
  El `'` cierra la cadena, `OR '1'='1'` vuelve verdadera la condición y `--`
  comenta el resto de la consulta (el `AND password`).
- **Impacto:** acceso a `/dashboard` sin credenciales válidas.
- **Mitigación:** usar consultas parametrizadas (ya existe la versión segura
  comentada en `app.py:188`), por ejemplo `cursor.execute(query, (username, password))`.

---

### 2. SQL Injection — Exfiltración de datos con UNION (tabla oculta)

- **Dónde:** `/buscar`, parámetro `q` (`app.py:135`).
- **Cómo funciona:** la sentencia `UNION SELECT` permite fusionar la consulta
  original con otra de creación propia, accediendo a tablas que la app no
  muestra (aquí, `secret_flags`).
- **Payload:**
  ```
  ' UNION SELECT id, flag FROM secret_flags -- 
  ```
- **Impacto:** vuelca las 4 flags del laboratorio en la página de resultados.
- **Mitigación:** parametrización de la consulta; además, el usuario de BD
  (`labuser`) solo debería tener `SELECT` sobre las tablas necesarias y nunca
  `CREATE`, `DROP` ni acceso a esquemas completos.

---

### 3. SQL Injection — Error-based (enumeración de información)

- **Dónde:** `/buscar`, parámetro `q` (`app.py:149-151`).
- **Cómo funciona:** cualquier excepción SQL se imprime en pantalla
  (`error = str(e)`), revelando detalle del motor de base de datos, nombres de
  columnas y estructura interna. Sirve para sondeo:
- **Payload:**
  ```
  '
  ```
  (una comilla simple rompe la consulta y el error queda visible).
- **Impacto:** información entregada por el servidor (information disclosure),
  que facilita construir inyecciones más precisas enumerando `information_schema`.
- **Mitigación:** no mostrar errores SQL al usuario; registrarlos en un log
  interno y responder con un mensaje genérico.

---

### 4. Reflected XSS — Ejecución de scripts en el navegador

- **Dónde:** `/contacto`, campo *Mensaje* (`contacto.html:105`).
- **Cómo funciona:** Jinja2 escapa las variables por defecto, pero aquí se
  aplica `{{ mensaje|safe }}`, que desactiva el escape y el dato llega al HTML
  como código interpretable.
- **Payload:**
  ```html
  <script>alert('XSS')</script>
  ```
  o variantes sin `<script>`:
  ```html
  <img src=x onerror=alert('XSS')>
  ```
- **Impacto:** ejecución de JavaScript en la sesión de la víctima: robo de
  cookies de sesión, keylogging, redirección a sitios maliciosos. Es *reflected*
  (el mensaje no se guarda en la base de datos).
- **Mitigación:** quitar `|safe` (Jinja2 ya escapa el valor por sí solo) o
  aplicar filtros de saneamiento y Content Security Policy (CSP).

---

### 5. Information disclosure + modo debug (potencial RCE)

- **Dónde:** `app.py:248` (`app.run(debug=True)`).
- **Cómo funciona:** con debug activo, Flask muestra el depurador interactivo de
  Werkzeug. Ante un error expone rutas del sistema y una consola ejecutable que,
  si el atacante obtiene el PIN del depurador, permite ejecutar código en el
  servidor (**Remote Code Execution**).
- **Payload:** provocar un error (por ejemplo, una consulta inválida) y usar la
  consola `/__debugger__`.
- **Impacto:** fuga de paths internos; en el peor caso, control total del servidor.
- **Mitigación:** `debug=False` en producción y usar `gunicorn app:app` en lugar
  de `python app.py`; páginas de error propias.

---

### 6. Credenciales débiles y contraseñas en texto plano

- **Dónde:** `database.sql` (datos del laboratorio).
- **Cómo funciona:** las contraseñas se guardan sin hash (`admin`/`1234`,
  `orami`/`hackme`). Si la base se filtra, las contraseñas se leen directo;
  además son triviales de adivinar.
- **Impacto:** acceso directo con las credenciales por defecto.
- **Mitigación:** almacenar hashes con bcrypt/argon2 y exigir contraseñas fuertes
  (en este lab es intencional para facilitar el ejercicio).

---

### 7. Fuerza bruta — sin límite de intentos en el login

- **Dónde:** `/login` (no hay rate limiting).
- **Cómo funciona:** el endpoint acepta intentos ilimitados sin bloqueo ni
  espera, por lo que se pueden probar miles de contraseñas por segundo.
- **Impacto:** con credenciales tan débiles como `admin`/`1234`, el acceso se
  obtiene incluso sin SQLi, solo probando combinaciones.
- **Mitigación:** limitación de tasa (número de intentos por IP/usuario),
  bloqueo temporal, delay progresivo y CAPTCHA.

---

### 8. CSRF — Envío de formularios sin autorización

- **Dónde:** `/contacto` (POST sin token CSRF).
- **Cómo funciona:** un sitio ajeno puede cargar una página con un formulario
  oculto que `POST` a `/contacto`; si la víctima está logueada, el navegador
  envía la cookie de sesión y el servidor procesa la petición como legítima.
- **Impacto:** en este laboratorio es bajo (el formulario no modifica datos),
  pero ilustra el vector que en apps reales permite cambiar contraseña, transferir
  dinero, etc.
- **Mitigación:** token CSRF (generado por sesión) validado en cada POST, o
  validar `Origin`/`Referer`.

---

### 9. Control de acceso insuficiente (sin roles)

- **Dónde:** rutas protegidas (`/dashboard`, `/blog`, `/acerca`).
- **Cómo funciona:** la única comprobación es `session.get("logged_in")`; todo
  usuario autenticado accede a todas las secciones, sin jerarquía de roles.
- **Impacto:** cualquier cuenta (incluso la obtenida por bypass del punto 1)
  tiene la misma visibilidad; no existe separación de privilegios.
- **Mitigación:** roles por sesión (usuario/admin) y verificación de permisos
  por ruta.

---

### 10. Señuelos y flags client-side (retos del CTF)

- **Dónde:** `templates/index.html:73` y `static/js/script.js`.
- **Cómo funciona:** no son vulnerabilidades, sino retos propios del CTF:
  - una *fake flag* oculta en el HTML: `FLAG{not_the_flag_you_are_looking_for}`
    (señuelo para despistar);
  - flags visibles en la consola del navegador (`F12`) según la ruta visitada
    (`FLAG{blog_console}`, `FLAG{acerca_console}`, `FLAG{contacto_console}`).
- **Impacto:** ejercitan el reconocimiento con herramientas de desarrollador y
  el análisis de código del lado del cliente.
- **Mitigación:** nada que corregir; forman parte del diseño del laboratorio.

---

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