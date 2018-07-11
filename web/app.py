import os, pymongo
from flask import Flask, redirect, url_for, request, render_template, g, jsonify, flash, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os, datetime
import analytics

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['SECRET_KEY'] = os.urandom(24)

# dbconfig
client = pymongo.MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.guestbook


@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('index.html', user=session.get('username'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not ver_password(request.form['username'], request.form['password']):
            return render_template('login.html', status='IncorrectPassword')
        session['logged_in'] = True
        session['username'] = request.form['username']
        return redirect(url_for('create_post'))
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['username'] = ''
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
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
        session['logged_in'] = True
        session['username'] = request.form['username']
        return redirect(url_for('create_post'))

    return render_template('register.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        if not ver_password(session['username'], request.form['currentPassword']):
            return render_template('change_password.html', status='IncorrectPassword')
        else:
            db.users.update_one({"_id": session['username']},
                                {'$set': {"password": generate_password_hash(request.form['newPassword'])}})
            flash('Password updated')

    return render_template('change_password.html')


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
        post_doc = {
            'author': session['username'],
            'post': request.form['comment'],
            'time': datetime.datetime.now()
        }
        db.posts.insert_one(post_doc)
        return redirect(url_for('posts'))
    return render_template('create_post.html')

@app.route('/analytics/top', methods=['GET'])
def top_analytics():
    df_html = analytics.top_users_dataframe()
    return render_template('analytics/top_analytics.html', top_users = df_html)


def ver_password(username, password):
    user = db.users.find_one({'_id': username})
    if not user or not check_password_hash(user['password'], password):
        return False
    return True


@app.route("/getip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


def time_difference(then):
    '''takes in a datetime object from a previous point in time
    returns mins, seconds, hours, days, years ago
    TODO: add in later minutes and clean up this code'''
    delt = datetime.datetime.now() - then
    if delt.seconds < 60:
        return str(delt.seconds) + ' seconds ago'
    elif delt.seconds < 60 * 60:
        return str(delt.seconds // 60) + ' minutes ago'
    elif delt.seconds < 60 * 60 * 24:
        return str(delt.seconds // 3600) + ' hours ago'
    elif delt.days < 365:
        return str(delt.days) + ' days ago'
    else:
        return str(delt.days // 365) + ' years ago'


if __name__ == "__main__":
    for i in range(25,0,-1):
        analytics.populate_mongodb(minutes_ago=i)
    app.jinja_env.globals.update(time_difference=time_difference)
    app.run(host='0.0.0.0', debug=True)
