from flask import Flask

IMAGE_FOLDER  = 'website/static/images/'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'zhbnrzhzh'
    app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app