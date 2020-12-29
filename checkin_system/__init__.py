import os
from datetime import timedelta

from flask import Flask, redirect, url_for

from . import auth, main, db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DEBUG=True,
        # SEND_FILE_MAX_AGE_DEFAULT=timedelta(seconds=1),
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def root():
        return redirect(url_for('main.home'))

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    @app.context_processor  # 上下文渲染器，给所有html添加渲染参数
    def inject_url():
        data = {
            "url_for": dated_url_for,
        }
        return data

    def dated_url_for(endpoint, **values):
        filename = None
        if endpoint == 'static':
            filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            # 取文件最后修改时间的时间戳，文件不更新，则可用缓存
            values['v'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)

    return app
