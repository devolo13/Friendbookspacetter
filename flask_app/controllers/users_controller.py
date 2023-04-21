from flask_app import app
from flask import render_template, redirect, request, flash, session
from flask_app.models.user_model import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


# default page for users who aren't logged in
@app.route('/login')
@app.route('/register')
@app.route('/')
def login_page():
    return render_template('login.html')


# route for verifying user inputs, adding them to the db, then redirecting to their page
@app.route('/register_user', methods=['POST'])
def register_new_user():
    # format user inputs into the standard format
    # we get first_name, last_name, email, password, confirm_password fields
    data = {
        **request.form
    }
    # test if the users inputs were valid
    if User.validate_registration_inputs(data):
        # if user input was valid, add them to the db and redirect to their page
        data['password'] = bcrypt.generate_password_hash(data['password'])
        user = User.save(data)
        session['user_id'] = user.id
        session['user_name'] = f'{user.first_name} {user.last_name}'
        return redirect('/dashboard')
    else:
        # if user input was not valid, show errors and redirect back to registration/login page
        return redirect('/')


# route for logging in existing users and redirecting to their page
@app.route('/login_user', methods=['POST'])
def login_user():
    # format user inputs into the standard format
    # we will only get back 'email' and 'password' forms
    data = {
        'email': request.form['login_email'],
        'password': request.form['login_password']
    }
    # search for user's email in list of emails
    user = User.check_email(data['email'])
    if not user == False:
        if bcrypt.check_password_hash(user.password, data['password']):
            # password is correct. store the user's id in session and redirect them to the recipes page
            session['user_id'] = user.id
            session['user_name'] = f'{user.first_name} {user.last_name}'
            return redirect('/dashboard')
        else:
            # password is incorrect. show them an error and ask them to log in again
            flash('Incorrect password', 'login_password')
            return redirect('/')
    # that email was not found in db. show an error and send them back to the login page
    flash('Email not found', 'login_email')
    return redirect('/')


# route for updating user and redirecting to their account page
@app.route('/update_user', methods=['POST'])
def update_user():
    data = {
        **request.form,
        'id': int(request.form['id'])
    }
    if User.validate_update_inputs(data):
        User.update(data)
        session['user_name'] = f'{request.form["first_name"]} {request.form["last_name"]}'
    return redirect('/account')


# route for logging out a user and redirecting to login page
@app.route('/logout')
def log_out_a_user():
    session.clear()
    return redirect('/')
