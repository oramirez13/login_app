# login_app

Aplicacion Flask de laboratorio orientada a practicas de ciberseguridad.

## Nota

La app mantiene vulnerabilidades intencionales para fines de laboratorio.

## Render

Segun la documentacion oficial de Render:

- Flask se despliega con `pip install -r requirements.txt` y un arranque tipo `gunicorn app:app`
- Render Postgres es la base administrada nativa
- las variables de entorno deben configurarse en el dashboard o con `render.yaml`
- en el plan gratis no se puede usar `preDeployCommand`, por eso la app inicializa el esquema PostgreSQL al primer acceso

Fuentes:

- https://render.com/docs/deploy-flask
- https://render.com/docs/databases
- https://render.com/docs/configure-environment-variables
- https://render.com/docs/blueprint-spec

## Lo que hace esta version

- En Render usa PostgreSQL mediante `DATABASE_URL`
- Localmente puede seguir usando MySQL con las credenciales originales
- Incluye `render.yaml` para crear el servicio web y la base Postgres
- Incluye `database_postgres.sql` para cargar el laboratorio en PostgreSQL

## Ejecutar localmente con MySQL

```bash
cd flask/login_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Despliegue en Render

### Opcion recomendada: con Blueprint

1. Sube este proyecto a GitHub.
2. En Render, elige `New +` -> `Blueprint`.
3. Selecciona el repositorio.
4. Render detectara `render.yaml` y te propondra:
   - un `Web Service`
   - una base `Postgres`
5. Crea los recursos.
6. Cuando la base este lista, abre su panel y copia la `Internal Database URL` si la quieres revisar.
7. En el servicio web, Render usara:
   - `buildCommand: pip install -r requirements.txt`
   - `startCommand: gunicorn app:app`

### Cargar datos del laboratorio

En esta version para Render free, la app intenta crear las tablas e insertar los datos iniciales al primer acceso usando `database_postgres.sql`.

## Variables de entorno

- `DATABASE_URL`: usada en Render para PostgreSQL
- `SECRET_KEY`: opcional para sobreescribir la clave de sesion
- `TECHNOVA_DB_HOST`, `TECHNOVA_DB_USER`, `TECHNOVA_DB_PASSWORD`, `TECHNOVA_DB_NAME`: no aplican aqui

## Start command manual

Si prefieres crear el servicio manualmente en Render en vez de usar Blueprint:

- Build Command:
  - `pip install -r requirements.txt`
- Start Command:
  - `gunicorn app:app`
