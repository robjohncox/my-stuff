from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("src.config.Config")

    from .database import db

    db.init_app(app)

    from .views import bp as views_blueprint

    app.register_blueprint(views_blueprint)

    return app
