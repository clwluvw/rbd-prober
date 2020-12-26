import yaml
import argparse
import time

from loguru import logger
from prometheus_client import start_wsgi_server

from rbd_prober.prober import RBDProber


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str,
                        help="config file path", default="config.yaml")
    args = parser.parse_args()

    with open(args.config) as config_file:
        configs = yaml.full_load(config_file)
        rbd_prober = RBDProber(**configs)

    rbd_prober.start()

    logger.info("start listening to port 8000")
    start_wsgi_server(8000)


if __name__ == "__main__":
    main()
