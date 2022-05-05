##---全てのページの通信処理をまとめているファイル---##

from crypt import methods
from distutils.log import error
import functools
from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from jinja2 import StrictUndefined
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

## bpという認証を束ねるインスタンスに対してルートを定義
bp = Blueprint('auth', __name__, url_prefix='/auth')

## ログイン認証 --routeの指定 GET POST の通信方式
@bp.route('/register', methods=('GET','POST'))
def register():
  if request.method == 'POST': ##POSTだったら
    username = request.form['username'] ##usernameという名前のついているデータ
    password = request.form['password'] # passwordという名前のデータ
    db = get_db() #DBとの照合の為にDBを呼び出す get_db
    error = None ##errorであれば空

    if not username: ##usernameが入って無かったら
      error = "ユーザー名を入力してください"
    elif not password: #passwordが入って無かったら
      error = "パスワードを入力してください"
    ## どっちも空でなければ DBからUserを検索するQuery
    elif db.execute( 
      'SELECT id FROM user WHERE username = ?', (username,) ##usernameと一致するIDを取得
    ).fetchone() is not None: ##もしもNoneでなければ
        error = 'ユーザー {} はすでに登録されています' .format(username)
    ##もしもここまでエラーがでなければ…新しくDBに入力
    if error is None:
      db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)', ##userテーブルにテータを入れますよ。 usernameとpasswordに それは valeus 
        (username, generate_password_hash(password)), ## ? = username ? =password(暗号化 hash)
      )
      db.commit() ##commitする
      return redirect(url_for('auth.login')) ## リダイレクト(authのloginへ)

    flash(error)
  
  return render_template('auth/register.html') ##登録に失敗した時は(auth/register.html)

##ログイン承認処理
@bp.route('/login', methods = ('GET', 'POST'))
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
      'SELECT * FROM user WHERE username = ?', (username,) ##db一致するユーザーを探すQuery
    ).fetchone()

    if user is None: ##もしユーザーが空だったら
      error = 'ユーザー名が不正です' ##
    elif not check_password_hash(user['password'], password): ##パスワードが一致しなかったら
      error = 'パスワードが違います'

    if error is None: ##もし全てerrorがなかったら
      session.clear() #sessionを初期化
      session['user_id'] = user['id'] ##このセッションにユーザーIDのセッションを持たせる
      return redirect(url_for('blog.index')) ##index.htmlにリダイレクト

    flash(error)
  
  return render_template('auth/login.html')

## 上記以降の処理でセションにユーザーID情報を持たせる
@bp.before_app_request ##要求されたurlに関係なく,view関数の前に実行される関数
def load_logged_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'SELECT * FROM user WHERE id = ?' , (user_id,)
    ).fetchone()

##ログアウト処理
@bp.route('/logout')
def logout():
  session.clear() ##sessionをクリア
  return redirect(url_for('auth.login'))

## loginが必要な処理に対してログインの情報が入手できればスルー、できない場合はログアウトさせる
def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs): ##ログイン状態のチェック kwargs = keyword args (key-valueの組み合わせで値を持つ変数)
    if g.user is None: ##もしもNoneだったら
      return redirect(url_for('auth.login')) #authで定義されている/loginに遷移

    return view(**kwargs)
  
  return wrapped_view