# encoding: utf-8

'''📚🪢 EDRN PubNot: RDF handling.'''

import rdflib, logging, re

_logger       = logging.getLogger(__name__)
_pub_type     = rdflib.URIRef('http://edrn.nci.nih.gov/rdf/types.rdf#Publication')
_pmid_pred    = rdflib.URIRef('http://edrn.nci.nih.gov/rdf/schema.rdf#pmid')
_pmid_pattern = re.compile(r'[0-9]+')


def _read_rdf(uri: str) -> dict:
    '''Parse the RDF at `uri` and return the statements made in the form of `{s→{p→[o]}}` where
    `s` is a subject URI, `p` is a predicate URI, and `[o]` is a sequence of objects which may
    be literals or URIs references.
    '''
    _logger.debug('Reading RDF from %s', uri)
    graph = rdflib.Graph()
    graph.parse(uri)
    statements = {}
    for s, p, o in graph:
        if s not in statements:
            statements[s] = {}
        predicates = statements[s]
        if p not in predicates:
            predicates[p] = []
        predicates[p].append(o)
    _logger.debug('Got %d subjects', len(statements))
    return statements


def read_pmids(uri: str) -> set:
    '''Read the RDF at `uri` and return the unique PubMed IDs from all publication objects.'''
    _logger.debug('Finding pmids at %s', uri)
    statements, pmids = _read_rdf(uri), set()
    for subject, predicates in statements.items():
        type_uri = predicates.get(rdflib.RDF.type, [None])[0]
        if type_uri != _pub_type: continue
        pmid = predicates.get(_pmid_pred, [''])[0].strip()
        if not pmid:
            _logger.info('Publication with subject URI %s does not have a pmid predicate; skipping', subject)
            continue
        elif not _pmid_pattern.match(pmid):
            _logger.info('Publication with subject URI %s has a bad pmid "%s"; skipping', subject, pmid)
        pmids.add(pmid)
    _logger.debug('Got %d pmids', len(pmids))
    return pmids
