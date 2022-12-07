from flask import Flask
from flask_sqlalchemy import SQLAlchemy   # database
from flask_bcrypt import Bcrypt           # password hashing
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bb372be0acc802e3bd829892d1059e41'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# db instance initialization
db = SQLAlchemy(app)

# bcrypt instance initialization
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

# importing and registering blueprints
from flask_blog.users.routes import users
from flask_blog.posts.routes import posts
from flask_blog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
