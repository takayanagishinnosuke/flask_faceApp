-- DBの設計 --
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

-- userのテーブルを定義
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT, --自動連番
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- postのテーブルを定義
CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT, --自動連番
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  filepath TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id) --外部キー asthorIDとUserIDと関連づけられていますよ。
);
