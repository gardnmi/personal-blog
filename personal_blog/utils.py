from PIL import Image
import os
import secrets
from personal_blog import app


def save_picture(form_picture):
    # random_hex = secrets.token_hex(8)
    # _, f_ext = os.path.splitext(form_picture.filename)
    # picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/tags', form_picture.filename)

    # output_size = (125, 125)
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return form_picture.filename
