from wsgiref.simple_server import make_server
import yaml

from prometheus_client import make_wsgi_app
from loguru import logger

from rbd_prober.prober import RBDProber, PrometheusExporter


def home():
    status = '200 OK'
    header = ('Content-Type', 'text/html')
    output = b'''<html>
        <head><title>RBD Prober</title></head>
        <body>
        <h1>RBD Prober</h1>
        <p><a href="/metrics">Metrics</a></p>
        </body>
        </html>'''
    return status, header, output


def not_found():
    status = '404 Not Found'
    header = ('Content-Type', 'application/openmetrics-text')
    output = b''
    return status, header, output


def wsgi():
    def exporter_app(environ, start_response):
        if environ['PATH_INFO'] == '/metrics':
            app = make_wsgi_app()
            return app(environ, start_response)

        if environ['PATH_INFO'] == '/':
            status, header, output = home()
        else:
            status, header, output = not_found()

        start_response(status, [header])
        return [output]
    return exporter_app


with open("./config.yaml") as config_file:
    configs = yaml.full_load(config_file)

    # exporer config
    exporter_host = configs['exporter_host']
    exporter_port = configs['exporter_port']

    # init exporter metrics
    PrometheusExporter.getInstance().init_metrics(configs['histogram_buckets'])

    for config in configs['probs']:
        rbd_prober = RBDProber(**config)
        rbd_prober.start()


app = wsgi()
httpd = make_server(exporter_host, exporter_port, app)
logger.info(f"Listening on address: {exporter_host}:{exporter_port}")
httpd.serve_forever()
