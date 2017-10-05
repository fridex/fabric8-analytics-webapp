#!/usr/bin/env python3
import os
import connexion
import logging
from flask import jsonify, Response
from flask_script import Manager
from f8a_worker.setup_celery import init_selinon

import f8a_webapp.defaults as defaults
from f8a_webapp.auth import oauth
from f8a_webapp.models import create_models

logger = logging.getLogger(__name__)


def init_logging():
    """ Initialize application logging """
    # Initialize flask logging
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    # Use flask App instead of Connexion's one
    application.logger.addHandler(handler)
    # Webapp logger
    logger.setLevel(logging.DEBUG)
    # lib logger
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    liblog = logging.getLogger('f8a_webapp')
    liblog.setLevel(logging.DEBUG)
    liblog.addHandler(handler)


app = connexion.App(__name__)
application = app.app
init_logging()
app.add_api(defaults.SWAGGER_YAML_PATH)
# Expose for uWSGI
manager = Manager(application)
# Needed for session
application.secret_key = defaults.APP_SECRET_KEY
oauth.init_app(application)


logger.debug("Initializing Selinon")
init_selinon()
logger.debug("Selinon initialized successfully")


@app.route('/')
def ui_index():
    """Our first citizen URL."""
    # TODO: is this safe? should be...
    # TODO: more optimal way?
    with open(os.path.join(defaults.STATIC_DIR, 'html', 'index.html')) as index_html:
        return Response(index_html.read(), content_type='text/html')


@app.route('/static/html/<page>')
def ui_html(page):
    """Access static html files."""
    # TODO: is this safe? should be...
    # TODO: more optimal way?
    try:
        with open(os.path.join(defaults.STATIC_DIR, 'html', page + '.html')) as project_html:
            return Response(project_html.read(), content_type='text/html')
    except FileNotFoundError:
        return jsonify({"error": "Requested file '%s.html' not found" % page}), 404


@app.route('/static/js/<js_file>')
def ui_js(js_file):
    """Access javascript files."""
    # TODO: is this safe? should be...
    # TODO: more optimal way?
    try:
        with open(os.path.join(defaults.STATIC_DIR, 'js', js_file)) as project_html:
            return Response(project_html.read(), content_type='application/javascript')
    except FileNotFoundError:
        return jsonify({"error": "Requested file '%%' not found" % js_file}), 404


@app.route('/static/css/<css_file>')
def ui_css(css_file):
    """Access CSS files."""
    # TODO: is this safe? should be...
    # TODO: more optimal way?
    try:
        with open(os.path.join(defaults.STATIC_DIR, 'js', css_file)) as project_html:
            return Response(project_html.read(), content_type='text/css')
    except FileNotFoundError:
        return jsonify({"error": "Requested file '%s' not found" % css_file}), 404


@app.route('/api/v1')
def api_v1():
    """Provide a listing of available endpoints."""
    paths = []

    for rule in application.url_map.iter_rules():
        rule = str(rule)
        if rule.startswith('/api/v1'):
            paths.append(rule)

    return jsonify({'paths': paths})

@manager.command
def initjobs():
    """ initialize default jobs """""
    logger.debug("Default jobs initialized")
    logger.debug("Initializing DB for tokens")
    create_models()
    logger.debug("DB for tokens initialized")

@manager.command
def runserver():
    """Run webapp service server."""
    app.run(
        port=os.getenv('WEBAPP_SERVICE_PORT', defaults.DEFAULT_SERVICE_PORT),
        server='flask',
        debug=True,
        use_reloader=True,
        threaded=True,
        processes=1
    )

if __name__ == '__main__':
    manager.run()
