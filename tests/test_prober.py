import pytest

from rbd_prober.prober import Prober


def test_prober():
    kwargs = {
        'type': 'write',
        'object_size': 4096,
    }
    prober = Prober(**kwargs)
    assert prober.type == 'write'
    assert prober.object_size == 4096

    kwargs = {
        'type': 'read',
        'object_size': 1024,
    }
    prober = Prober(**kwargs)
    assert prober.type == 'read'
    assert prober.object_size == 1024

    with pytest.raises(ValueError):
        kwargs = {
            'type': 'write',
            'object_size': 'not_int',
        }
        Prober(**kwargs)

    with pytest.raises(TypeError):
        kwargs = {
            'type': 'not_write_and_read',
            'object_size': 4096,
        }
        Prober(**kwargs)
