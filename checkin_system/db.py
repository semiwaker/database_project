from flask import g


def get_db():
    pass


def close_db(exception=None):
    pass

def init_app(app):
    app.teardown_appcontext(close_db)
