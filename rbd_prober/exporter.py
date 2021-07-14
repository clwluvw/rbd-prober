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
    def getInstance():
        if PrometheusExporter.__instance is None:
            PrometheusExporter()
        return PrometheusExporter.__instance

    def __init__(self, *args, **kwargs):
        if PrometheusExporter.__instance is not None:
            raise Exception("This class is a singleton!")
        PrometheusExporter.__instance = self

    def init_metrics(self, histogram_buckets):
        histogram_buckets.append(INF)
        self.response_time = Histogram(
            name='response_time',
            documentation='Prober response time in seconds',
            labelnames=self.LABELS,
            namespace=self.NAMESPACE,
            buckets=histogram_buckets,
        )
        self.bandwidth = Counter(
            name='bandwidth',
            documentation='Bytes has be written or read from RBD',
            labelnames=self.LABELS,
            namespace=self.NAMESPACE,
        )
        self.prober_ops = Counter(
            name='ops',
            documentation='Total ops count',
            labelnames=self.LABELS,
            namespace=self.NAMESPACE,
        )

    def observe(self, response_time, bytes_size, label_values):
        if response_time != -1:
            label_values['status'] = 'success'
        else:
            label_values['status'] = 'fail'

        self.response_time.labels(**label_values).observe(response_time)
        self.bandwidth.labels(**label_values).inc(bytes_size)
        self.prober_ops.labels(**label_values).inc()
