import sqlite3
import sys
from flask import Flask, render_template, request

s=False
currentuserid=-1

app = Flask(__name__)

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


@app.route('/login.html')
def login():
    global s
    if s:
        s=False
        return render_template('login.html', signedup=True)
    return render_template('login.html', signedup=False)


@app.route('/login.html', methods=['POST'])
def loginpost():
    username = request.form['username'] 
    processed_username = username.upper()
    print(processed_username, file=sys.stderr)
    return login()
        
@app.route('/profile.html')
def profile():
    return render_template('profile.html')


@app.route('/overview-topics.html')
def overviewtopics():
    return render_template('overview-topics.html')


@app.route('/new-post.html')
def newpost():
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
#validate that user does not exist
    
    con = get_db_connection()
    users=con.execute("SELECT * FROM users").fetchall()
    id=len(users)
    
    con.execute(f"INSERT INTO users VALUES ({id}, '{processed_username}', '{password}')")
    con.commit()
    con.close()
    s=True
    return login()
    

def get_db_connection():
    conn = sqlite3.connect('database/wb.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
    app.run(debug=True)

