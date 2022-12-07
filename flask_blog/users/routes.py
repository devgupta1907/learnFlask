# Head over to https://hackersandslackers.com/flask-wtforms-forms/  to get some taste of wtforms

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import db, bcrypt
from flask_blog.models import User, Post
from flask_blog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm)
from flask_blog.users.utils import save_picture

users = Blueprint('users', __name__)



# registration page route
@users.route("/register", methods=['GET', 'POST'])
def register():
    # if logged in user tries to access /register route, he will be redirected to /home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # creating RegistrationForm class instance
    form = RegistrationForm()
    # if data entered is good, and request is 'POST'
    if form.validate_on_submit():
        # generate hashed version of user password and decode it in utf-8 encoding
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # adding and commiting to our db  
        db.session.add(user)
        db.session.commit()
        # flash message on screen, if account is created successfully for the user.
        flash(f'Your account has been created! You are now able to log in!', 'success')
        # redirect our new user to login page to login with their credentials
        return redirect(url_for('users.login'))
    # else, render the given template, and display the errors
    return render_template("register.html", title='Register', form=form)


# login page route
@users.route("/login", methods=['GET', 'POST'])
def login():
    # if logged in user tries to access /login route, he will be redirected to /home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # creating LoginForm class instance
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if email exists in our db and given password matched with our db,
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # then log him in. And remember him if he check the 'remember me' box.
            login_user(user, form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        # if credentials does not match, then throw a flash message.
        flash('Login Unsuccessful! Please check email and password.', 'danger')
    return render_template("login.html", title='Login', form=form)


# logout route
@users.route("/logout")
def logout():
    # this method will log out the user and riedirect hime to home.
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
    return render_template('user_posts.html', posts=posts, user=user)