from rbd_prober.exporter import PrometheusExporter

from prometheus_client import REGISTRY


def get_sample_value(name, labels=None):
    value = REGISTRY.get_sample_value(name, labels)
    if value is None:
        return 0
    return value


def test_prometheus_exporter():
    label_values = {
        'name': 'test',
        'object_size': '4096',
        'type': 'write',
        'pool': 'test_pool',
        'image': 'test_image',
        'status': 'success',
    }
    prometheus_exporter = PrometheusExporter.getInstance(label_values)
    ops_before = get_sample_value('rbd_prober_ops_total', label_values)
    bandwidth_before = get_sample_value('rbd_prober_bandwidth_total', label_values)
    prometheus_exporter.observe(0.5, 4096)
    ops_after = get_sample_value('rbd_prober_ops_total', label_values)
    bandwidth_after = get_sample_value('rbd_prober_bandwidth_total', label_values)
    assert ops_after - ops_before == 1
    assert bandwidth_after - bandwidth_before == 4096

    label_values = {
        'name': 'test',
        'object_size': '4096',
        'type': 'write',
        'pool': 'test_pool',
        'image': 'test_image',
        'status': 'fail',
    }
    prometheus_exporter = PrometheusExporter.getInstance(label_values)
    ops_before = get_sample_value('rbd_prober_ops_total', label_values)
    bandwidth_before = get_sample_value('rbd_prober_bandwidth_total', label_values)
    prometheus_exporter.observe(-1, 4096)
    ops_after = get_sample_value('rbd_prober_ops_total', label_values)
    bandwidth_after = get_sample_value('rbd_prober_bandwidth_total', label_values)
    assert ops_after - ops_before == 1
    assert bandwidth_after - bandwidth_before == 4096
