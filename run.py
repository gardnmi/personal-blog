import os
from sqlalchemy_utils import database_exists
from personal_blog import app, db, bcrypt
from personal_blog.models import User, Post, Tag

with open('sample_post.txt') as file:
    content = file.read().replace('\n', '')


def my_function():
    current_file_directory = os.path.dirname(os.path.realpath(__file__))
    database_directory = os.path.join(current_file_directory, 'personal_blog')
    os.chdir(database_directory)

    with app.app_context():
        if database_exists(os.environ.get('SQLALCHEMY_DATABASE_URI')):
            os.chdir(current_file_directory)
        else:
            os.chdir(current_file_directory)
            db.drop_all()
            db.create_all()

            hashed_password = bcrypt.generate_password_hash(os.environ.get('BLOG_PASSWORD')).decode('utf-8')
            user = User(username='gardnmi', alias='Michael G.', password=hashed_password)
            db.session.add(user)
            db.session.commit()

            python_tag = Tag(tag_name='Python', slug='python', image_file='python.png')
            machine_learning_tag = Tag(tag_name='Machine Learning', slug='machine-learning', image_file='machine_learning.png')
            flask_tag = Tag(tag_name='Flask', slug='flask', image_file='flask.png')

            db.session.add_all([python_tag, machine_learning_tag, flask_tag])
            db.session.commit()

            user = User.query.get(int(1))
            tags = Tag.query.get(int(1))
            post = Post(title='First Blog Post', slug='first-blog-post', content=content, user_id=user.id, tags=[tags])
            db.session.add(post)
            db.session.commit()


my_function()


if __name__ == '__main__':
    app.run(debug=True)
