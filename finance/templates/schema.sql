CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00
    );

CREATE TABLE sqlite_sequence (
    name,seq);

CREATE UNIQUE INDEX username
ON users (username);


CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    stock TEXT NOT NULL
    );

CREATE UNIQUE INDEX stock
ON stocks (stock);

CREATE TABLE stock_assignments (
    user_id INTEGER,
    stock_id INTEGER,
    shares INTEGER,
    price INTEGER,
    epoch_time INTEGER,
    FOREIGN KEY(user_id)
        REFERENCES users (id)
    FOREIGN KEY(stock_id)
        REFERENCES stocks (id)
    );

CREATE TABLE stock_assignments_temp AS
    SELECT user_id, stock_id, shares, bought_price, epoch_time
    FROM stock_assignments;





SELECT shares, stock, username, cash FROM stock_assignments
JOIN stocks
ON stock.id = stock_assignments.stock_id
JOIN users
ON users.id = stock_assignments.user_id
WHERE users.id = ?




SELECT user_id, SUM(shares) as sumshares, stock, price FROM stock_assignments
JOIN stocks
ON stocks.id = stock_assignments.stock_id
JOIN users
ON users.id = stock_assignments.user_id
WHERE users.id = 1
GROUP BY stock


SELECT user_id, SUM(shares) as sumshares, stock
FROM stock_assignments
JOIN stocks ON stocks.id = stock_assignments.stock_id
JOIN users ON users.id = stock_assignments.user_id
WHERE users.id = 1
GROUP BY stock


SELECT user_id, shares, stock
FROM stock_assignments
JOIN stocks ON stocks.id = stock_assignments.stock_id
JOIN users ON users.id = stock_assignments.user_id
WHERE users.id = 1


SELECT * FROM stock_assignments
JOIN stocks
ON stocks.id = stock_assignments.stock_id
JOIN users
ON users.id = stock_assignments.user_id
WHERE users.id = 1
GROUP BY stock


SELECT * FROM users WHERE id = 1;





ALTER TABLE stock_assignments RENAME COLUMN purchase_price TO bought_price;


ALTER TABLE stock_assignments ADD COLUMN sale_price INTEGER;



datetime(epoch_time, 'unixepoch', 'localtime')


SELECT stock, shares, price, datetime(epoch_time/1000, 'unixepoch', 'utc') AS time_utc, user_id
FROM stock_assignments
JOIN stocks ON stocks.id = stock_assignments.stock_id
JOIN users ON users.id = stock_assignments.user_id
WHERE users.id = ?
GROUP BY stock


SELECT datetime(epoch_time,'auto') AS timestamp_utc
FROM stock_assignments;
