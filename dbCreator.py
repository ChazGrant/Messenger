'''
CREATE TABLE IF NOT EXISTS messages(
    message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT,
    text TEXT,
    timestamp FLOAT,
    server_id INT,
    FOREIGN KEY (server_id) REFERENCES servers(server_id));


CREATE TABLE servers(
        server_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        server_name TEXT,
        admin TEXT);
'''