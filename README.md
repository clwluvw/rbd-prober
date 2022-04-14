# RBD Prober

[![lint](https://github.com/clwluvw/rbd-prober/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/clwluvw/rbd-prober/actions/workflows/lint.yml) [![test](https://github.com/clwluvw/rbd-prober/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/clwluvw/rbd-prober/actions/workflows/test.yml)

RBD Prober is a monitoring software to monitor availability and performance of Rados Block Device (RBD) and exports them via HTTP for Prometheus consumption.

## Getting Started

The code use the python binding of librados and librbd. When running the code the native RADOS and RBD library and development headers are expected to be installed.

On debian based systems (apt) these may be:

```
librbd-dev python3-rbd librados-dev python3-rados
```

On rpm based systems (dnf, yum, etc) these may be:

```
librbd-devel librados-devel
```

## Usage

RBD Prober needs a `config.yaml` file that provides the following information to be run.

```yaml
exporter_host: 0.0.0.0 # listen address
exporter_port: 8000 # listen port
log_level: info # log level (info, debug, error, warn)
histogram_buckets: # Histogram Buckets for rbd_prober_response_time metric
  - 0
  - 0.2
  - 0.5
  - 0.7
  - 1.0
  - 2.0
  - 5.0
probs: # list of probers
  - name: "write-test" # name of the test
    interval: 5 # seconds
    prober:
      object_size: 4096 # data size to be written or read from RBD image
      type: "write" # type of the operation write OR read
    pool_name: "watchdog" # Ceph pool name that images is exists in
    image_name: "foo" # Image name that data will be write or read from
    rbd_user: "watchdog" # cephx user that has access to the image
    rbd_keyring_path: "/etc/ceph/ceph.keyring" # path of the rbd_user keyring
    monitors: # Ceph monitor ips
      - 10.0.0.1
      - 10.0.0.2
      - 10.0.0.3
```

To run it:

```bash
pip3 install -r requirements.txt
python3 app.py
```

## Metrics

| Metric                     | Notes
|----------------------------|---------------------------------------
| rbd_prober_response_time   | Prober response time in seconds
| rbd_prober_bandwidth_total | Bytes has be written or read from RBD
| rbd_prober_ops_total       | Total ops count
