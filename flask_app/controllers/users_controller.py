from flask_app import app
from flask import render_template, redirect, request, flash, session
from flask_app.models.user_model import User
from flask_app.models.post_model import Post
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
        session['theme'] = user.theme
        return redirect('/home')
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
            session['theme'] = user.theme
            return redirect('/home')
        else:
            # password is incorrect. show them an error and ask them to log in again
            flash('Incorrect password', 'login_password')
            return redirect('/')
    # that email was not found in db. show an error and send them back to the login page
    flash('Email not found', 'login_email')
    return redirect('/')


# route for updating user and redirecting to their account page
@app.route('/update_user_settings', methods=['POST'])
def update_user():
    data = {
        **request.form,
        'id': session['user_id']
    }
    if User.validate_update_inputs(data):
        user = User.update(data)
        session['theme'] = user.theme
    return redirect(f'/profile/{session["user_id"]}')


# template for user's profile page
@app.route('/profile/<int:id>')
def profile_template(id):
    if not 'user_id' in session:
        return redirect('/')
    user = User.get_by_id(id)
    friends = User.get_friends(session['user_id'])
    all_posts = Post.get_by_uploader(id)
    if not all_posts == []:
        interactions = 0
        popular_post = all_posts[0]
        for post in all_posts:
            if (post.comments + post.lit_count) > interactions:
                interactions = post.comments + post.lit_count
                popular_post = post
        return render_template('profile.html', user=user, all_posts=all_posts, popular_post=popular_post, friends=friends)
    return render_template('profile.html', user=user, all_posts=None, popular_post=None, friends=friends)


# template for a user's settings page
@app.route('/settings')
def user_settings():
    if not 'user_id' in session:
        return redirect('/')
    user = User.get_by_id(session['user_id'])
    return render_template('settings.html', user=user)


# template for showing a user's friends
@app.route('/friends')
def friends_page():
    if not 'user_id' in session:
        return redirect('/')
    friends_ids = User.get_friends(session['user_id'])
    friends = []
    for friend_index in range(len(friends_ids)):
        friends.append(User.get_by_id(friends_ids[friend_index]))
    return render_template('friends_list.html', friends=friends)


# route for adding a friend and return to the previous page
@app.route('/add_friend/profile/<int:friend_id>')
def add_friend(friend_id):
    data = {
        'user_id': session['user_id'],
        'friend_id': friend_id
    }
    User.add_friend(data)
    return redirect(f'/profile/{friend_id}')


# route for unfriending/unfollowing a user and returning to the friends page
@app.route('/unfriend/<int:friend_id>')
@app.route('/unfollow/<int:friend_id>')
def remove_friend(friend_id):
    data = {
        'user_id': session['user_id'],
        'friend_id': friend_id
    }
    User.remove_friend(data)
    return redirect('/friends')


# route for deleting a user and redirecting to register page
@app.route('/delete_user')
def delete_user():
    user_id = session['user_id']
    User.delete_user(user_id)
    return redirect('/')


# route for logging out a user and redirecting to login page
@app.route('/signout')
@app.route('/sign_out')
@app.route('/logout')
def log_out_a_user():
    session.clear()
    return redirect('/')
