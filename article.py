from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval
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

        # 首先检查tinydb中是否有这个文章的信息，如果有就直接读取，如果没有就调用pybliometrics获取（待实现）
        # 读取tinydb中的信息
        # self._read_from_db(identifier, id_type)
            
        # 利用pybliometrics获得文章的摘要信息
        ab = AbstractRetrieval(identifier)

        self._abattrlist = ["abstract", "affiliation", "authors", "aggregationType", "authkeywords", "authorgroup",
                            "citedby_count", "citedby_link", "chemicals", "confcode", "confdate", "conflocation",
                            "confname", "confsponsor", "contributor_group", "coverDate", "date_created", "description",
                            "doi", "eid", "endingPage", "funding", "funding_text", "isbn", "issn", "identifier",
                            "idxterms", "issueIdentifier", "issuetitle", "language", "openaccess", "openaccessFlag",
                            "pageRange", "pii", "publicationName", "publisher", "publisheraddress", "pubmed_id",
                            "refcount", "references", "scopus_link", "self_link", "sequencebank", "source_id",
                            "source_type", "startingPage", "subject_areas", "title", "url", "volume", "website"]

        # 将ab中的所有属性字段赋给self
        for attr in self._abattrlist:
            if hasattr(ab, attr):
                # 如果ab中有这个属性，就赋值给self
                setattr(self, attr, ab.__getattribute__(attr))
            else:
                # 如果ab中没有这个属性，就赋值为None
                setattr(self, attr, None)
        
class Author:
    def __init__(self,author_id: Union[int, str]) -> None:
        """
        class that stores the author information
        :param author_id: The ID or the EID of the author.
        """

        au = AuthorRetrieval(author_id)
        self._authorattrlist = ["affiliation_current", "affiliation_history", "alias", "citation_count", "cited_by_count",
                                "classificationgroup", "coauthor_count", "coauthor_link", "date_created", "document_count",
                                "eid", "given_name", "h_index", "historical_identifier", "identifier", "indexed_name",
                                "initials", "name_variants", "orcid", "publication_range", "scopus_author_link",
                                "search_link", "self_link", "status", "subject_areas", "surname", "url"]
        # 将au中的所有属性字段赋给self
        for attr in self._authorattrlist:
            if hasattr(au, attr):
                # 如果au中有这个属性，就赋值给self
                setattr(self, attr, au.__getattribute__(attr))
            else:
                # 如果au中没有这个属性，就赋值为None
                setattr(self, attr, None)



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
author_id1 = a.authors[0].auid
print(author_id1)

au1 = Author(author_id1)


print(config['Authentication']['APIKey'])  # Show keys
config['Proxy']['https'] = 'https://127.0.0.1:7890'  # Redefine proxy


