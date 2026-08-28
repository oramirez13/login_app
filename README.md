# login_app

Flask laboratory application for cybersecurity practice.
It includes intentional vulnerabilities (SQL Injection and XSS) so you can
practice attack and defense techniques in a controlled environment.

## Important note (educational purposes only)

This application is **exclusively a cybersecurity laboratory**.

- It contains **intentional vulnerabilities** created to study attacks and defenses at an educational level.
- It must be run **only in an isolated and controlled environment** (local machine or VM).
- **FOR EDUCATIONAL PURPOSES ONLY**: test the attacks in this list on _this project_.
  Attacking systems without authorization is illegal, and using it outside a lab is your responsibility.
- It must **not** be deployed to production, exposed to the Internet, or connected to real data.

## What this app does

- Login with `SQL Injection` to bypass authentication
- `/search` page vulnerable to `SQL Injection` (probing and exfiltration)
- `/contact` page vulnerable to `XSS`
- Session-protected routes (`/dashboard`, `/blog`, `/about`)
- Uses **MySQL/MariaDB** as its only database (configuration in `DB_CONFIG`)

## Database ports on this machine

| Port | Use                            | Engine  |
| ---- | ------------------------------ | ------- |
| 3306 | LAMPP (Apache + MySQL)         | MySQL   |
| 3307 | `sabd_mariadb` (container)     | MariaDB |
| 3308 | **login_app** (native service) | MariaDB |

The app connects to **port 3308** to avoid colliding with LAMPP or the
Docker container.

## Requirements

- Python 3
- MySQL or MariaDB running on `localhost:3308`
- The database and user defined in `DB_CONFIG`:
  - Host: `localhost`
  - Port: `3308`
  - User: `labuser`
  - Password: `labpass`
  - Database: `login_app`

## Quick install

```bash
# 0. Configure native MariaDB on port 3308 (3306 is LAMPP, 3307 is the container)
sudo sed -i 's/^port=330[67]$/port=3308/' /etc/my.cnf
sudo systemctl start mariadb

# 1. Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database, the user and load the schema
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

# 4. Run the app
python app.py
```

Open the browser: `http://localhost:5000`

## Lab screenshots

The application includes the following main screens when running locally at `http://localhost:5000`.

| Login page                                           | Dashboard after authentication                           |
| ---------------------------------------------------- | -------------------------------------------------------- |
| ![Login page](screenshots/login_app_01.png?raw=true) | ![Dashboard page](screenshots/login_app_02.png?raw=true) |

| Blog page                                                                    | About page                                                                          |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| ![Blog page with vulnerability cards](screenshots/login_app_03.png?raw=true) | ![About page with lab overview and warnings](screenshots/login_app_04.png?raw=true) |

| Contact form (reflected XSS challenge)                 | Search page (SQL Injection challenge)                 |
| ------------------------------------------------------ | ----------------------------------------------------- |
| ![Contact page](screenshots/login_app_05.png?raw=true) | ![Search page](screenshots/login_app_06.png?raw=true) |

| 404 error page                                     | Not found and custom error handling                                                            |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| ![404 page](screenshots/login_app_09.png?raw=true) | This page is shown when a route is missing or the request cannot be resolved by the Flask app. |

The login screen shows the initial authentication form used to test SQLi bypass techniques. The dashboard confirms that the session is active after login. The blog page presents the main vulnerability categories in a card-based layout, while the about page explains the purpose of the lab, its limitations, and its educational scope. The contact form demonstrates a reflected XSS payload rendered unsafely in the browser, the search page shows the UNION-based SQLi challenge used to extract hidden flags from the database, and the 404 page provides a controlled response for missing routes.

## Test credentials

| Username | Password |
| -------- | -------- |
| admin    | 1234     |
| orami    | hackme   |

## Available routes

| Route        | Access  | Vulnerability            |
| ------------ | ------- | ------------------------ |
| `/`          | public  | login (SQLi auth bypass) |
| `/login`     | public  | login endpoint (SQLi)    |
| `/search`    | session | SQL Injection            |
| `/contact`   | session | XSS                      |
| `/dashboard` | session | -                        |
| `/blog`      | session | -                        |
| `/about`     | session | -                        |
| `/logout`    | session | closes the session       |

## Lab attacks (educational purposes only)

Each attack lists: where it happens, how it works, an example payload and how
it is mitigated in a real scenario. Everything is studied on this app, **in a
controlled environment**.

---

### 1. SQL Injection - Authentication bypass in the login

- **Where:** `/login`, _Username_ field (`app.py:186`).
- **How it works:** the query is built by concatenating the user input
  without parameterization:
  ```sql
  SELECT * FROM users WHERE username = '...' AND password = '...'
  ```
  By injecting an always-true condition, the query returns rows even though
  the credentials are false.
- **Payload:**
  ```
  ' OR '1'='1' --
  ```
  The `'` closes the string, `OR '1'='1'` makes the condition true and `--`
  comments out the rest of the query (the `AND password` part).
- **Impact:** access to `/dashboard` without valid credentials.
- **Mitigation:** use parameterized queries (the secure version already exists
  commented out in `app.py:189`), e.g. `cursor.execute(query, (username, password))`.

---

### 2. SQL Injection - Data exfiltration with UNION (hidden table)

- **Where:** `/search`, parameter `q` (`app.py:137`).
- **How it works:** the `UNION SELECT` statement merges the original query
  with a custom one, accessing tables the app does not show (here, `secret_flags`).
