DROP DATABASE IF EXISTS ${ctf_db};

CREATE DATABASE ${ctf_db}
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ${ctf_db};

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  author_id INT NOT NULL,
  category_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_published BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (author_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB;

CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;


CREATE TABLE ctf_progress (
  id INT PRIMARY KEY CHECK (id = 1),
  user_pwned BOOLEAN NOT NULL DEFAULT FALSE,
  admin_pwned BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;

INSERT INTO ctf_progress (id, user_pwned, admin_pwned)
VALUES (1, FALSE, FALSE);

INSERT INTO users (username, email, password_hash) VALUES
('alice', 'alice@example.com', 'hash_alice'),
('bob', 'bob@example.com', 'hash_bob');

INSERT INTO admins (username, password_hash) VALUES
('admin', 'hash_admin');

INSERT INTO categories (name) VALUES
('Tech'),
('Life');

INSERT INTO posts (title, content, author_id, category_id) VALUES
('My First Post', 'Hello world', 1, 1);

INSERT INTO comments (post_id, user_id, content) VALUES
(1, 2, 'Nice post!');
