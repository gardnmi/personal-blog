import os
from sqlalchemy_utils import database_exists
from personal_blog import app, db, bcrypt
from personal_blog.models import User


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

my_function()

if __name__ == '__main__':
    app.run(debug=True)

