import logging
import os
import sys

from flask import Flask
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect
from termcolor import colored

from sibyl import g
from sibyl.routes import add_routes

LOGGER = logging.getLogger(__name__)


class Sibyl:
    """Sibyl Class.

    The Sibyl Class provides the main functionalities of Sibyl to launch or
    test the Flask server.

    Args:
        conf (dict):
            Dictionary loaded from `config.yaml`
        docker (bool):
            Whether launch app in docker environment.
    """

    def _init_flask_app(self, env):
        app = Flask(
            __name__,
            static_url_path="",
            static_folder="../apidocs",
            template_folder="../apidocs",
        )

        app.config.from_mapping(**self._conf["flask"])

        if env == "production":
            app.config.from_mapping(DEBUG=False, TESTING=False)

        elif env == "development":
            app.config.from_mapping(DEBUG=True, TESTING=True)

        elif env == "test":
            app.config.from_mapping(DEBUG=False, TESTING=True)

        CORS(app)
        add_routes(app)

        # set up global variables
        g["config"] = self._conf
        g["app"] = app

        return app

    def __init__(self, conf: dict, docker: bool):
        self._conf = conf.copy()

        if not docker:
            kargs = {
                key: conf["mongodb"][key] for key in ["db", "host", "port", "username", "password"]
            }
            self._db = connect(**kargs)
        else:
            kargs = {
                key: conf["docker"]["mongodb"][key]
                for key in ["db", "host", "port", "username", "password"]
            }
            self._db = connect(**kargs)
        # TODO - using testing datasets in test env

    def run_server(self, env=None, port=None):
        env = self._conf["flask"]["ENV"] if env is None else env
        port = self._conf["flask"]["PORT"] if port is None else port

        # env validation
        if env not in ["development", "production", "test"]:
            LOGGER.exception("env '%s' is not in ['development', 'production', 'test']", env)
            raise ValueError

        # in case running app with the absolute path
        sys.path.append(os.path.dirname(__file__))

        app = self._init_flask_app(env)

        LOGGER.info(colored("Starting up FLASK APP in {} mode".format(env), "yellow"))

        LOGGER.info(
            colored("APIs are available on:", "yellow")
            + "  http://localhost:"
            + colored(port, "green")
            + "/"
        )

        if env == "development":
            app.run(debug=True, port=port)
            # app.run(debug=True, port=port, ssl_context="adhoc")

        elif env == "production":
            server = WSGIServer(("0.0.0.0", port), app, log=None)
            # server = WSGIServer(('0.0.0.0', port), app, ssl_context="adhoc", log=None)
            server.serve_forever()
