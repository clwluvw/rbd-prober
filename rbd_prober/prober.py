from loguru import logger
from datetime import datetime

import rados
import rbd

from .exceptions import InternalError


class Prober(object):
    def __init__(self, *args, **kwargs):
        self.type = kwargs.get('type')
        self._validate_type()
        self.object_size = int(kwargs.get('object_size'))

    def _validate_type(self):
        if self.type != 'write' and self.type != 'read':
            raise TypeError("prober type should be one of the write or read")


class RBDProber(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.interval = kwargs.get('interval')
        self.prober = Prober(**kwargs.get('prober'))
        self.pool_name = kwargs.get('pool_name')
        self.image_name = kwargs.get('image_name')
        self.rbd_user = kwargs.get('rbd_user')
        self.rbd_keyring_path = kwargs.get('rbd_keyring_path')
        self.monitors = kwargs.get('monitors')

        rados_connection = self._connect_to_rados()
        self.image_ioctx = self._open_image(rados_connection)

    def _connect_to_rados(self):
        cluster = rados.Rados(rados_id=self.rbd_user, conf={
            "mon_host": ",".join(self.monitors),
            "keyring": self.rbd_keyring_path,
            "rbd_cache": "false",
        })
        cluster.connect()
        return cluster

    def _open_image(self, rados_connection):
        ioctx = rados_connection.open_ioctx(self.pool_name)
        return rbd.Image(ioctx, self.image_name)

    def probe(self):
        logger.debug("start probing")
        response_time = -1

        try:
            if self.prober.type == "write":
                response_time = self.write()
            elif self.prober.type == "read":
                response_time = self.read()
        except InternalError:
            return

        logger.info(f"probbing finished response_time: {response_time}")

    def write(self):
        logger.debug("start write probe")

        try:
            self.image_ioctx.discard(0, self.prober.object_size)
        except Exception:
            logger.exception("failed to discard previous write")
            raise InternalError()

        data = b'1' * self.prober.object_size
        logger.debug("data created for write")
        start_time = datetime.now()
        try:
            n = self.image_ioctx.write(data, 0)
            end_time = datetime.now()
        except Exception:
            logger.exception("failed to write to rbd image")
            return -1
        logger.debug(f"write finished data_size: {n}")

        response_time = (end_time - start_time).total_seconds()
        logger.debug(f"response time calculated \
                    response_time: {response_time}")
        return response_time

    def read(self):
        logger.debug("start read probe")

        data = b'1' * self.prober.object_size
        try:
            self.image_ioctx.write(data, 0)
        except Exception:
            logger.exception("failed to prepare data to for read")
            raise InternalError()
        logger.debug("data has been written to be read")

        start_time = datetime.now()
        try:
            self.image_ioctx.read(0, self.prober.object_size)
            end_time = datetime.now()
        except Exception:
            logger.exception("failed to read data from rbd image")
            return -1
        logger.debug("read finished")

        response_time = (end_time - start_time).total_seconds()
        logger.debug(f"response time calculated \
                    response_time: {response_time}")
        return response_time
