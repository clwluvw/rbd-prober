import yaml
import argparse
import time
from loguru import logger

from rbd_prober.prober import RBDProber


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, help="config file path", default="config.yaml")
    args = parser.parse_args()

    with open(args.config) as config_file:
        configs = yaml.full_load(config_file)
        rbd_prober = RBDProber(**configs)
        interval = int(configs.get('interval'))
    
    while True:
        logger.debug(f"sleep {interval}")
        time.sleep(interval)
        rbd_prober.probe()
    

if __name__ == "__main__":
    main()
