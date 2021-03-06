from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    SelectMultipleField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Optional,
)
from personal_blog.models import User, Tag


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    alias = StringField("Alias", validators=[DataRequired()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    try:
        tags = SelectMultipleField(
            choices=Tag.query.with_entities(Tag.slug, Tag.tag_name).all()
        )
    except:
        pass
    description = TextAreaField("Description")
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TagForm(FlaskForm):
    name = StringField("Tag Name", validators=[DataRequired(), Length(min=2, max=20)])
    picture = FileField("Update Tag Picture", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("Submit")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError(
                "There is no account with that email. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")


class SearchForm(FlaskForm):
    q = StringField("Search terms", validators=[Optional(), Length(1, 256)])


class BulkDeleteForm(FlaskForm):
    scope = SelectField(
        "Privileges",
        choices=[
            ("all_selected_items", "All selected items"),
            ("all_search_results", "All search results"),
        ],
        validators=[DataRequired()],
    )


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    alias = StringField("Alias", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    admin = BooleanField("Make Admin")
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")

    def validate_alias(self, alias):
        user = User.query.filter_by(alias=alias.data).first()
        if user:
            raise ValidationError("That alias is taken. Please choose a different one.")
