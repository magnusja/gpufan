import time

from nvfan.decorators import constant, aggressive

import logging

logging.basicConfig(level=logging.DEBUG)


@constant(percentage=95)
def main():
    time.sleep(60)


@aggressive()
def main_agg():
    time.sleep(60)


if __name__ == '__main__':
    main()
    main_agg()
