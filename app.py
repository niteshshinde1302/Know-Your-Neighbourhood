from cffi.setuptools_ext import execfile
from flask import Flask, render_template, request, jsonify, session, redirect, escape, url_for

import lib.Users as Users, lib.Block_Details as Block_Details
import mysql.connector


app = Flask(__name__)


class ServerError(Exception): pass


class DB:
    conn = None

    def connect(self):
        #config = {}
        execfile("config.conf.new", config)

        self.conn = mysql.connector.connect(user='root', password='', host='localhost', database='nextdoor')
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        #self.conn.set_character_set('utf8')

    def query(self, sql, args=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, '')
        except (AttributeError, mysql.connector.Error):
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql, args)
        return cursor


if __name__ == '__main__':
    config = {}
    execfile("config.conf.new", config)
    app.secret_key = config['app_key']
    db = DB()
    notifications = None


# Routes
@app.route('/')
def index():

    message = None
    global notifications
    if notifications:
        message = notifications
        notifications = None
    if 'username' not in session:
        message = {'message': 'Please log in', 'type': 'warning'}
        return redirect(url_for('login'))
    res = Users.getUserBlockLinkInfo(db)
    res = int(0) if res == "Failed" else res
    blocks = Block_Details.getblock_info(db)

    return render_template('index.html', session=session, message=message, blocks=blocks, blockId=int(res))

@app.route('/joinBlock/<int:blockId>')
def joinBlock_Request(blockId):
    message = None
    global notifications
    if notifications:
        message = notifications
        notifications = None
    if 'username' not in session:
        message = {'message': 'Please log in', 'type': 'warning'}
        return redirect(url_for('login'))
    resp = Block_Details.joinBlock_Request(db, blockId)
    return index()

@app.route('/profile',methods=['GET','POST'])
def profile():
    message = None
    global notifications
    if notifications:
        message = notifications
        notifications = None
    if 'uid' not in session:
        return redirect(url_for('login'))

    result = Users.userprofile(db, request.form)
    print (result[0])
    return render_template('userprofile.html', data=result[0])

@app.route('/changepassword', methods=['GET','POST'])
def changepassword():
    print('in change password function')
    #result = Users.changepassword(db.conn, None)
    if request.method == 'POST':
        result = Users.changepassword(db, request.form)
        result1 = Users.userprofile(db, request.form)
        if not result:
            message = {'message': 'Username/Password Changed', 'type': 'success'}
            return render_template('userprofile.html', data=result1[0], message=message)
        else:
            message = {'message': 'Username/Password change Failed', 'type': 'error'}
            return render_template('userprofile.html', data=result1[0], message=message)
        return render_template('userprofile.html', data=result1[0])
    return render_template('changepwd.html')

@app.route('/users')
def users():
    message = None
    global notifications
    if notifications:
        message = notifications
        notifications = None
    if 'username' not in session:
        notifications = {'message': 'Please log in', 'type': 'warning'}
        return redirect(url_for('login'))
    #if session['username'] != 'admin':
        #return redirect(url_for('index', message="Admin only page"))

    users = Users.getUsers(db)
    if not users:
        notifications = {'message': 'Failed to retrieve users', 'type': 'error'}
        return render_template('users.html', message=message)
    return render_template('users.html', users=users, message=message)


@app.route('/users/edit/<user>')
def editUser(user):
    return "ToDo"


@app.route('/users/delete/<user>')
def delUser(user):
    global notifications
    if 'username' not in session:
        notifications = {'message': 'Please log in', 'type': 'warning'}
        return redirect(url_for('login'))
    if session['username'] != 'admin':
        notifications = {'message': 'Admin only page', 'type': 'error'}
        return redirect(url_for('index'))

    result = Users.deleteUser(db, user)
    if not result:
        notifications = {'message': 'User deleted successfully', 'type': 'success'}
        return redirect(url_for('users', message="User deleted successfully"))
    notifications = {'message': 'Something went wrong: ' + result, 'type': 'error'}
    return redirect(url_for('users', message="Something went wrong: " + result))


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    global notifications
    if notifications:
        message = notifications
        notifications = None
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        result = Users.loginForm(db, request.form)
        if not result:
            notifications = {'message': 'Logged in', 'type': 'success'}
            return redirect(url_for('index'))
        else:
            message = {'message': 'Failed to log in', 'type': 'error'}
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    global notifications
    if 'username' not in session:
        return redirect(url_for('login'))
    session.pop('username', None)
    notifications = {'message': 'Logged out', 'type': 'success'}
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    global notifications
    if notifications:
        message = notifications
        notifications = None
    if request.method == 'POST':
        result = Users.registerUser(db, request.form, config['pw_rounds'])
        print(result)
        if not result:
            notifications = {'message': 'Registration successful', 'type': 'success'}
            #if session['username'] == 'admin':
                #return redirect(url_for('register'))
            #else:
            return redirect(url_for('login'))
        else:
            message = {'message': 'Something went wrong: ' + result, 'type': 'error'}
            return render_template('register.html', message=message)
    if 'username' in session :#and session['username'] == 'admin':
        return render_template('register.html', message=message)
    if config['registration_enabled']:
        return render_template('register.html', message=message)
    else:
        notifications = {'message': 'User registration is disabled by the admin', 'type': 'warning'}
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))


# Run app
if __name__ == '__main__':
    if config['ssl']:
        context = (config['ssl_crt'], config['ssl_key'])
        app.run(
            host=config['server_ip'],
            port=config['server_port'],
            ssl_context=context,
            debug=config['debug']
        )
    else:
        app.run(
            host=config['server_ip'],
            port=config['server_port'],
            debug=config['debug']
        )
