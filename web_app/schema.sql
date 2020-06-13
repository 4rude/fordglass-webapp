DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS user;

CREATE TABLE item (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	author_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	item_name TEXT,
	picture_url TEXT,
	description TEXT,
	category_id INTEGER NOT NULL,
	FOREIGN KEY (author_id) REFERENCES user(id),
	FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL
);

CREATE TABLE category (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	category TEXT NOT NULL,
	sub_category TEXT 
);

INSERT INTO category (category, sub_category)
VALUES ("paraphernalia", "bong"); 