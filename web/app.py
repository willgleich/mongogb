import os, pymongo
from flask import Flask, redirect, url_for, request, render_template, g, jsonify, flash, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os, datetime

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['SECRET_KEY'] = os.urandom(24)

#dbconfig
client = pymongo.MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.guestbook


@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('index.html', user = session.get('username'))
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not ver_password(request.form['username'], request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session['logged_in'] = True
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    session['logged_in'] = False
    session['username'] = ''
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user_doc = {
            '_id': request.form['username'],
            'name': request.form['username'],
            'password': generate_password_hash(request.form['password']),
            'email': request.form['email']
        }
        try:
            db.users.insert_one(user_doc)
        except pymongo.errors.DuplicateKeyError:
            status = '**ERROR** User with that name has already registered'
            flash(status)
            return render_template('register.html')
        status = 'Registered Successfully'
        flash(status)
        return render_template('register.html')

    return render_template('register.html')

@app.route('/posts', methods=['GET'])
def posts():
    _posts = db.posts.find()
    posts = [item for item in _posts]

    return render_template('posts.html', posts=reversed(posts))

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if not session.get('logged_in'):
        return render_template('unauthorized.html')
    if request.method == 'POST':
        flash(request.form['comment'])
        flash('Message Posted Successfully')
        post_doc = {
            'author': session['username'],
            'post': request.form['comment'],
            # 'time': datetime.datetime.now()
        }
        db.posts.insert_one(post_doc)
        redirect(url_for('posts'))
        #return render_template('posts.html')
    return render_template('create_post.html')

def ver_password(username, password):
    user = db.users.find_one({'_id': username})
    if not user or not check_password_hash(user['password'],  password):
        return False
    return True

@app.route("/getip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)