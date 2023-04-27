from flask import Flask
from secret_key import secret_key

app = Flask(__name__)
# in secret_key.py is secret_key = 'some random string thing'
app.secret_key = secret_key

DATABASE = 'social_media_schema'