- **Payload:**
  ```
  ' UNION SELECT id, flag FROM secret_flags --
  ```
- **Impact:** dumps the 4 lab flags in the results page.
- **Mitigation:** parameterize the query; additionally, the DB user
  (`labuser`) should only have `SELECT` on the needed tables and never
  `CREATE`, `DROP` or access to full schemas.

---

### 3. SQL Injection - Error-based (information enumeration)

- **Where:** `/search`, parameter `q` (`app.py:153`).
- **How it works:** any SQL exception is printed on screen
  (`error = str(e)`), revealing database engine details, column names and
  internal structure. Useful for probing:
- **Payload:**
  ```
  '
  ```
  (a single quote breaks the query and the error becomes visible).
- **Impact:** information disclosure from the server, which makes it easier
  to build more precise injections by enumerating `information_schema`.
- **Mitigation:** do not show SQL errors to the user; log them internally
  and respond with a generic message.

---

### 4. Reflected XSS - Script execution in the browser

- **Where:** `/contact`, _Message_ field (`contact.html:108`).
- **How it works:** Jinja2 escapes variables by default, but here
  `{{ message|safe }}` is used, which disables escaping and the data reaches
  the HTML as interpretable code.
- **Payload:**
  ```html
  <script>
    alert("XSS");
  </script>
  ```
  or variants without `<script>`:
  ```html
  <img src=x onerror=alert('XSS')>
  ```
- **Impact:** JavaScript execution in the victim's session: session cookie
  theft, keylogging, redirection to malicious sites. It is _reflected_
  (the message is not stored in the database).
- **Mitigation:** remove `|safe` (Jinja2 already escapes the value by
  itself) or apply sanitization filters and a Content Security Policy (CSP).

---

### 5. Information disclosure + debug mode (potential RCE)

- **Where:** `app.py:252` (`app.run(debug=True)`).
- **How it works:** with debug active, Flask shows the interactive Werkzeug
  debugger. On an error it exposes system paths and an executable console
  which, if the attacker obtains the debugger PIN, allows code execution on
  the server (**Remote Code Execution**).
- **Payload:** trigger an error (e.g. an invalid query) and use the
  `/__debugger__` console.
- **Impact:** internal path leakage; in the worst case, full server control.
- **Mitigation:** `debug=False` in production and use `gunicorn app:app`
  instead of `python app.py`; custom error pages.

---

### 6. Weak credentials and passwords in plain text

- **Where:** `database.sql` (lab data).
- **How it works:** passwords are stored without hashing (`admin`/`1234`,
  `orami`/`hackme`). If the database leaks, passwords are read directly;
  besides, they are trivial to guess.
- **Impact:** direct access with the default credentials.
- **Mitigation:** store hashes with bcrypt/argon2 and require strong
  passwords (intentional in this lab to make the exercise easier).

---

### 7. Brute force - no login attempt limit

- **Where:** `/login` (no rate limiting).
- **How it works:** the endpoint accepts unlimited attempts without blocking
  or delay, so thousands of passwords can be tried per second.
- **Impact:** with credentials as weak as `admin`/`1234`, access is obtained
  even without SQLi, just by trying combinations.
- **Mitigation:** rate limiting (attempts per IP/user), temporary lockout,
  progressive delay and CAPTCHA.

---

### 8. CSRF - Submitting forms without authorization

- **Where:** `/contact` (POST without CSRF token).
- **How it works:** a third-party site can load a page with a hidden form
  that `POST`s to `/contact`; if the victim is logged in, the browser sends
  the session cookie and the server processes the request as legitimate.
- **Impact:** low in this lab (the form does not modify data), but it
  illustrates the vector that in real apps allows changing passwords,
  transferring money, etc.
- **Mitigation:** CSRF token (generated per session) validated on every
  POST, or validate `Origin`/`Referer`.

---

### 9. Insufficient access control (no roles)

- **Where:** protected routes (`/dashboard`, `/blog`, `/about`).
- **How it works:** the only check is `session.get("logged_in")`; every
  authenticated user accesses all sections, without a role hierarchy.
- **Impact:** any account (even one obtained by the point 1 bypass) has the
  same visibility; there is no privilege separation.
- **Mitigation:** roles per session (user/admin) and permission checks per
  route.

---

### 10. Decoys and client-side flags (CTF challenges)

- **Where:** `templates/index.html:72` and `static/js/script.js`.
- **How it works:** these are not vulnerabilities, but CTF-specific challenges:
  - a _fake flag_ hidden in the HTML: `FLAG{not_the_flag_you_are_looking_for}`
    (decoy to mislead);
  - flags visible in the browser console (`F12`) depending on the route
    visited (`FLAG{blog_console}`, `FLAG{about_console}`, `FLAG{contact_console}`).
- **Impact:** they practice reconnaissance with developer tools and
  client-side code analysis.
- **Mitigation:** nothing to fix; they are part of the lab design.

---

## Project structure

- `app.py` - Flask application (routes and lab logic)
- `database.sql` - MySQL schema with the lab data
- `templates/` - HTML templates rendered by Flask
- `static/` - CSS, JavaScript and images
- `STEP-BY-STEP.md` - complete guide to set up the service from scratch

## From-scratch guide

To set up the whole service step by step (dependencies, database, user,
startup and tests), see [`STEP-BY-STEP.md`](STEP-BY-STEP.md).

## Environment variables (optional)

- `SECRET_KEY`: defines a fixed key to sign sessions. If not defined, the
  app generates a random key on every start (sessions are invalidated when
  the server restarts).
