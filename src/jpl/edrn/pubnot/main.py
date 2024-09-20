# encoding: utf-8

'''📚🪢 EDRN PubNot: main entrypoint.'''


from . import VERSION
from ._scanner import scan
from ._argparse import add_logging_argparse_options
from ._mail import notify
import argparse, logging, pathlib, sys, os


_logger  = logging.getLogger(__name__)
_pub_rdf = 'https://edrn.jpl.nasa.gov/cancerdataexpo/rdf-data/publications/@@rdf'
_email   = 'sean.kelly@jpl.nasa.gov'
_smtp    = 'smtp.jpl.nasa.gov'
_port    = 587


def main():
    '''Main entrypoint.'''
    parser = argparse.ArgumentParser(description='Notification of changes to EDRN publications')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    journal = pathlib.Path.home() / '.publication-journal'
    parser.add_argument('-j', '--journal', default=str(journal), help='📓 Journal file [%(default)s]')
    parser.add_argument('-r', '--reset', default=False, action='store_true', help='❌ Reset the journal')
    parser.add_argument('-u', '--url', default=_pub_rdf, help='🔗 URL to RDF of publications [%(default)s]')
    parser.add_argument(
        '-e', '--email', default=_email, help='📧 Comma-separated list of emails to notify [%(default)s]'
    )
    parser.add_argument('-s', '--smtp', default=_smtp, help='🖥️ SMTP server for email [%(default)s]')
    parser.add_argument('-p', '--port', default=str(_port), help='🍄‍🟫 SMTP port [%(default)s]')
    parser.add_argument('-a', '--apikey', help='🔑 Entrez API key, defaults to env var ENTREZ_API_KEY')
    add_logging_argparse_options(parser)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    journal = pathlib.Path(args.journal)
    apikey = args.apikey if args.apikey else os.getenv('ENTREZ_API_KEY')
    port = int(args.port)
    if not apikey:
        raise ValueError('Please specify either --apikey or set ENTREZ_API_KEY')
    if args.reset: journal.unlink(missing_ok=True)
    first_time, new_pmids, deleted_pmids = scan(args.url, journal)
    if first_time:
        _logger.info('Initial run, so no notifications will be sent')
    elif new_pmids or deleted_pmids:
        _logger.info('Notifying of %d new_pmids and/or %d deleted_pmids', len(new_pmids), len(deleted_pmids))
        notify(args.email, args.smtp, port, new_pmids, deleted_pmids, apikey)
    else:
        _logger.info('No changes from last run, so no notifications')
    sys.exit(0)


if __name__ == '__main__':
    main()
