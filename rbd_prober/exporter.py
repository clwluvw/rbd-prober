from prometheus_client import Histogram, Counter
from prometheus_client.utils import INF


class PrometheusExporter(object):
    __instance = None
    LABELS = [
        'name',
        'object_size',
        'type',
        'pool',
        'image',
        'status',
    ]
    NAMESPACE = 'rbd_prober'

    @staticmethod
    def getInstance(label_values):
        if PrometheusExporter.__instance is None:
            PrometheusExporter(label_values)
        return PrometheusExporter.__instance

    def __init__(self, label_values, *args, **kwargs):
        if PrometheusExporter.__instance is not None:
            raise Exception("This class is a singleton!")
        self._init_metrics()
        self.label_values = label_values
        PrometheusExporter.__instance = self

    def _init_metrics(self):
        self.response_time = Histogram(
            name='response_time',
            documentation='Prober response time in seconds',
            labelnames=self.LABELS,
            namespace=self.NAMESPACE,
            buckets=(0, .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, INF),
        )
        self.bandwidth = Counter(
            name='bandwidth',
            documentation='Bytes has be written or read from RBD',
            labelnames=self.LABELS,
            namespace=self.NAMESPACE,
        )
        self.prober_requests = Counter(
            name='request_count',
            documentation='Total request count',
            labelnames=self.LABELS,
            namespace=self.NAMESPACE,
        )

    def observe(self, response_time, bytes_size):
        label_values = self.label_values
        if response_time != -1:
            label_values['status'] = 'success'
        else:
            label_values['status'] = 'fail'

        self.response_time.labels(**label_values).observe(response_time)
        self.bandwidth.labels(**label_values).inc(bytes_size)
        self.prober_requests.labels(**label_values).inc()
