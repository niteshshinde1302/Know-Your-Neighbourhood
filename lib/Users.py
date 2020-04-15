import sys

from flask import Flask, render_template, request, jsonify, session, redirect, escape, url_for
from datetime import datetime
import bcrypt
from getpass import getpass

class ServerError(Exception): pass

def loginForm(db, form):
    # logging.info('Users login')
    # error = None
    try:
        username = form['username']
        cur = db.query("SELECT COUNT(1) FROM SignUp_Details WHERE username = %s", [username])
        if not cur.fetchone()[0]:
            raise ServerError('Incorrect username / password')

        password = form['password']
        cur = db.query("SELECT pwd FROM SignUp_Details WHERE username = %s;", [username])

        salt = hashlib.sha256().hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        password = (salt + pwdhash).decode('ascii')
        print("Password:", password)

        cur2 = db.query("SELECT uid FROM SignUp_Details WHERE username = %s", [username])
        uid = cur2.fetchone()[0]
        for row in cur.fetchall():
            print("row   :  ", row[0])
            if password == row[0]:
                session['uid'] = uid
                print("password match")
                return None

        raise ServerError('Incorrect username / password')
    except ServerError as e:
        error = str(e)
        return error

def editprofile(db, form):
    error = None
    try:
        dict = []
        uid = session['uid']
        fname = form['fname']
        lname = form['lname']
        # username = form['username']
        email = form['email']
        apt = form['apt']
        phone = form['phone']
        street = form['street']
        city = form['city']
        state = form['state']
        zip = form['zip']
        intro = form['intro']
        block = form['blockID']
        email_preference = form['emailpref']
        if email_preference == 1 or email_preference.upper()[0] == 'Y':
            email_preference = 1
        else:
            email_preference = 0
        print(email_preference)

        cur = db.query(
            "UPDATE User_Info SET fname=%s, lname=%s, email=%s, apt_num=%s, phone_num=%s, street=%s, city=%s, state=%s, zip_code=%s, intro=%s, block_id=%s , email_preference=%s where uid=%s;",
            [fname, lname, email, apt, phone, street, city, state, int(zip), intro, block, int(email_preference),
             int(uid)])
        dict.append(
            {'fname': fname, 'lname': lname, 'email': email, 'phone_num': phone, 'apt_num': apt, 'street': street,
             'city': city, 'state': state, 'zip_code': zip, 'block_id': block, 'intro': intro,
             "email_preference": email_preference})
        return userprofile(db, form)
    except ServerError as e:
        error = str(e)
        return error

def userprofile(db, form):
    error = None
    try:
        uid = session['uid']
        dict = []
        # print(uid)
        cur = db.query(
            "SELECT fname,lname,email,phone_num,apt_num,street,city,state,zip_code,block_id,intro,email_preference,photo FROM User_Info WHERE uid = %s;",
            [uid])
        c = cur.fetchone()
        print("C : ", c[12])
        dict.append({'fname': c[0], 'lname': c[1], 'email': c[2], 'phone_num': c[3], 'apt_num': c[4], 'street': c[5],
                     'city': c[6], 'state': c[7], 'zip_code': c[8], 'block_id': c[9], 'intro': c[10],
                     'email_preference': c[11], 'photo': c[12].decode('utf-8')})
        return dict
    except ServerError as e:
        error = str(e)
        return error

def getUsers(db):
    error = None
    try:
        userlist = []
        cur = db.query("SELECT user, email FROM users")
        for row in cur.fetchall():
            userlist.append({'name': row[0], 'email': row[1]})
        return userlist
    except:
        error = "Failed"
        return error

def changepassword(db, form):
    error = None
    try:
        uid = int(session['uid'])
        username=form['username']
        opwd = form['opwd']
        pwd = form['pwd']
        cpwd = form['confirmpwd']
        args = ([uid])
        print(args)
        cur = db.query("SELECT username,pwd from SignUp_Details where uid=%s;", args)
        c = cur.fetchone()
        print(c)

        salt = hashlib.sha256().hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', opwd.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        originalpassword = (salt + pwdhash).decode('ascii')


        if originalpassword==c[1]:
            if pwd==cpwd:
                salt = hashlib.sha256().hexdigest().encode('ascii')
                pwdhash = hashlib.pbkdf2_hmac('sha512', pwd.encode('utf-8'), salt, 100000)
                pwdhash = binascii.hexlify(pwdhash)
                password = (salt + pwdhash).decode('ascii')
                print("New password : ",password)
                cur = db.query("UPDATE SignUp_Details set username=%s, pwd=%s where uid=%s", [username, password,uid])
            else:
                print('Passwords don\'t match')
                raise ServerError('Passwords don\'t match')
        else:
            print('Incorrect Original Password')
            raise ServerError('Original Password incorrect')
    except ServerError as e:
        error = str(e)
        return error

def registerUser(db, form):
    error = None
    try:
        fname = form['fname']
        lname = form['lname']
        username = form['username']
        password = form['password']
        email = form['email']
        apt = form['apt']
        phone = form['phone']
        street = form['street']
        city = form['city']
        state = form['state']
        zip = form['zip']
        intro = form['intro']
        if request.form.get('emailpref'):
            emailpref = 1
        else:
            emailpref = 0

        if not username:
            raise ServerError('Enter Username')
        if not password:
            raise ServerError('Enter Password')
        if not email:
            raise ServerError('Enter Email')
        if not fname:
            raise ServerError('Enter fname')
        if not lname:
            raise ServerError('Enter lname')
        if not phone:
            raise ServerError('Enter phone')
        if not apt:
            raise ServerError('Enter apt')
        if not street:
            raise ServerError('Enter street')
        if not city:
            raise ServerError('Enter city')
        if not state:
            raise ServerError('Enter state')
        if not zip:
            raise ServerError('Enter zip')
        if not intro:
            raise ServerError('Enter intro')

        salt = hashlib.sha256().hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        password = (salt + pwdhash).decode('ascii')
        # password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(ROUNDS))

        cur = db.query("SELECT COUNT(*) FROM SignUp_Details WHERE username = %s", [username])
        c = cur.fetchone()
        # print("Password : ",password)
        if c[0] == 0:
            cur = db.query("INSERT INTO SignUp_Details (`username`, `pwd`, `signuptime`) VALUES (%s,%s,NOW())",
                           [username, password])

            cur = db.query("SELECT uid FROM SignUp_Details WHERE username = %s", [username])
            uid = cur.fetchone()[0]

            cur = db.query(
                "INSERT INTO User_Info (`uid`,`fname`,`lname`,`email`,`phone_num`,`apt_num`,`street`,`city`,`state`,`zip_code`,`intro`,`email_preference`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [int(uid), fname, lname, email, phone, apt, street, city, state, int(zip), intro, emailpref])

            return None
        else:
            return "User exists"
    except ServerError as e:
        error = str(e)
        return error

def deleteUser(db, user):
    error = None
    try:
        cur = db.query("DELETE FROM users WHERE user = %s", [user])
        return None
    except:
        return "Failed"

def getUserBlockLinkInfo(db):
	error = None
	try:
		print('inside get user block info function')
		userName = str(session['username'])
		print(userName)
		args = [userName, '@Bid']
		res = db.cursor.callproc('Get_User_Block_Infor', args)
		print(res[1])
		if res[1] is None:
			return 0

		print(res[1])
		return res[1]
	except IOError as err:
		print("I/O error: {0}".format(err))
	except ValueError:
		print("Could not convert data to an integer.")
	except:
		print("Unexpected error:", sys.exc_info()[0])
		error = "Failed"
		return error