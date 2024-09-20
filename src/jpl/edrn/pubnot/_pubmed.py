# encoding: utf-8

'''📚🪢 EDRN PubNot: Entrez PubMed lookup.'''


from Bio import Entrez
from contextlib import closing
from http.client import HTTPException
from urllib.error import HTTPError
import logging, time

_logger            = logging.getLogger(__name__)
_entrez_batch_size = 20                           # Pubs to get at once
_max_failures      = 5                            # Failures to tolerate per batch
_wait_time         = 5                            # Seconds to wait between batch
Entrez.email       = 'sean.kelly@nih.gov'         # Hard coded
Entrez.tool        = 'jpl.edrn.pubnot'            # Hard coded


def lookup_titles(pmids: set, apikey: str) -> dict:
    '''Find the titles for all the pubmed IDs in `pmids` using `apikey` in the Entrez API and
    return a dictionary mapping from pubmed ID to its article title.
    '''
    _logger.info('Finding titles for %d pmids in Entrez API', len(pmids))

    Entrez.api_key = apikey
    pmids = list(pmids)
    last_group = False

    def divvy():
        '''Divide the pubmed IDs into groups for API sensitivity.'''
        nonlocal pmids, last_group
        while len(pmids) > 0:
            group, pmids = pmids[:_entrez_batch_size], pmids[_entrez_batch_size:]
            if len(pmids) == 0:
                last_group = True
            yield group

    pmids_to_titles = dict()
    for group in divvy():
        failures = 0
        while True:
            try:
                _logger.debug('Querying Entrez for pmids «%r»', group)
                with closing(Entrez.efetch(db='pubmed', retmode='xml', rettype='medline', id=group)) as ef:
                    records = Entrez.read(ef)
                    for record in records['PubmedArticle']:
                        pubmed_id = str(record['MedlineCitation']['PMID'])
                        title = str(record['MedlineCitation']['Article']['ArticleTitle'])
                        pmids_to_titles[pubmed_id] = title
                    break
            except (HTTPError, HTTPException) as ex:
                failures += 1
                if failures >= _max_failures:
                    raise RuntimeError(f'Too many failures ({failures})') from ex
                _logger.warning('Entrez failed for batch «%r»; will re-attempt', group)
                if hasattr(ex, 'geturl'):
                    _logger.warning('Entrez failed URL was «%s»', ex.geturl())
                if hasattr(ex, 'getcode'):
                    _logger.warning('Status code was %d', ex.getcode())
                time.sleep(_wait_time)
        if not last_group:
            time.sleep(_wait_time)
    return pmids_to_titles
