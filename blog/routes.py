#from crypt import methods
from blog import app 
from flask import render_template, redirect, url_for, flash, request
from blog.models import User, Post
from blog.forms import RegistrationForm, LoginForm, CreateBlogForm, UpdateBlogForm
from blog import db
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc


@app.route("/")
@app.route("/home")
def home_page():
    title = "Home Page"
    posts = Post.query.order_by(desc(Post.created))
    return render_template("index.html", title=title, posts=posts)

@app.route("/my-post/<int:id>/")
def my_post(id):
    mypost = Post.query.filter(Post.owner==id)
    
    return render_template("my-post.html", mypost=mypost)


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
        blog_to_create = Post(title=form.title.data, body=form.body.data, author=current_user.fname, owner=current_user.id)
        db.session.add(blog_to_create)
        db.session.commit()
        flash(f'Blog created successfully', category='success')
        return redirect(url_for('home_page'))
    
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Find below error message {err_msg}', category='danger')
     
    return render_template('create-blog.html', form=form)


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


#I thought to create error handly pages

#invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500


@app.route('/delete/<int:id>')
def delete(id):
    blog_to_delete = Post.query.get_or_404(id)
    

    try:
        db.session.delete(blog_to_delete)
        db.session.commit()
        flash('Blog successfully deleted', category='success')
        return redirect(url_for('my_post', id=current_user.id))

    except:
        flash('Looks like there is an error', category='danger')
        return redirect(url_for('my_post', id=current_user.id))


@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def update(id):
    blog_to_update = Post.query.get_or_404(id)
    form = UpdateBlogForm()
    
    if form.validate_on_submit():
        blog_to_update.title = form.title.data
        blog_to_update.slug = form.slug.data
        blog_to_update.body = form.body.data
        try:
            db.session.add(blog_to_update)
            db.session.commit()
            flash('Blog successfully updated', category='success')
            return redirect(url_for('my_post', id=current_user.id))
        except:
            flash('Error. Looks like something went wrong', category='danger')
            return render_template('update.html', blog_to_update=blog_to_update, form=form)
    form.title.data = blog_to_update.title
    form.slug.data = blog_to_update.slug
    form.body.data = blog_to_update.body
    return render_template('update.html', blog_to_update=blog_to_update, form=form)

