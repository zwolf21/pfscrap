import os
import sys
import argparse

import pandas as pd

import settings.environments
from pfscrap.argparser import set_argparser, route


def main():

    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="ProFp Scraper"
    )
    set_argparser(argparser)
    args = argparser.parse_args()
    route(args)

if __name__ == "__main__":
    main()
