from behave.fixture import use_fixture

from tests.behave import fixtures


def before_feature(context, feature):
    use_fixture(fixtures.docker_client, context)
    use_fixture(fixtures.docker_network, context)
    use_fixture(fixtures.ceph_cluster, context)
    use_fixture(fixtures.prepare_rbd, context)
    use_fixture(fixtures.create_rbd_prober_config, context)
    use_fixture(fixtures.run_rbd_prober, context)
