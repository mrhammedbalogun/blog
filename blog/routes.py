#from crypt import methods
from blog import app 
from flask import render_template, redirect, url_for, flash, request
from blog.models import User, Post
from blog.forms import RegistrationForm, LoginForm, CreateBlogForm
from blog import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home_page():
    title = "Home Page"
    posts = Post.query.all()
    return render_template("index.html", title=title, posts=posts)

@app.route("/<slug>")
def post_details(slug):
    post = Post.query.filter(Post.slug==slug).first()
    return render_template("post-details.html", post=post)

@app.route("/about")
def about_page():
    title = "About Page"
    return render_template("about.html", title=title)

@app.route("/contact")
def contact_page():
    title = "Contact Page"
    return render_template("contact.html", title=title)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_to_create = User(fname=form.fname.data, lname=form.lname.data, username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully. You are now loged in as {user_to_create.username}', category='success')
            
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Find below error message {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/create-blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    form = CreateBlogForm()
    if form.validate_on_submit():
        blog_to_create = Post(title=form.title.data, body=form.body.data)
        db.session.add(blog_to_create)
        db.session.commit()
        flash(f'Blog created successfully', category='success')
        return redirect(url_for('home_page'))
    
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Find below error message {err_msg}', category='danger')
     
    return render_template('create-blog.html', form=form)

@app.route('/posting', methods=['GET', 'POST'])
def posting():
    return 'we now now'




@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'You have successfully logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username or Password is incorrect', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been loged out!', category='info')
    return redirect(url_for('home_page'))