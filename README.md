# RBD Prober

RBD Prober is a monitoring software to monitor availability and performance of Rados Block Device (RBD) and exports them via HTTP for Prometheus consumption.

## Getting Started

The code use the python binding of librados and librbd. When running the code the native RADOS and RBD library and development headers are expected to be installed.

On debian based systems (apt) these may be:

```
librbd-dev librados-dev
```

On rpm based systems (dnf, yum, etc) these may be:

```
librbd-devel librados-devel
```

## Usage

RBD Prober needs a `config.yaml` file that provides the following information to be run.

```yaml
name: "write-test" # name of the test
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
python3 main.py --config /path/to/config.yaml
```
