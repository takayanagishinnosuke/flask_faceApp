## --blog用のBlueprintを作成しているファイル-- ##
from crypt import methods
from distutils.log import error
from tkinter import INSERT
from flask import(Blueprint, flash , g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
import numpy as np
from werkzeug.utils import secure_filename
import flaskr.recognition

bp = Blueprint('blog', __name__)
be_ossan = flaskr.recognition.BeOssan() ##recognitionのBeOssan()クラスを読み込み

## blog / のview
@bp.route('/')
def index():
  db = get_db()
  posts = db.execute(
    ##select文で ポストのID タイトル 本文 投稿日時 投稿者ID ユーザーネーム
    'SELECT p.id, title, body, created, author_id, username, filepath'
    ##postをpで参照 userはuで参照 /記事の投稿者IDとユーザーIDが一致するところを検索
    ' FROM post p JOIN user u ON p.author_id = u.id' 
    ##記事の一覧を並び替える/ desc 降順で並び替える
    ' ORDER BY created DESC'
  ).fetchall() ##この実行結果に対して全ての結果を取得しますよ
  return render_template('blog/index.html', posts=posts) ##index.html postsに上記のpostsを渡す

##--記事を作成する為のview--##
@bp.route('/create', methods=('GET', 'POST'))
@login_required  ##このviewが投稿状態であれば処理ができる
def create():
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    files = request.files.get('file')
    filename = secure_filename(files.filename)
    filepath = 'static/image/'+ filename

    error = None

    if not title: #もしもtitleがなければエラーを表示
      error = 'タイトルは必須です'

    if not files:
      error = '画像ファイルが選択されてません'

    if error is not None: #もしもerrorにNoneデータが入っていれば
      flash(error)
    
    else: #そうでなければ
      files.save(filepath) ##画像保存
      print(filepath) ##確認用
      be_ossan.to_bean(filepath) ##BeOssanクラスの合成関数へ渡す

      db = get_db()
      db.execute(
        'INSERT INTO post (title, body, author_id, filepath)' #postテーブルに4つ挿入
        ' VALUES (?, ?, ?, ?)',  ## valuesは #title,body,g.user,filepathを
        (title, body, g.user['id'], filepath) ##順番に注意
      )
      db.commit() #登録
      return redirect(url_for('blog.index')) #登録したらindexへ

  return render_template('blog/create.html') ##それ以外の場合はcreate.htmlに


##----作成してある記事を編集する関数群----##

#--更新するIDが一致している確認
def get_post(id, check_author=True): ##idが一致してるか確認
  post = get_db().execute(
    'SELECT p.id, title, body, created, author_id, username, filepath'
    ' FROM post p JOIN user u ON p.author_id = u.id' ##p.id u.idが一致しているところを探す
    ' WHERE p.id = ?',
    (id,)
  ).fetchone()

  if post is None: ##もしもpost idが無かったらエラーを返す
    abort(404, "IDが {id} の記事は存在しません。".format(id))
  #もしログインユーザーIDと投稿のユーザーIDが一致していなければエラー
  if check_author and post['author_id'] != g.user['id']:
    abort(403)

  return post

 #-タイトルを更新する為の関数
@bp.route('/<int:id>/update', methods=('POST', 'GET'))
@login_required
def update(id):
  post = get_post(id)

  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
      error = 'タイトルがありません'
    if error is not None:
      flash(error)
    else:
      db = get_db()
      db.execute(
        'UPDATE post SET title = ?, body = ?' #既存の記事を更新
        ' WHERE id = ?',
        (title, body, id)
      )
      db.commit()
      return redirect(url_for('blog.index'))
  ##更新がうまく行かなかったら
  return render_template('blog/update.html', post=post)

 #--削除をする関数--#
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
  get_post(id)
  db = get_db()
  db.execute('DELETE FROM post WHERE id = ?' , (id,))
  db.commit()
  return redirect(url_for('blog.index'))