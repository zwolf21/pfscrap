import os, sys
import argparse

import pandas as pd

import settings.environments
from pfscrap.argparser.kofia import set_kofia_argparser, parse_kofia_args


def main():

    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="ProFp Scraper"
    )

    set_kofia_argparser(argparser)

    args = argparser.parse_args()

    parse_kofia_args(args)


if __name__ == "__main__":
    main()
