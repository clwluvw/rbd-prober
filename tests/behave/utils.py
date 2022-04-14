import requests
import requests.exceptions

import time
import logging
import multiprocessing


def container_exec_with_timeout(func, timeout, *args):
    '''
    :parm list args: first element should always be docker container
    '''
    p = multiprocessing.Process(target=func, args=args)
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.kill()
        logging.error(args[0].logs())
        exit(1)


def wait_for_ceph_cluster(container):
    while True:
        rc, _ = container.exec_run(
            cmd="ceph -s"
        )
        if rc == 0:
            break
        time.sleep(1)


def wait_for_rbd_prober(container, rbd_prober_url):
    while True:
        try:
            res = requests.get(rbd_prober_url, timeout=1)
            if res.status_code == 200:
                break
        except (ConnectionRefusedError, requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            pass
        time.sleep(1)
