USE ${prod_db};

/* comments → posts → users / categories / admins */
DELETE FROM comments
WHERE content = 'Nice post!';

DELETE FROM posts
WHERE title = 'My First Post';

DELETE FROM users
WHERE username IN ('alice', 'bob');

DELETE FROM admins
WHERE username = 'admin';

DELETE FROM categories
WHERE name IN ('Tech', 'Life');
