from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models.magazine_model import Magazine
from flask_app.models.user_model import User


# dashboard page showing all magazines
@app.route('/dashboard')
def dashboard():
    if not 'user_id' in session:
        return redirect('/')
    user_id = session['user_id']
    user_name = session['user_name']
    magazines = Magazine.get_all()
    subscribed_magazines = Magazine.get_subscribed_mags(user_id)
    return render_template('all_magazines.html', user_id=user_id, user_name=user_name, magazines=magazines, subscribed_magazines=subscribed_magazines)


# page showing a single magazine
@app.route('/show/<int:mag_id>')
def single_mag_page(mag_id):
    if not 'user_id' in session:
        return redirect('/')
    user_id = session['user_id']
    user_name = session['user_name']
    magazine = Magazine.get_by_id(mag_id)
    subscribers = Magazine.get_subscribers(mag_id)
    print(subscribers)
    return render_template('single_magazine.html', user_id=user_id, user_name=user_name, magazine=magazine, subscribers=subscribers)


# route for creating a new magazine
@app.route('/add_magazine', methods=['POST'])
def add_magazine():
    data = {
        **request.form,
        'uploader_id': session['user_id'],
        'uploader_name': session['user_name']
    }
    if Magazine.validate(data):
        Magazine.save(data)
        return redirect('/dashboard')
    return redirect('/new')


# template for adding a new magazine
@app.route('/new')
def new_magazine_template():
    if not 'user_id' in session:
        return redirect('/')
    return render_template('add_magazine.html')


# template for user's account page
@app.route('/account')
def account_template():
    if not 'user_id' in session:
        return redirect('/')
    user_id = int(session['user_id'])
    user = User.get_by_id(user_id)
    magazines = Magazine.get_by_uploader(user_id)
    subs = {}
    for magazine in magazines:
        subs[magazine.title] = len(Magazine.get_subscribers(magazine.id))
    return render_template('account.html', user=user, magazines=magazines, subs=subs)


# route for deleting a magazine and redirecting to user's account page
@app.route('/delete/<int:mag_id>')
def delete_magazine(mag_id):
    if not 'user_id' in session:
        return redirect('/')
    Magazine.delete(mag_id)
    return redirect('/account')


# route for subscribing a user to a magazine
@app.route('/subscribe/<int:mag_id>')
def subscribe(mag_id):
    user_id = int(session['user_id'])
    Magazine.add_subscriber(user_id, mag_id)
    return redirect('/dashboard')
