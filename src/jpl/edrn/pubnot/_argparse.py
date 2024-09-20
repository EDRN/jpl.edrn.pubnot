# encoding: utf-8

'''📚🪢 EDRN PubNot: argument parsing.'''


import argparse, logging


def add_logging_argparse_options(parser: argparse.ArgumentParser):
    '''Add logging options to the given `parser`.'''
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d',
        '--debug',
        action='store_const',
        const=logging.DEBUG,
        default=logging.INFO,
        dest='loglevel',
        help='📢 Log copious debugging messages suitable for developers',
    )
    group.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=logging.WARNING,
        dest='loglevel',
        help="🤫 Don't log anything except warnings and critically-important messages",
    )
