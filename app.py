import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime as dt
from distutils.log import debug 
from fileinput import filename 
import os

current_user_id = -1

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for the session, replace 'your_secret_key' with a random key

def get_db_connection():
    conn = sqlite3.connect('database/wb.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

@app.route('/index.html')
def index():
    session['signed_up'] = False
    return render_template('index.html')

@app.route('/')
def root():
    session['signed_up'] = False
    return render_template('index.html')

@app.route('/overview-topics.html')
def overviewtopics():
    return render_template('overview-topics.html')

@app.route('/new-post.html', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        print(f"Form Data: {request.form}")
        title = request.form['title']
        content = request.form['content']

        print(title)
        print(content)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()

    return render_template('new-post.html')

@app.route('/overview-forum-category.html')
def overviewforumcategory():
    return render_template('overview-forum-category.html')

@app.route('/post.html')
def post():
    return render_template('post.html')

@app.route('/sign-up.html')
def signup():
    return render_template('sign-up.html')

@app.route('/sign-up.html', methods=['POST'])
def signuppost():
    username = request.form['username']
    processed_username = username.upper()
    password = request.form['password']
    date = dt.today()

    con = get_db_connection()
    users = con.execute("SELECT * FROM users").fetchall()
    current_user_id = len(users)

    con.execute(f"INSERT INTO users VALUES ({current_user_id}, '{processed_username}', '{password}', '{date}')")
    con.commit()
    con.close()

    # Set the user ID in the session upon successful signup
    session['user_id'] = current_user_id
    session['signed_up'] = True

    return login()

@app.route('/login.html')
def login():
    if session.get('signed_up', False):
        session['signed_up'] = False
        return render_template('login.html', signedup=True)
    return render_template('login.html', signedup=False)

@app.route('/login.html', methods=['POST'])
def loginpost():
    username = request.form['username']
    processed_username = username.upper()
    password = request.form['password']

    con = get_db_connection()
    user = con.execute("SELECT * FROM users WHERE username = ? AND password = ?", (processed_username, password)).fetchone()
    con.close()

    if user:
        current_user_id = user['id']

        # Set the user ID in the session upon successful login
        session['user_id'] = current_user_id
        session['signed_up'] = True

        return redirect(url_for('profile'))
    else:
        session['signed_up'] = False
        return render_template('login.html', signedup=False, login_failed=True)

@app.route('/logout')
def logout():
    # Remove the user ID from the session upon logout
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/profile.html')
def profile():
    user_id = session.get('user_id', None)

    if user_id is not None:
        con = get_db_connection()
        user = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        date = con.execute("SELECT * FROM users WHERE date = ?", (user_id,)).fetchone()
        con.close()

        return render_template('profile.html', user=user, date=date)
    else:
        return redirect(url_for('login'))
    
@app.route('/success', methods = ['POST'])   
def success():   
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(os.path.join(app.instance_path, f.filename))   
        return render_template("Acknowledgement.html", name = f.filename)   



if __name__ == '__main__':
    app.run(debug=True)
