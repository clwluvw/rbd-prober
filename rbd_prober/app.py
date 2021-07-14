import yaml

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

from rbd_prober.prober import RBDProber, PrometheusExporter


app = Flask(__name__)

with open("../config.yaml") as config_file:
    configs = yaml.full_load(config_file)

    # init exporter metrics
    PrometheusExporter.getInstance().init_metrics(configs['histogram_buckets'])

    for config in configs['probs']:
        rbd_prober = RBDProber(**config)
        rbd_prober.start()


@app.route('/')
def home():
    return '''<html>
        <head><title>RBD Prober</title></head>
        <body>
        <h1>RBD Prober</h1>
        <p><a href="/metrics">Metrics</a></p>
        </body>
        </html>'''


app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})
