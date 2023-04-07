CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT,
    created INTEGER
);

CREATE TABLE IF NOT EXISTS rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    now_rate INTEGER,
    created INTEGER
);

CREATE TABLE IF NOT EXISTS wallets (
    id TEXT UNIQUE,                 -- Ключ вида fi34u-3128f-12rfw-r2398g (5 символов в ячейке)
    user_id INTEGER UNIQUE,
    tokens INTEGER DEFAULT 0,
    diamonds INTEGER DEFAULT 0,
    created INTEGER
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT UNIQUE,
    amount INTEGER,
    now_rate INTEGER,
    sender_wallet_id TEXT,
    recipient_wallet_id TEXT,
    created INTEGER
);

CREATE TABLE IF NOT EXISTS sells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER,
    now_rate INTEGER,
    user_id INTEGER,
    created INTEGER
);

