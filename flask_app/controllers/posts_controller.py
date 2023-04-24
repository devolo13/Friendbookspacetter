from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.post_model import Post
from flask_app.models.user_model import User


# home page showing all posts
@app.route('/home')
def home_page():
    all_posts = Post.get_all()
    return render_template('home.html', all_posts=all_posts)


# search page showing results
@app.route('/search')
def search_page():
    return render_template('search.html')


# route for creating a new post and redirecting back to the page the user was on
@app.route('/add_post/<route>/<user_id>', methods=['POST'])
@app.route('/add_post/<route>', methods=['POST'])
def add_post(route, user_id = None):
    if not request.form['content'] == '':
        data = {**request.form}
        Post.save(data)
    elif request.form['content'] == '':
        flash('Post too short', 'new_post')
    if user_id == None:
        return redirect(f'/{route}')
    return redirect(f'/{route}/{user_id}')


# route for adding a lit and redirecting back to the page the user was on
@app.route('/add_lit/<int:post_id>/<route>/<user_id>')
@app.route('/add_lit/<int:post_id>/<route>')
def add_lit(post_id, route, user_id = None):
    Post.add_lit(post_id, session['user_id'])
    if user_id == None:
        return redirect(f'/{route}')
    return redirect(f'/{route}/{user_id}')


# route for adding a comment and redirecting to that post's page
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if not request.form['content'] == '':
        data = {**request.form}
        Post.add_comment(data)
    elif request.form['content'] == '':
        flash('comment cannot be empty', 'new_comment')
    return redirect(f'/post/{request.form["post_id"]}')


# page showing a single post
@app.route('/post/<int:post_id>')
def single_post_page(post_id):
    if not 'user_id' in session:
        return redirect('/')
    post = Post.get_by_id(post_id)
    comments = Post.get_all_comments(post_id)
    return render_template('post.html', post=post, comments=comments)


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
