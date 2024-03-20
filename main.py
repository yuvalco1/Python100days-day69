from datetime import date

from flask import Flask, abort, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy import Column, Integer, String, Text, ForeignKey
# from flask_gravatar import Gravatar
from hashlib import md5

from forms import CreatePostForm, RegForm, LoginForm, CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yuvalco1'
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# gravatar = Gravatar(app,
#                     size=100,
#                     rating='g',
#                     default='retro',
#                     force_default=False,
#                     force_lower=False,
#                     use_ssl=False,
#                     base_url=None)

def avatar(email):
    digest = md5(email.lower().encode('utf-8')).hexdigest()
    return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={100}'


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# test_img= avatar("yuvalco1@gmail.com")
# print(test_img)

# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    subtitle = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    img_url = Column(String(250), nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = Column(Integer, ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(1000))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

    # class BlogPost(db.Model):
    #     __tablename__ = "blog_posts"
    #     id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #     title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    #     subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    #     date: Mapped[str] = mapped_column(String(250), nullable=False)
    #     body: Mapped[str] = mapped_column(Text, nullable=False)
    #     author: Mapped["User"] = relationship(back_populates="posts")
    #     author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    #     img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    #
    #
    # # Create a User table for all your registered users.
    # class User(UserMixin, db.Model):
    #     __tablename__ = "users"
    #     id: Mapped[int] = mapped_column(Integer, primary_key=True)
    #     email: Mapped[str] = mapped_column(String(100), unique=True)
    #     password: Mapped[str] = mapped_column(String(100))
    #     name: Mapped[str] = mapped_column(String(1000))
    #     posts: Mapped[List["BlogPost"]] = relationship(back_populates="author")
    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# example code for a conditional decorator
# def conditional_decorator(func):
#     def wrapper():
#         oldstring = func()
#
#         if condition:
#             newstring = oldstring.upper()
#         else:
#             newstring = oldstring.lower()
#
#         return newstring
#
#     return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.get_id() == '1':
            return func(*args, **kwargs)
        else:
            return abort(403)

    return wrapper


#  Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegForm()
    if form.validate_on_submit():
        if request.method == "POST":
            user = User.query.filter_by(email=request.form.get('email')).first()
            if user:
                flash("Email already exists, please Login")
                return redirect(url_for('login'))
            else:
                to_add_user = User(name=request.form.get('name'), email=request.form.get('email'),
                                   password=generate_password_hash(request.form['password'], method="pbkdf2",
                                                                   salt_length=8))
                db.session.add(to_add_user)
                db.session.commit()
                print(to_add_user.id)
                login_user(to_add_user, remember=True)
                flash("User created successfully")
                return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated,
                           admin=current_user.get_id == 1)


#  Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            email = request.form.get('email').lower()
            password_entered = request.form.get('password')
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password_entered):
                print("Login Successful")
                flash("Logged in successfully")
                print(user.password)
                print(check_password_hash(user.password, password_entered))
                print(user)
                login_user(user, remember=True)
                return redirect(url_for('get_all_posts'))
            else:
                flash("Login unsuccessful. Please check username and password")
                return redirect(url_for('login'))

    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated,
                           admin=current_user.get_id() == '1')


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    author = db.get_or_404(User,
                           requested_post.author_id).name  # better way is to reference in the html post.author.name without finding here the author name
    comments = requested_post.comments
    if form.validate_on_submit():
        if request.method == "POST":
            new_comment = Comment(
                text=form.comment.data,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
    return render_template("post.html", post=requested_post, admin=current_user.get_id() == '1', author=author,
                           form=form, logged_in=current_user.is_authenticated, comments=comments, avatar=avatar)


# Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
