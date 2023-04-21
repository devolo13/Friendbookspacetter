from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask import flash


class Post:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.uploader_name = data['uploader_name']
        self.uploader_id = data['uploader_id']

    # method for getting all magazines. returns a list of magazine objects
    @classmethod
    def get_all(cls):
        query = 'SELECT magazines.id, uploader_id, title, description, concat(users.first_name, " ", users.last_name) as uploader_name from magazines LEFT JOIN users on users.id = magazines.uploader_id;'
        results = connectToMySQL(DATABASE).query_db(query)
        magazines_list = []
        for magazine in results:
            magazines_list.append(cls(magazine))
        return magazines_list

    # method for getting a single magazine by it's id. returns magazine object
    @classmethod
    def get_by_id(cls, id):
        data = {'id': int(id)}
        query = 'SELECT magazines.id, uploader_id, title, description, concat(users.first_name, " ", users.last_name) as uploader_name from magazines LEFT JOIN users on users.id = magazines.uploader_id WHERE magazines.id = %(id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        return cls(results[0])

    # method for getting all magazines by uploader_id. returns a list of magazine objects
    @classmethod
    def get_by_uploader(cls, user_id):
        print('getting magazines by uploader')
        data = {'user_id': user_id}
        query = 'SELECT magazines.id, uploader_id, title, description, concat(users.first_name, " ", users.last_name) as uploader_name from magazines LEFT JOIN users on users.id = magazines.uploader_id WHERE magazines.uploader_id = %(user_id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        magazines_list = []
        for magazine in results:
            magazines_list.append(cls(magazine))
        return magazines_list

    # method for getting all people who have subscribed to a magazine. returns a list with user names
    @classmethod
    def get_subscribers(cls, id):
        data = {'id': int(id)}
        query = 'SELECT concat(users.first_name, " ", users.last_name) as subscriber_name from magazines LEFT JOIN subscribers on subscribers.magazine_id = magazines.id LEFT JOIN users on users.id = subscribers.user_id WHERE magazines.id = %(id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        return results

    # method for determining if a user is subscribed to a magazine. returns list of magazine id's the user is subscribed to
    @classmethod
    def get_subscribed_mags(cls, user_id):
        data = {'user_id': user_id}
        query = 'SELECT magazine_id from subscribers WHERE user_id = %(user_id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        magazines = []
        for index in range(len(results)):
            magazines.append(results[index]['magazine_id'])
        return magazines

    # method for adding a user to a magazine's subscribers. returns nothing
    @classmethod
    def add_subscriber(cls, user_id, magazine_id):
        data = {
            'user_id': user_id,
            'magazine_id': magazine_id
        }
        query = 'INSERT into subscribers (user_id, magazine_id) VALUES (%(user_id)s, %(magazine_id)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        return

    # method for adding a new magazine. returns that magazine's id
    @classmethod
    def save(cls, data):
        query = 'INSERT into magazines (title, uploader_id, description) values (%(title)s, %(uploader_id)s, %(description)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        query = 'SELECT MAX(id) from magazines;'
        magazine_id = connectToMySQL(DATABASE).query_db(query)[0]['MAX(id)']
        return magazine_id

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
