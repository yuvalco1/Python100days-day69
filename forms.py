from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, URL, InputRequired, Length, Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=250)])
    email = StringField('Email', validators=[Email("This field requires a valid email address")])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,
                                                                             message="Password must be at least 8 charcters long")])
    submit = SubmitField(label='Register')
    """
    remember_me = BooleanField('Remember me')
    salary = DecimalField('Salary', validators=[InputRequired()])
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    country = SelectField('Country', choices=[('IN', 'India'), ('US', 'United States'),('UK', 'United Kingdom')])
    message = TextAreaField('Message', validators=[InputRequired()])
    photo = FileField('Photo')
    """


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email("This field requires a valid email address")])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,
                                                                             message="Password must be at least 8 charcters long")])
    submit = SubmitField(label='Login')


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")