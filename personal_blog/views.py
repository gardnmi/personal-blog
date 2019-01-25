from flask import render_template, url_for, flash, redirect, request, abort
from personal_blog import app, db, bcrypt
from personal_blog.forms import LoginForm, UpdateAccountForm, PostForm, SearchForm, BulkDeleteForm, TagForm, RegistrationForm
from personal_blog.models import User, Post, Tag
from personal_blog.utils import save_picture
from flask_login import login_user, current_user, logout_user, login_required
from slugify import slugify
from sqlalchemy import text
from sqlalchemy import or_
# from flask_mail import Message


# --------------------------------------------USERS-------------------------------------------- #

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:

        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.alias = form.alias.data

        db.session.commit()

        flash('Your account has been updated!', 'success')

        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.alias.data = current_user.alias

    image_file = url_for('static', filename='images/profile/' + current_user.image_file)

    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()

        flash('Account has been created!', 'success')
        return redirect(url_for('admin_users'))
    return render_template('register.html', title='Register', form=form)


# --------------------------------------------POSTS-------------------------------------------- #

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    print(Post.query.filter(Post.title.ilike('%blog%'), Post.slug.ilike('%blog%')))

    return render_template('home.html', posts=posts, title='Michael G.')


@app.route("/blog")
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title='Blog')


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()

        post = Post(title=form.title.data, slug=slugify(form.title.data),
                    content=form.content.data, author=current_user, tags=tags)

        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')

        return redirect(url_for('post', slug=post.slug))
    return render_template('create_update_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<slug>")
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    print(post)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<slug>/update", methods=['GET', 'POST'])
@login_required
def update_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()

    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        tags = Tag.query.filter(Tag.slug.in_(form.tags.data)).all()
        post.title = form.title.data
        post.content = form.content.data
        post.tags = tags

        db.session.commit()

        flash('Your post has been updated!', 'success')

        return redirect(url_for('post', slug=slug))

    elif request.method == 'GET':
        print(post.tags)
        form.title.data = post.title
        form.content.data = post.content

        tag_list = []
        for tag in post.tags:
            print(tag.slug)
            tag_list.append(tag.slug)

        form.tags.data = tag_list

    return render_template('create_update_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<slug>/delete", methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted!', 'success')

    return redirect(url_for('home'))


@app.route("/tag/<string:slug>")
def tag_posts(slug):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter(Tag.slug.contains(slug)).first_or_404()

    posts = Post.query.filter(Post.tags.contains(tag))\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('tag_posts.html', posts=posts, tag=tag)


# --------------------------------------------TAGS--------------------------------------------- #

@app.route("/admin/tags/new", methods=['GET', 'POST'])
@login_required
def new_tag():
    form = TagForm()
    if form.validate_on_submit():

        tag = Tag(tag_name=form.name.data, slug=slugify(form.name.data))

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            tag.image_file = picture_file

        tag.save()

        flash('Your tag has been created!', 'success')

        return redirect(url_for('admin_tags'))

    return render_template('create_update_tag.html', title='New Tag', form=form, legend='New Tag')


@app.route("/tags/update_tag/<string:slug>", methods=['GET', 'POST'])
@login_required
def update_tag(slug):
    form = TagForm()

    tag = Tag.query.filter(Tag.slug.contains(slug)).first_or_404()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            tag.image_file = picture_file

        tag.tag_name = form.name.data
        tag.slug = slugify(form.name.data)

        tag.save()

        flash('Tags has been updated!', 'success')

        return redirect(url_for('admin_tags'))

    elif request.method == 'GET':
        form.name.data = tag.tag_name
        form.picture.data = tag.image_file

    return render_template('create_update_tag.html', title='Update Tag', form=form, legend='Update Tag')


# --------------------------------------------ADMIN-------------------------------------------- #

@app.route("/admin/tags", methods=['GET', 'POST'])
@login_required
def admin_tags():

    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Tag.sort_by(request.args.get('sort', 'created_on'),
                          request.args.get('direction', 'desc'))

    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    search = '%{0}%'.format(request.args.get('q', ''))

    tags = Tag.query \
        .filter(Tag.tag_name.ilike(search)) \
        .order_by(text(order_values)).all()

    return render_template('admin_tags.html', form=search_form, bulk_form=bulk_form, tags=tags, title='Tags')


@app.route('/admin/tags/bulk_delete', methods=['POST'])
@login_required
def admin_tags_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Tag.get_bulk_action_ids(request.form.get('scope'),
                                      request.form.getlist('bulk_ids'),
                                      query=request.args.get('q', '')
                                      )

        delete_count = Tag.bulk_delete(ids)

        flash('{0} tag(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No tags were deleted, something went wrong.', 'error')

    return redirect(url_for('admin_tags'))


@app.route("/admin/posts", methods=['GET', 'POST'])
@login_required
def admin_posts():

    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Post.sort_by(request.args.get('sort', 'created_on'),
                           request.args.get('direction', 'desc'))

    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    search = '%{0}%'.format(request.args.get('q', ''))

    posts = Post.query \
        .filter(or_(Post.title.ilike(search), Post.title.ilike(search))) \
        .order_by(text(order_values)).all()

    return render_template('admin_posts.html', form=search_form, bulk_form=bulk_form, posts=posts, title='Posts')


@app.route('/admin/posts/bulk_delete', methods=['POST'])
@login_required
def admin_posts_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Post.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       query=request.args.get('q', '')
                                       )

        delete_count = Post.bulk_delete(ids)

        flash('{0} post(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No posts were deleted, something went wrong.', 'error')

    return redirect(url_for('admin_posts'))


@app.route("/admin/users", methods=['GET', 'POST'])
@login_required
def admin_users():

    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = User.sort_by(request.args.get('sort', 'created_on'),
                           request.args.get('direction', 'desc'))

    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    search = '%{0}%'.format(request.args.get('q', ''))

    users = User.query \
        .filter(or_(User.alias.ilike(search), User.username.ilike(search))) \
        .order_by(text(order_values)).all()

    return render_template('admin_users.html', form=search_form, bulk_form=bulk_form, users=users, title='Users')


@app.route('/admin/users/bulk_delete', methods=['POST'])
@login_required
def admin_users_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = User.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       query=request.args.get('q', '')
                                       )

        delete_count = User.bulk_delete(ids)

        flash('{0} user(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No users were deleted, something went wrong.', 'error')

    return redirect(url_for('admin_users'))


# @app.route("/user/<string:username>")
# def user_posts(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     posts = Post.query.filter_by(author=user)\
#         .order_by(Post.date_posted.desc())\
#         .paginate(page=page, per_page=5)
#     return render_template('user_posts.html', posts=posts, user=user)


# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='noreply@demo.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('reset_token', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)


# @app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('login'))
#     return render_template('reset_request.html', title='Reset Password', form=form)


# @app.route("/reset_password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid or expired token', 'warning')
#         return redirect(url_for('reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash('Your password has been updated! You are now able to log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('reset_token.html', title='Reset Password', form=form)


# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         flash('Your account has been created! You are now able to log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)
