import yaml
import argparse

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from prometheus_client import make_wsgi_app

from rbd_prober.prober import RBDProber


app = Flask(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str,
                        help="config file path", default="config.yaml")
    args = parser.parse_args()

    with open(args.config) as config_file:
        configs = yaml.full_load(config_file)
        rbd_prober = RBDProber(**configs)

    rbd_prober.start()


if __name__ == "__main__":
    main()
    app_dispatch = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })
    run_simple('0.0.0.0', 8000, app_dispatch)
