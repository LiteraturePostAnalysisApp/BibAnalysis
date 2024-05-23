from pybliometrics.scopus import AbstractRetrieval
from pybliometrics.scopus.utils import config
from collections import defaultdict, namedtuple
from typing import List, NamedTuple, Optional, Tuple, Union

class Article:
    def __init__(self, identifier: str, id_type: str = None):
        """
        :param identifier: The identifier of a document. Can be the Scopus EID,
                           the Scopus ID, the PII, the Pubmed-ID, or the DOI.
        :param id_type: The type of used ID. Allowed values: None, 'eid', 'pii',
                        'scopus_id', 'pubmed_id', 'doi'. If the value is None,
                        the function tries to infer the ID type itself.
        """
        # 区分不同的ID类型，期望支持的ID类型有：eid, pii, scopus_id, pubmed_id, doi，目前只支持doi
        if id_type is None:
            id_type = detect_id_type(identifier)
        else:
            # allowed_id_types = ('eid', 'pii', 'scopus_id', 'pubmed_id', 'doi')
            allowed_id_types = ('doi')
            check_parameter_value(id_type, allowed_id_types, "id_type")

        # 利用pybliometrics获得文章的摘要信息
        ab = AbstractRetrieval(identifier)
        self.abstract: Optional[str] = ab.abstract
        self.affiliation: Optional[List[NamedTuple]] = ab.affiliation
        authors: Optional[List[NamedTuple]] = ab.authors
        # 每个Author的信息包括：affiliation_id, dptid, organization, city, postalcode, addresspart, country, collaboration, auid, orcid, indexed_name, surname, given_name
        # 下面利用每个Author的信息创建一个Author类的实例
        self.authors: Optional[list[Author]] = [Author(author) for author in authors]

        self.aggregationType: str = ab.aggregationType
        self.authkeywords: Optional[List[str]] = ab.authkeywords
        self.authorgroup: Optional[List[NamedTuple]] = ab.authorgroup
        self.citedby_count: Optional[int] = ab.citedby_count
        self.citedby_link: str = ab.citedby_link
        self.chemicals: Optional[List[NamedTuple]] = ab.chemicals
        self.confcode: Optional[int] = ab.confcode
        self.confdate: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = ab.confdate
        self.conflocation: Optional[str] = ab.conflocation
        self.confname: Optional[str] = ab.confname
        self.confsponsor: Optional[Union[List[str], str]] = ab.confsponsor
        self.contributor_group: Optional[List[NamedTuple]] = ab.contributor_group
        self.coverDate: str = ab.coverDate
        self.date_created: Optional[Tuple[int, int, int]] = ab.date_created
        self.description: Optional[str] = ab.description
        self.doi: Optional[str] = ab.doi
        self.eid: str = ab.eid
        self.endingPage: Optional[str] = ab.endingPage
        self.funding: Optional[List[NamedTuple]] = ab.funding
        self.funding_text: Optional[str] = ab.funding_text
        self.isbn: Optional[Tuple[str, ...]] = ab.isbn
        self.issn: Optional[NamedTuple] = ab.issn
        self.identifier: int = ab.identifier
        self.idxterms: Optional[List[str]] = ab.idxterms
        self.issueIdentifier: Optional[str] = ab.issueIdentifier
        self.issuetitle: Optional[str] = ab.issuetitle
        self.language: Optional[str] = ab.language
        self.openaccess: Optional[int] = ab.openaccess
        self.openaccessFlag: Optional[bool] = ab.openaccessFlag
        self.pageRange: Optional[str] = ab.pageRange
        self.pii: Optional[str] = ab.pii
        self.publicationName: Optional[str] = ab.publicationName
        self.publisher: Optional[str] = ab.publisher
        self.publisheraddress: Optional[str] = ab.publisheraddress
        self.pubmed_id: Optional[int] = ab.pubmed_id
        self.refcount: Optional[int] = ab.refcount
        self.references: Optional[List[NamedTuple]] = ab.references
        self.scopus_link: str = ab.scopus_link
        self.self_link: str = ab.self_link
        self.sequencebank: Optional[List[NamedTuple]] = ab.sequencebank
        self.source_id: Optional[str] = ab.source_id
        self.source_type: Optional[str] = ab.source_type
        self.startingPage: Optional[str] = ab.startingPage
        self.subject_areas: Optional[List[str]] = ab.subject_areas
        self.title: str = ab.title
        self.url: str = ab.url
        self.volume: Optional[str] = ab.volume
        self.website: Optional[str] = ab.website

class Author:
    def __init__(self) -> None:
        pass

def check_parameter_value(parameter, allowed, name):
    """Raise a ValueError if a parameter value is not in the set of
    allowed values.
    """
    if parameter not in allowed:
        raise ValueError(f"Parameter '{name}' must be one of {', '.join(allowed)}.")
        
def detect_id_type(sid):
    """Method that tries to infer the type of abstract ID.

    Parameters
    ----------
    sid : str
        The ID of an abstract on Scopus.

    Raises
    ------
    ValueError
        If the ID type cannot be inferred.

    Notes
    -----
    Scopus IDs and Pubmed IDs are sometimes hard to distinguish.  If you
    work with both types, consider specifying the ID type manually.
    """
    sid = str(sid)
    if not sid.isnumeric():
        if sid.startswith('1-s2.0-') or sid.startswith('2-s2.0-'):
            id_type = 'eid'
        elif '/' in sid or "." in sid:
            id_type = 'doi'
        elif 16 <= len(sid) <= 17:
            id_type = 'pii'
    else:
        if len(sid) < 10:
            id_type = 'pubmed_id'
        else:
            id_type = 'scopus_id'
    try:
        return id_type
    except UnboundLocalError:
        raise ValueError(f'ID type detection failed for "{sid}".')



ab = AbstractRetrieval("10.1016/j.softx.2019.100263")

a = Article("10.1016/j.softx.2019.100263")
print(a)


print(config['Authentication']['APIKey'])  # Show keys
config['Proxy']['https'] = 'https://127.0.0.1:7890'  # Redefine proxy


