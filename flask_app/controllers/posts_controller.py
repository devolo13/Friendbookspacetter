from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.post_model import Post
from flask_app.models.user_model import User
from datetime import date


# home page showing all posts
@app.route('/home', methods=["POST", "GET"])
def home_page():
    # organizing and sanitizing sorting options
    sort = {**request.form}
    if not 'user_id' in session:
        session['theme'] = 'dark'
        sort = {
            'sort': 'chronological',
            'show_time': 'week',
            'show_celebrities': 'true'
        }
    if not 'sort' in sort:
        sort['sort'] = 'chronological'
    if not 'show_time' in sort:
        sort['show_time'] = 'all'
    if not 'show_friends' in sort and not 'show_friends_of_friends' in sort and not 'show_celebrities' in sort and not 'show_everyone' in sort:
        sort['show_everyone'] = 'true'
    query = 'SELECT posts.id, posts.poster_id, posts.content, users.username as poster_username, posts.created_at, posts.updated_at from posts LEFT JOIN users on users.id = posts.poster_id'
    posts = []
    # time filter
    today = date.today()
    if sort['show_time'] == 'today':
        if today.day == 1:
            if today.month == 1:
                yesterday = today.replace(day=31, month=12, year=today.year-1)
            elif (today.month == 3 or today.month == 5 or today.month == 7 or today.month == 8 or today.month == 10 or today.month == 12):
                yesterday = today.replace(month=today.month-1, day=31)
            elif (today.month == 2):
                yesterday = today.replace(month=today.month-1, day=28)
            else:
                yesterday = today.replace(month=today.month-1, day=30)
        else:
            yesterday = today.replace(day=today.day-1)
        time_filter = f' and posts.created_at > "{yesterday}"'
    elif sort['show_time'] == 'week':
        if today.day < 8:
            if today.month == 1:
                last_week = today.replace(
                    day=31-7+today.day, month=12, year=today.year-1)
            elif (today.month == 3 or today.month == 5 or today.month == 7 or today.month == 8 or today.month == 10 or today.month == 12):
                last_week = today.replace(
                    month=today.month-1, day=31-7+today.day)
            elif (today.month == 2):
                last_week = today.replace(
                    month=today.month-1, day=28-7+today.day)
            else:
                last_week = today.replace(
                    month=today.month-1, day=30-7+today.day)
        else:
            last_week = today.replace(day=today.day-7)
        time_filter = f' and posts.created_at > "{last_week}"'
    elif sort['show_time'] == 'month':
        if today.month == 1:
            last_month = today.replace(year=today.year-1, month=12)
        else:
            last_month = today.replace(month=today.month-1)
        time_filter = f' and posts.created_at > "{last_month}"'
    elif sort['show_time'] == 'all':
        time_filter = ' and 2=2'
    # users filter
    if 'show_everyone' in sort:
        users_filter = ' WHERE 1=1'
        posts = posts + \
            Post.get_with_filters(query=query+users_filter+time_filter+';')
    else:
        if 'show_friends' in sort:
            users_filter = f' LEFT JOIN friendships on poster_id = friendships.friend_id WHERE friendships.user_id = {session["user_id"]} and users.celebrity = "no"'
            posts = posts + \
                Post.get_with_filters(query=query+users_filter+time_filter+';')
        if 'show_friends_of_friends' in sort:
            users_filter = f' LEFT JOIN friendships as friends_of_friends on poster_id = friends_of_friends.friend_id LEFT JOIN friendships as friends on friends_of_friends.user_id = friends.friend_id WHERE friends.user_id = {session["user_id"]} and users.celebrity = "no"'
            posts = posts + \
                Post.get_with_filters(query=query+users_filter+time_filter+';')
        if 'show_celebrities' in sort:
            users_filter = ' WHERE users.celebrity = "yes"'
            posts = posts + \
                Post.get_with_filters(query=query+users_filter+time_filter+';')
    # remove duplicates
    posts = [*set(posts)]
    # sort order
    if sort['sort'] == 'chronological':
        posts.sort(key=lambda x: x.created_at, reverse=True)
    elif sort['sort'] == 'lit':
        posts.sort(key=lambda x: x.lit_count, reverse=True)
    elif sort['sort'] == 'comments':
        posts.sort(key=lambda x: x.comments, reverse=True)
    elif sort['sort'] == 'ratio':
        posts.sort(key=lambda x: x.ratio, reverse=True)
    return render_template('home.html', sort=sort, all_posts=posts)


# search page showing results
@app.route('/search/<string>')
def search_page(string, posts=[]):
    if not 'user_id' in session:
        return redirect('/')
    posts = Post.search_posts(string)
    users = User.search_users(string)
    return render_template('search.html', posts=posts, users_list=users, query=string)


# search template page
@app.route('/search', methods=["POST", 'GET'])
def search_template():
    if not 'user_id' in session:
        return redirect('/')
    if 'search' in request.form:
        if not request.form['search'] == '':
            string = request.form['search']
            return redirect(f'/search/{string}')
    return render_template('search.html')


# route for creating a new post and redirecting back to the page the user was on
@app.route('/add_post/<route>/<user_id>', methods=['POST'])
@app.route('/add_post/<route>', methods=['POST'])
def add_post(route, user_id=None):
    if not request.form['content'] == '':
        if len(request.form['content']) >= 240:
            flash('Post too long', 'new_post')
        else:
            data = {**request.form}
            Post.save(data)
    elif request.form['content'] == '':
        flash('Post too short', 'new_post')
    if user_id == None:
        return redirect(f'/{route}')
    return redirect(f'/{route}/{user_id}')


# route for editing a post and redirecting to that post's page
@app.route('/edit_post/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    post = Post.get_by_id(post_id)
    if session['user_id'] == post.poster_id:
        data = {
            **request.form,
            'id': post_id
        }
        if data['content'] == '':
            flash('Post too short', 'post')
        elif len(data['content']) >= 240:
            flash('Post too long', 'post')
        else:
            Post.update(data)
    return redirect(f'/post/{post_id}')


# route to delete a post
@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    if session['user_id'] == post.poster_id:
        Post.delete(post_id)
        return redirect('/home')
    return redirect(f'/post/{post_id}')


# route for adding a lit and redirecting back to the page the user was on
@app.route('/add_lit/<int:post_id>/<route>/<user_id>')
@app.route('/add_lit/<int:post_id>/<route>')
def add_lit(post_id, route, user_id=None):
    Post.add_lit(post_id, session['user_id'])
    if user_id == None:
        return redirect(f'/{route}')
    return redirect(f'/{route}/{user_id}')


# route for adding a comment and redirecting back to that post's page
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if request.form['content'] == '':
        flash('comment cannot be empty', 'new_comment')
    elif len(request.form['content']) >= 240:
        flash('comment too long', 'new_comment')
    else:
        data = {**request.form}
        Post.add_comment(data)
    return redirect(f'/post/{request.form["post_id"]}')


# page showing a single post
@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def single_post_page(post_id):
    if not 'user_id' in session:
        return redirect('/')
    post = Post.get_by_id(post_id)
    comments = Post.get_all_comments(post_id)
    return render_template('post.html', post=post, comments=comments)
