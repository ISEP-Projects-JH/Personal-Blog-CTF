USE ${prod_db};

INSERT INTO users (username, email, password_hash) VALUES
('alice', 'alice@example.com', 'hash_alice'),
('bob', 'bob@example.com', 'hash_bob')
ON DUPLICATE KEY UPDATE
  password_hash = VALUES(password_hash);

INSERT INTO admins (username, password_hash) VALUES
('admin', 'hash_admin')
ON DUPLICATE KEY UPDATE
  password_hash = VALUES(password_hash);

INSERT INTO categories (name) VALUES
('Tech'),
('Life')
ON DUPLICATE KEY UPDATE
  name = VALUES(name);

INSERT INTO posts (title, content, author_id, category_id)
SELECT
  'My First Post',
  'Hello world',
  u.id,
  c.id
FROM users u, categories c
WHERE u.username = 'alice'
  AND c.name = 'Tech'
ON DUPLICATE KEY UPDATE
  content = VALUES(content);

INSERT INTO comments (post_id, user_id, content)
SELECT
  p.id,
  u.id,
  'Nice post!'
FROM posts p, users u
WHERE p.title = 'My First Post'
  AND u.username = 'bob'
ON DUPLICATE KEY UPDATE
  content = VALUES(content);
