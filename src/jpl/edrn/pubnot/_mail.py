# encoding: utf-8

'''📚🪢 EDRN PubNot: email notification.'''

from ._pubmed import lookup_titles
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging, smtplib

_logger = logging.getLogger(__name__)
_from = 'sean.kelly@jpl.nasa.gov'


def notify(to_addresses: str, smtp: str, port: int, user: str, pw: str, new_pmids: set, del_pmids: set, apikey: str):
    _logger.info(
        'Sending email via %s to %s about %d new pmids and %d deleted pmids', smtp, to_addresses,
        len(new_pmids), len(del_pmids)
    )

    # First, make a lookup table of all the pubmed IDs to their titles in PubMed
    pmid_to_titles = lookup_titles(new_pmids | del_pmids, apikey)

    message = ['👋 Greetings! PubNot here with a message about changes in publications.\n\n']
    if len(new_pmids) == 1:
        message.append('There was one new publication:\n')
        pmid = new_pmids.pop()
        message.append(f'PMID {pmid}, "{pmid_to_titles[pmid]}"\n')
    elif len(new_pmids) > 1:
        message.append(f'There were {len(new_pmids)} new publications:\n')
        for pmid in new_pmids:
            message.append(f'PMID {pmid}, "{pmid_to_titles[pmid]}"\n')

    if len(del_pmids) == 1:
        message.append('One publication was deleted:\n')
        pmid = del_pmids.pop()
        message.append(f'PMID {pmid}, "{pmid_to_titles[pmid]}" was removed by the DMCC\n')
    elif len(del_pmids) > 1:
        message.append(f'{len(del_pmids)} publications were deleted:\n')
        for pmid in del_pmids:
            message.append(f'PMID {pmid}, "{pmid_to_titles[pmid]}"\n')

    message = '\n'.join(message)

    email = MIMEMultipart()
    email['From'] = _from
    email['To'] = to_addresses
    email['Subject'] = 'Changes in publications from DMCC'
    email.attach(MIMEText(message, 'plain'))

    # Note: this is fine for JPL SMTP which supports StartTLS
    _logger.debug('Connecting to SMTP with StartTLS on %s at %d', smtp, port)
    with smtplib.SMTP(host=smtp, port=port) as server:
        server.starttls()
        server.login(user, pw)
        server.sendmail(_from, to_addresses, email.as_string())
        server.quit()
