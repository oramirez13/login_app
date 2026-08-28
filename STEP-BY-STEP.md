# STEP-BY-STEP: set up login_app from scratch

Step-by-step guide to set up the service **locally** with **MySQL/MariaDB**,
without depending on cloud services (Render, Netlify, etc.).

At the end of this guide you will have the app running at
`http://localhost:5000` with its `login_app` database.

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [Get the project](#2-get-the-project)
3. [Create the virtual environment (venv)](#3-create-the-virtual-environment-venv)
4. [Install dependencies](#4-install-dependencies)
5. [Set up the database](#5-set-up-the-database)
6. [Create database and user](#6-create-database-and-user)
7. [Load the lab schema](#7-load-the-lab-schema)
8. [Start the application](#8-start-the-application)
9. [Test the service](#9-test-the-service)
10. [Stop the service](#10-stop-the-service)
11. [Troubleshooting](#11-troubleshooting)
12. [Extra: Docker variant](#12-extra-docker-variant)

---

## 1. Prerequisites

You need installed on your system:

- **Python 3** with `pip` (includes `venv`)
- **MySQL** or **MariaDB** (server and client)
- **Git** (to clone the repository)

To check they are already installed:

```bash
python3 --version        # Python version
mysql --version          # MySQL/MariaDB version
git --version            # Git version
```

If any command fails, install the corresponding package with your manager:

```bash
# Fedora / RHEL
sudo dnf install python3 python3-pip mariadb-server git

# Debian / Ubuntu
sudo apt install python3 python3-venv python3-pip mariadb-server git

# Arch Linux
sudo pacman -S python python-pip mariadb git
```

---

## 2. Get the project

Clone the repository (or enter your local copy if you already have it):

```bash
git clone https://github.com/oramirez13/login_app.git
cd login_app
```

---

## 3. Create the virtual environment (venv)

The **virtual environment** isolates the Python dependencies from the rest
of the system, so each project has its own library versions.

```bash
# create the virtual environment inside the venv/ folder
python3 -m venv venv

# activate it (changes the terminal prompt)
source venv/bin/activate
```

After activating it you will see `(venv)` at the start of the prompt.

To deactivate it at any time:

```bash
deactivate
```

---

## 4. Install dependencies

With the virtual environment **active**, install the project libraries:

```bash
pip install -r requirements.txt
```

This installs:

- `Flask` - the web framework
- `mysql-connector-python` - connector to talk to MySQL/MariaDB
- `gunicorn` - WSGI server for production (optional in development)

To see what was installed:

```bash
pip list
```

---

## 5. Set up the database

### 5.1 Ports in use on this machine

Several databases coexist on this machine, which is why the native MariaDB
moves to port **3308**:

| Port | Use                            | Engine  | Note                           |
| ---- | ------------------------------ | ------- | ------------------------------ |
| 3306 | LAMPP (Apache + MySQL)         | MySQL   | reserved by LAMPP when running |
| 3307 | `sabd_mariadb` (container)     | MariaDB | do not touch it                |
| 3308 | **login_app** (native service) | MariaDB | the app connects here          |

### 5.2 Adjust the native MariaDB port to 3308

The file `/etc/my.cnf` defines the port. If it has `3307` (conflicts with the
container) or `3306` (conflicts with LAMPP), change it to `3308`:

```bash
sudo sed -i 's/^port=330[67]$/port=3308/' /etc/my.cnf
```

Verify it ended up like this:

```bash
cat /etc/my.cnf
```

It must show `port=3308` both in the `[mysqld]` section and in `[client]`.

### 5.3 Start the MariaDB server

```bash
sudo systemctl start mariadb      # starts the service
```

To make it start automatically on boot:

```bash
sudo systemctl enable mariadb
```

### 5.4 Verify it is active

```bash
systemctl status mariadb
```

It must show `active (running)` and listening on `3308`.

---

## 6. Create database and user

The app connects with these credentials (defined in `DB_CONFIG`
inside `app.py`):

- Host: `localhost`
- Port: `3308`
- User: `labuser`
- Password: `labpass`
- Database: `login_app`

Create the database, the user and the permissions:

```bash
sudo mariadb
```

Inside the SQL client run:

```sql
-- create the database
CREATE DATABASE login_app;

-- create the app user
CREATE USER 'labuser'@'localhost' IDENTIFIED BY 'labpass';

-- grant permissions on the login_app database
GRANT ALL PRIVILEGES ON login_app.* TO 'labuser'@'localhost';

-- apply restrictions immediately
FLUSH PRIVILEGES;

-- exit the SQL client
EXIT;
```

> Note: if your server is MySQL (not MariaDB) the command to enter is
> `sudo mysql` and the SQL commands are the same.

---

## 7. Load the lab schema

The file `database.sql` creates the `users` and `secret_flags` tables and
inserts the test data (credentials and CTF flags).

Go to the project folder and load the file:

```bash
cd /path/to/login_app
sudo mariadb < database.sql
```

To confirm it was loaded, enter the client and check the tables:

```bash
sudo mariadb
```

```sql
USE login_app;
SHOW TABLES;            -- should list: users, secret_flags
SELECT * FROM users;    -- should list: admin and orami
EXIT;
```

---

## 8. Start the application

With the virtual environment **active** and inside the project folder:

```bash
python app.py
```

You should see something like:

```
 * Running on http://127.0.0.1:5000
```

The app stays listening on **port 5000** of your machine.

Open the browser:

```
http://localhost:5000
```

---

## 9. Test the service

### 9.1 Normal login

Use the test credentials:

| Username | Password |
| -------- | -------- |
| admin    | 1234     |
| orami    | hackme   |

After logging in you access `/dashboard` and can browse `/blog`, `/about`,
`/contact` and `/search`.

### 9.2 Login with SQL Injection (auth bypass)

In the login form, type in **Username**:

```sql
' OR '1'='1' --
```

and any password. The attack makes the query always return a
result and the login completes without valid credentials.

### 9.3 Search with SQL Injection (exfiltration)

While logged in, in `/search` try the classic payload:

```sql
' UNION SELECT id, flag FROM secret_flags --
```

This merges the original query with the hidden `secret_flags` table, where
the lab flags are stored.

### 9.4 Contact with XSS

While logged in, in `/contact` type in the message field:

```html
<script>
  alert("XSS");
</script>
```

The script executes in the browser because the message is rendered with `|safe`.

---

## 10. Stop the service

To **stop the app**: press `Ctrl + C` in the terminal where it runs.

To **stop the database**:

```bash
sudo systemctl stop mariadb
```

---

## 11. Troubleshooting

| Problem                                 | Likely cause                                                               | Solution                                                                   |
| --------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `Can't connect to MySQL server`         | MariaDB is not running                                                     | `sudo systemctl start mariadb`                                             |
| `Bind on TCP/IP port. Got error: 98`    | The configured port (3307) is already used by the `sabd_mariadb` container | `sudo sed -i 's/port=3307/port=3308/' /etc/my.cnf` and restart the service |
| `Access denied for user 'labuser'`      | The user was not created correctly                                         | Repeat [step 6](#6-create-database-and-user)                               |
| `Unknown database 'login_app'`          | The database was not created                                               | `CREATE DATABASE login_app;`                                               |
| `Table 'login_app.users' doesn't exist` | `database.sql` was not loaded                                              | Run `sudo mariadb < database.sql`                                          |
| `Connection refused (3308)`             | LAMPP or the container changed the port                                    | Confirm `/etc/my.cnf` has `port=3308` and that the service is active       |
| `Address already in use` (port 5000)    | A previous Flask server is still open                                      | Kill the process or change the port in `app.py`                            |
| `ModuleNotFoundError`                   | Dependencies not installed                                                 | `pip install -r requirements.txt` with the venv active                     |

---

## 12. Extra: Docker variant

If instead of native MariaDB you prefer to set the database up in a **Docker
container** (without touching the system MariaDB), you can do it like this.
Stop the native service first, because both would use port 3308:

```bash
sudo systemctl stop mariadb

# create the container with the expected database and user (port 3308)
docker run -d --name login_app_db \
  -e MARIADB_DATABASE=login_app \
  -e MARIADB_USER=labuser \
  -e MARIADB_PASSWORD=labpass \
  -e MARIADB_ROOT_PASSWORD=rootpass \
  -p 3308:3306 \
  mariadb:latest

# copy and run the schema inside the container
docker cp database.sql login_app_db:/database.sql
docker exec login_app_db mariadb -u labuser -plabpass login_app < database.sql
```

To stop it:

```bash
docker stop login_app_db
```
