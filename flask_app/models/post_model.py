from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask import flash


class Post:
    def __init__(self, data):
        self.id = data['id']
        self.poster_id = data['poster_id']
        self.content = data['content']
        self.poster_username = data['poster_username']
        self.lits = Post.get_lits(self.id)

    # method for adding a new post. returns that magazine's id
    # should validate content length before posting
    @classmethod
    def save(cls, data):
        # if data['content'] == '':
            # return False
        query = 'INSERT into posts (poster_id, content) values (%(poster_id)s, %(content)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        query = 'SELECT MAX(id) from posts;'
        post_id = connectToMySQL(DATABASE).query_db(query)[0]['MAX(id)']
        return post_id

    # method for getting all posts. returns a list of post objects
    @classmethod
    def get_all(cls):
        query = 'SELECT posts.id, poster_id, content, users.username as poster_username from posts LEFT JOIN users on users.id = posts.poster_id;'
        results = connectToMySQL(DATABASE).query_db(query)
        all_posts = []
        for post in results:
            all_posts.append(cls(post))
        return all_posts

    # method for getting a single post by it's id. returns post object
    @classmethod
    def get_by_id(cls, id):
        data = {'id': int(id)}
        query = 'SELECT posts.id, poster_id, content, users.username as poster_name from posts LEFT JOIN users on users.id = posts.poster_id WHERE posts.id = %(id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        return cls(results[0])

    # method for getting all posts by poster_id. returns a list of post objects
    @classmethod
    def get_by_uploader(cls, user_id):
        data = {'user_id': int(user_id)}
        query = 'SELECT posts.id, poster_id, content, users.username as poster_username from posts LEFT JOIN users on users.id = posts.poster_id WHERE users.id = %(user_id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        all_posts = []
        for post in results:
            all_posts.append(cls(post))
        return all_posts

    # method for determining how many lit a post has. returns number of lits
    # BROKEN. DON'T KNOW WHAT GETS RETURNED IF THERE ARE NO LITS
    @staticmethod
    def get_lits(post_id):
        data = {'post_id': int(post_id)}
        query = 'SELECT count(user_id) FROM fires WHERE post_id = %(id)s GROUP BY post_id;'
        lits = int(connectToMySQL(DATABASE).query_db(query, data)[0]['count(user_id)'])
        # lits = connectToMySQL(DATABASE).query_db(query, data)
        # if lits == {}:
        #     return 0
        return lits

    # method for adding a user to another user's friends. returns nothing
    @classmethod
    def add_subscriber(cls, user_id, friend_id):
        data = {
            'user_id': user_id,
            'friend_id': friend_id
        }
        query = 'INSERT into friendships (user_id, friend_id) VALUES (%(user_id)s, %(friend_id)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        return

    # method for validating magazine creation. returns True if valid, False if invalid. creates flash messages along the way
    @staticmethod
    def validate(data):
        valid_inputs = True
        # validate title length
        if (len(data['title']) < 2):
            flash('Magazine title must be at least 2 characters', 'title')
            valid_inputs = False
        # validate description length
        if (len(data['description']) < 10):
            flash('Magazine description must be at least 10 characters', 'description')
            valid_inputs = False
        return valid_inputs

    # method for deleting a recipe
    @classmethod
    def delete(cls, id):
        data = {'id': id}
        query = 'DELETE from magazines where id = %(id)s;'
        connectToMySQL(DATABASE).query_db(query, data)
        return

    # method for determining how many lits a post has
    # untested
    @staticmethod
    def lits_by_post_id(id):
        data = {'post_id': int(id)}
        query = 'SELECT count(user_id) FROM fires WHERE post_id = %(id)s GROUP BY post_id;'
        result = connectToMySQL(DATABASE).query_db(query, data)
        return int(result)
