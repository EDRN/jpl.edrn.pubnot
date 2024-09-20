# encoding: utf-8

'''📚🪢 EDRN PubNot: publicaiton scanning.'''

from ._rdf import read_pmids
import pathlib, logging, pickle

_logger = logging.getLogger(__name__)


def _load_pubs(journal: pathlib.Path) -> set:
    '''Load the known pubmed IDs from the `journal` and return a set of strings of them.

    If the journal file doesn't exist, just return an empty set.
    '''
    _logger.debug('Reading publications from %s', journal)
    if journal.is_file():
        with journal.open('rb') as io:
            return pickle.load(io)
    else:
        return set()


def _save_pubs(pubs: set, journal: pathlib.Path):
    '''Save the set of `pubs` to the `journal`.'''
    _logger.debug('Saving %d publications %s', len(pubs), journal)
    with journal.open('wb') as io:
        pickle.dump(pubs, io)


def scan(rdf_url: str, journal: pathlib.Path) -> tuple:
    '''Scan the publications at `rdf_url` and update the `journal`, returning a
    boolean indicating if this is the very first scan, a set of new pubmed IDs, and
    a set of changed pubmed IDs.
    '''
    _logger.debug('Scanning and comparing pubs from %s and %s', rdf_url, journal)
    existing = _load_pubs(journal)
    first_time = len(existing) == 0
    fresh_pmids = read_pmids(rdf_url)
    _logger.info('From last run had %d pubs, RDF says there are %d', len(existing), len(fresh_pmids))
    new_pmids = fresh_pmids - existing
    del_pmids = existing - fresh_pmids
    _save_pubs(fresh_pmids, journal)
    return first_time, new_pmids, del_pmids
