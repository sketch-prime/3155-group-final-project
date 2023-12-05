import sqlite3
import sys
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime as dt

s=False
currentuserid=-1

app = Flask(__name__)

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
    global s
    s=False
    return render_template('index.html')

@app.route('/')
def root():
    global s
    s=False
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
    global s
    username = request.form['username']
    processed_username = username.upper()
    password = request.form['password']
    date = dt.today()
    print(date)
#validate that user does not exist
    
    con = get_db_connection()
    users=con.execute("SELECT * FROM users").fetchall()
    id=len(users)
    
    con.execute(f"INSERT INTO users VALUES ({id}, '{processed_username}', '{password}', '{date}')")
    con.commit()
    con.close()
    s=True
    return login()



@app.route('/login.html')
def login():
    global s
    if s:
        s = False
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
        global s, currentuserid
        s = True
        currentuserid = user['id']
        return redirect(url_for('profile'))
    else:
        return render_template('login.html', signedup=False, login_failed=True)


@app.route('/profile.html')
def profile():
    user_id = currentuserid  # Use the global current_user_id variable

    if user_id != -1:
        con = get_db_connection()
        user = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        date = con.execute("SELECT * FROM users WHERE date = ?", (user_id,)).fetchone()
        con.close()

        return render_template('profile.html', user=user, date=date)
    else:
        return redirect(url_for('login'))  # Corrected redirect here


if __name__ == '__main__':
    app.run(debug=True)