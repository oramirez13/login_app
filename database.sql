-- Create the database
CREATE DATABASE login_app;

-- Use the database
USE login_app;

-- Create the users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY, -- unique ID
    username VARCHAR(50),              -- username
    password VARCHAR(50)               -- password (vulnerable: plain text)
);

-- Insert admin user
INSERT INTO users (username, password) VALUES ('admin', '1234');

-- Another user
INSERT INTO users (username, password) VALUES ('orami', 'hackme');

-- Hidden flags table (the player must discover it with SQLi)
CREATE TABLE secret_flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),     -- flag name
    flag VARCHAR(100)      -- flag value
);

-- CTF flags
INSERT INTO secret_flags (name, flag) VALUES ('flag_1', 'FLAG{union_select_master}');
INSERT INTO secret_flags (name, flag) VALUES ('flag_2', 'FLAG{information_schema_pro}');
INSERT INTO secret_flags (name, flag) VALUES ('flag_3', 'FLAG{blind_sqli_hunter}');
INSERT INTO secret_flags (name, flag) VALUES ('flag_4', 'FLAG{database_enum_complete}');