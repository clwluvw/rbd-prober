from behave import fixture
import docker

from tests.behave import utils

import tempfile
import yaml


@fixture
def docker_client(context):
    context.client = docker.from_env()


@fixture
def docker_network(context):
    ipam_pool = docker.types.IPAMPool(
        subnet='192.168.3.0/24',
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )
    context.network = context.client.networks.create(
        "rbd_prober_network",
        driver="bridge",
        ipam=ipam_config
    )
    yield

    context.network.remove()


@fixture
def ceph_cluster(context):
    context.ceph_container = context.client.containers.run(
        image="quay.io/ceph/daemon:v6.0.8-stable-6.0-pacific-centos-stream8",
        command="demo",
        environment={
            "DEMO_DAEMONS": "osd",
            "MON_IP": "192.168.3.2",
            "CEPH_PUBLIC_NETWORK": "192.168.3.0/24",
        },
        detach=True,
        network=context.network.name,
    )
    utils.container_exec_with_timeout(utils.wait_for_ceph_cluster, 20, context.ceph_container)
    yield
    context.ceph_container.remove(force=True)


@fixture
def prepare_rbd(context):
    # create watchdog pool
    context.ceph_container.exec_run(
        cmd="ceph osd pool create watchdog"
    )
    # enable rbd application on watchdog pool
    context.ceph_container.exec_run(
        cmd="ceph osd pool application enable watchdog rbd"
    )
    # create rbd image
    context.ceph_container.exec_run(
        cmd="rbd create write_foo --size 4096 --image-feature layering -p watchdog"
    )
    context.ceph_container.exec_run(
        cmd="rbd create read_foo --size 4096 --image-feature layering -p watchdog"
    )
    # create watchdog cephx user
    res = context.ceph_container.exec_run(
        cmd="ceph auth get-or-create client.watchdog mon 'profile rbd' osd 'profile rbd pool=watchdog'",
        stream=False,
        demux=False
    )
    context.ceph_keyring = tempfile.NamedTemporaryFile()
    with open(context.ceph_keyring.name, "wb") as f:
        f.write(res.output)
    yield
    # clean ceph_keyring file
    context.ceph_keyring.close()


@fixture
def create_rbd_prober_config(context):
    config = {
        'log_level': 'debug',
        'probs': [
            {
                'name': 'write_test',
                'interval': 1,
                'prober': {
                    'object_size': 4096,
                    'type': "write",
                },
                'pool_name': 'watchdog',
                'image_name': 'write_foo',
                'rbd_user': 'watchdog',
                'rbd_keyring_path': context.ceph_keyring.name,
                'monitors': [
                    '192.168.3.2'
                ],
            },
            {
                'name': 'read_test',
                'interval': 1,
                'prober': {
                    'object_size': 4096,
                    'type': "read",
                },
                'pool_name': 'watchdog',
                'image_name': 'read_foo',
                'rbd_user': 'watchdog',
                'rbd_keyring_path': context.ceph_keyring.name,
                'monitors': [
                    '192.168.3.2'
                ],
            }
        ],
        'histogram_buckets': [
            0, 0.2, 0.5, 0.7, 1.0, 2.0, 5.0
        ],
        'exporter_host': '0.0.0.0',
        'exporter_port': 8000,
    }
    context.rbd_prober_config_file = tempfile.NamedTemporaryFile()
    with open(context.rbd_prober_config_file.name, 'w') as f:
        yaml.dump(config, f)
    yield
    # clean rbd_prober_config_file
    context.rbd_prober_config_file.close()


@fixture
def run_rbd_prober(context):
    # build rbd_prober
    context.client.images.build(
        path=".",
        tag="rbd_prober",
    )
    # run rbd_prober
    context.rbd_prober_container = context.client.containers.run(
        image="rbd_prober",
        volumes={
            context.rbd_prober_config_file.name: {
                'bind': '/rbd-prober/config.yaml',
                'mode': 'ro',
            },
            context.ceph_keyring.name: {
                'bind': context.ceph_keyring.name,
                'mode': 'ro',
            },
        },
        detach=True,
    )
    context.network.connect(context.rbd_prober_container, ipv4_address='192.168.3.100')
    context.rbd_prober_url = 'http://192.168.3.100:8000/'
    utils.container_exec_with_timeout(
        utils.wait_for_rbd_prober, 10,
        context.rbd_prober_container, context.rbd_prober_url
    )
    yield
    context.rbd_prober_container.remove(force=True)
