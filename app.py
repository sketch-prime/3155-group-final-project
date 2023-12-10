import datetime
import os
import sqlite3, secrets
import sqlite3, secrets
from flask import Flask, render_template, request, redirect, url_for, session
from distutils.log import debug 
from fileinput import filename 
from datetime import datetime as dt

current_user_id = -1

app = Flask(__name__)
secret_key = secrets.token_urlsafe(32)
app.secret_key = secret_key 

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
            author_id INTEGER,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


create_table()

def get_posts():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch posts from the database
    cursor.execute('''
        SELECT posts.id, posts.title, posts.content, posts.category, posts.author_id, users.username
        FROM posts
        JOIN users ON posts.author_id = users.id
    ''')    
    posts = cursor.fetchall()

    conn.close()
    return posts

def get_post(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch posts from the database
    cursor.execute('''
        SELECT posts.id, posts.title, posts.content, posts.category, posts.author_id, users.username
        FROM posts
        JOIN users ON posts.author_id = users.id
        WHERE posts.id = ?
    ''', (id,))    
    post = cursor.fetchone()

    conn.close()
    return post

@app.route('/index.html')
def index():

    session['signed_up'] = False
    posts = get_posts()
    u=''
    if 'username' in session.keys():
        u=session['username']
    return render_template('index.html', items=posts, username=u)

@app.route('/')
def root():
    session['signed_up'] = False
    posts = get_posts()
    return render_template('welcome.html', items=posts)

@app.route('/overview-topics.html')
def overviewtopics():
    return render_template('overview-topics.html')

@app.route('/new-post.html', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        # Retrieve the currently logged-in user's ID
        author_id = current_user_id

        title = request.form['title']
        content = request.form['content']
        category = request.form['category']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert post with the author's ID
        cursor.execute("INSERT INTO posts (author_id, title, content, category) VALUES (?, ?, ?, ?)",
                       (author_id, title, content, category))

        conn.commit()
        conn.close()

    return render_template('post.html')

@app.route('/overview-forum-category.html')
def overviewforumcategory():
    return render_template('overview-forum-category.html')


@app.route('/post.html/<int:pid>')
def post(pid=None):
    conn = get_db_connection()
    cursor=conn.cursor()
    post = cursor.execute(f"SELECT * FROM posts WHERE id={pid}").fetchone()
    conn.commit()
    return render_template('post.html', post=post)

pid = '/pid'
app.add_url_rule(pid, 'post', post)

@app.route('/sign-up.html')
def signup():
    return render_template('sign-up.html')

@app.route('/sign-up.html', methods=['POST'])
def signuppost():
    global current_user_id  # Declare current_user_id as a global variable

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
    global current_user_id  # Declare current_user_id as a global variable

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
        session['username'] = username
        return redirect(url_for('profile'))
    else:
        session['signed_up'] = False
        return render_template('login.html', signedup=False, login_failed=True)

@app.route('/logout')
def logout():
    # Remove the user ID and any other session variables upon logout
    session.clear()
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

    
@app.route('/success', methods = ['GET', 'POST'])   
def success():   
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(os.path.join(app.instance_path, f.filename))   
        fpath = "/instance/" + f.filename
        print(fpath)
        testuser = 6
        print(testuser)
        con = get_db_connection()
        users = con.execute("SELECT * FROM users").fetchall()
        con.execute("UPDATE users SET resume = ? WHERE id = ?", (fpath, testuser))
        con.close()

        return render_template("Acknowledgement.html", name = f.filename)   

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')


@app.route('/view-post/<int:id>')
def view_post(id):
    post = get_post(id)
    print(id)
    return render_template('view-post.html', post=post)

    if query:
        con = get_db_connection()
        cursor = con.cursor()

        # Example query: Find posts containing the search query in title or content
        cursor.execute("SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?", ('%' + query + '%', '%' + query + '%'))

        search_results = cursor.fetchall()

        con.close()

        return render_template('search_results.html', query=query, results=search_results)
    else:
        return render_template('search_results.html', query=None, results=None)


if __name__ == '__main__':
    app.run(debug=True)
