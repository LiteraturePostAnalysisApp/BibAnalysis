from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
from pybliometrics.scopus.utils import config
from collections import defaultdict, namedtuple
from typing import Union

class Article(AbstractRetrieval):
    def __init__(self,
                 identifier: Union[int, str] = None,
                 refresh: Union[bool, int] = False,
                 view: str = 'META_ABS',
                 id_type: str = None,
                 **kwds: str
                 ) -> None:
        """Interaction with the Abstract Retrieval API.

        :param identifier: The identifier of a document.  Can be the Scopus EID
                           , the Scopus ID, the PII, the Pubmed-ID or the DOI.
        :param refresh: Whether to refresh the cached file if it exists or not.
                        If int is passed, cached file will be refreshed if the
                        number of days since last modification exceeds that value.
        :param id_type: The type of used ID. Allowed values: None, 'eid', 'pii',
                        'scopus_id', 'pubmed_id', 'doi'.  If the value is None,
                        the function tries to infer the ID type itself.
        :param view: The view of the file that should be downloaded.  Allowed
                     values: META, META_ABS, REF, FULL, where FULL includes all
                     information of META_ABS view and META_ABS includes all
                     information of the META view.  For details see
                     https://dev.elsevier.com/sc_abstract_retrieval_views.html.
        :param kwds: Keywords passed on as query parameters.  Must contain
                     fields and values listed in the API specification at
                     https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl.

        Raises
        ------
        ValueError
            If any of the parameters `id_type`, `refresh` or `view` is not
            one of the allowed values.

        Notes
        -----
        The directory for cached results is `{path}/{view}/{identifier}`,
        where `path` is specified in your configuration file.  In case
        `identifier` is a DOI, an underscore replaces the forward slash.
        """
        # Initialize
        super().__init__(identifier=identifier, refresh=refresh, view=view,
                         id_type=id_type, api='AbstractRetrieval', **kwds)
        self._attrlist = ['abstract', 'affiliation', 'aggregationType',
                            'authkeywords', 'authorgroup', 'authors', 'citedby_count',
                            'citedby_link', 'chemicals', 'confcode', 'confdate',
                            'conflocation', 'confname', 'confsponsor',
                            'contributor_group', 'copyright', 'copyright_type',
                            'correspondence', 'coverDate', 'date_created', 'description',
                            'doi', 'eid', 'endingPage', 'funding', 'funding_text',
                            'isbn', 'issn', 'identifier', 'idxterms', 'issueIdentifier',
                            'issuetitle', 'language', 'openaccess', 'openaccessFlag',
                            'pageRange', 'pii', 'publicationName', 'publisher',
                            'publisheraddress', 'pubmed_id', 'refcount', 'references',
                            'scopus_link', 'self_link', 'sequencebank', 'source_id',
                            'sourcetitle_abbreviation', 'srctype', 'startingPage',
                            'subject_areas', 'subtype', 'subtypedescription', 'title',
                            'url', 'volume', 'website']
        
    def save_to_database(self, db: TinyDB) -> int:
        """save the article to database in class Bibanalysis,and return the doc_id"""
        raise NotImplementedError
        doc_id = db.insert(self.data)
        return doc_id
    
    def get_pdf_from_zotero(self, zotero_api_key, zotero_user_id, zotero_collection_id):
        """get the pdf from zotero"""
        raise NotImplementedError
        return pdf_path
    
    def refresh(self):
        """refresh the article"""
        self.__init__(identifier=self.identifier, refresh=True)
        
class Author(AuthorRetrieval):
    def __init__(self, author_id: Union[int, str], refresh: Union[bool, int] = False, view: str = "ENHANCED", **kwds: str):
        """
        Interaction with the Author Retrieval API.
        :param author_id: The ID or the EID of the author.
        :param refresh: Whether to refresh the cached file if it exists or not.
                        If int is passed, cached file will be refreshed if the
                        number of days since last modification exceeds that value.
        :param view: The view of the file that should be downloaded. Allowed
                     values: `METRICS`, `LIGHT`, `STANDARD`, `ENHANCED`, where `STANDARD`
                     includes all information of `LIGHT` view and `ENHANCED`
                     includes all information of any view. For details see
                     https://dev.elsevier.com/sc_author_retrieval_views.html.
                     Note: Neither the `BASIC` nor the `DOCUMENTS` view are active,
                     although documented.
        :param kwds: Keywords passed on as query parameters. Must contain
                     fields and values mentioned in the API specification at
                     https://dev.elsevier.com/documentation/AuthorRetrievalAPI.wadl.
        Raises
        ------
        ValueError
            If any of the parameters `refresh` or `view` is not
            one of the allowed values.
        Notes
        -----
        The directory for cached results is `{path}/ENHANCED/{author_id}`,
        where `path` is specified in your configuration file, and `author_id`
        is stripped of an eventually leading `'9-s2.0-'`.
        """
        super().__init__(author_id, refresh, view, **kwds)
        self._attrlist = ["affiliation_current", "affiliation_history", "alias", "citation_count", "cited_by_count",
                            "classificationgroup", "coauthor_count", "coauthor_link", "date_created", "document_count",
                            "eid", "given_name", "h_index", "historical_identifier", "identifier", "indexed_name",
                            "initials", "name_variants", "orcid", "publication_range", "scopus_author_link",
                            "search_link", "self_link", "status", "subject_areas", "surname", "url"]

    def refresh(self):
        """refresh the author"""
        self.__init__(author_id=self.author_id, refresh=True)


class Affiliation(AffiliationRetrieval):
    def __init__(self,aff_id: Union[int, str],refresh: Union[bool, int] = False,view: str = "STANDARD",**kwds: str) -> None:
        """
        Interaction with the Affiliation Retrieval API.
        :param aff_id: Scopus ID or EID of the affiliation profile.
        :param refresh: Whether to refresh the cached file if it exists or not.
                        If int is passed, cached file will be refreshed if the
                        number of days since last modification exceeds that value.
        :param view: The view of the file that should be downloaded. Allowed
                     values: `LIGHT`, `STANDARD`, where `STANDARD` includes all
                     information of the `LIGHT` view. For details see
                     https://dev.elsevier.com/sc_affil_retrieval_views.html.
                     Note: Neither the `BASIC` view nor `DOCUMENTS` or `AUTHORS`
                     views are active, although documented.
        :param kwds: Keywords passed on as query parameters. Must contain
                     fields and values mentioned in the API specification at
                     https://dev.elsevier.com/documentation/AffiliationRetrievalAPI.wadl.
        Raises
        ------
        ValueError
            If any of the parameters `refresh` or `view` is not
            one of the allowed values.
        Notes
        -----
        The directory for cached results is `{path}/{view}/{aff_id}`,
        where `path` is specified in your configuration file.
        """
        super().__init__(aff_id,refresh,view,**kwds)
        self._attrlist = ["address", "affiliation_name", "author_count", "city", "country", "date_created",
                            "document_count", "eid", "identifier", "name_variants", "org_domain", "org_type",
                            "org_URL", "postal_code", "scopus_affiliation_link", "self_link", "search_link", "state",
                            "status", "sort_name", "url"]

    def refresh(self):
        """refresh the affiliation"""
        self.__init__(aff_id=self.aff_id, refresh=True)
        
if __name__ == "__main__":
    a = Article("10.1016/j.softx.2019.100263")
    print(a)
    print(a.authors)
    author_id1 = a.authors[0].auid
    au1 = Author(author_id1)



