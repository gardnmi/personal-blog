from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from personal_blog import db, login_manager, app
from flask_login import UserMixin
from sqlalchemy import or_
from personal_blog.lib.util_sqlalchemy import ResourceMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(ResourceMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    alias = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.image_file}')"


posts_and_tags = db.Table('posts_and_tags',
                          db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                          db.Column('page_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
                          )


class Post(ResourceMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', secondary=posts_and_tags, lazy='subquery', backref=db.backref('pages', lazy=True))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Tag(ResourceMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(20), unique=True, nullable=False)
    tag_name = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (Tag.tag_name.ilike(search_query))

        return search_chain
