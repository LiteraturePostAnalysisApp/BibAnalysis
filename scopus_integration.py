from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
from pybliometrics.scopus.utils import config as pybliometrics_config
from collections import defaultdict, namedtuple
from typing import Union
import pyzotero
from loguru import logger
import requests
from bs4 import BeautifulSoup

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
        try:
            super().__init__(identifier=identifier, refresh=refresh, view=view,
                             id_type=id_type, **kwds)
            logger.info(f"Article Info of DOI:{identifier} Get!")
        except Exception as e:
            logger.error(f"Fail to get Article Info of DOI:{identifier}! \n Mainly because of VPN Usage or Network Error, Detail:\n{e}")
        # Define attributes
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


        
    def save_to_database(self, db) -> int:
        """save the article to database in class Bibanalysis,and return the doc_id"""
        raise NotImplementedError
        doc_id = db.insert(self.data)
        logger.info(f"Article Info of DOI:{self.identifier} Save to Database with doc_id:{doc_id}")
        return doc_id
    
    def get_pdf_from_zotero(self, zotero_api_key, zotero_user_id, zotero_collection_id):
        """get the pdf from zotero"""
        raise NotImplementedError
        return pdf_path
    
    def add_to_zotero(self, zotero_api_key, zotero_user_id, zotero_collection_id):
        """add the article to zotero"""
        raise NotImplementedError
        if self.get_pdf_from_scihub():
            zotero_item_key = zotero.add_item(self.data)
        logger.info(f"Article Info of DOI:{self.identifier} Add to Zotero with item_key:{zotero_item_key}")
        return zotero_item_key
    
    def get_pdf_from_scihub(self, doi=None):
        """get the pdf from scihub, return the pdf file name
        if doi is not specified, use the doi of the current article"""
        scihub_url = 'https://sci-hub.se/'
        if not doi:
            doi = self.doi
        search_url = scihub_url + doi
        
        # Step 1: Get the SciHub page for the DOI
        response = requests.get(search_url)
        if response.status_code != 200:
            raise Exception('Failed to retrieve the page from SciHub')

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Step 2: Find the PDF download link in the page
        iframe = soup.find('iframe')
        if not iframe:
            raise Exception('PDF link not found on SciHub page')
        
        pdf_url = iframe.get('src')
        if not pdf_url.startswith('http'):
            pdf_url = 'https:' + pdf_url
        
        # Step 3: Download the PDF
        pdf_response = requests.get(pdf_url, stream=True)
        if pdf_response.status_code != 200:
            logger.warning('Failed to download the PDF from SciHub')
            raise Exception('Failed to download the PDF from SciHub')
        
        file_name = f'{doi.replace("/", "_")}.pdf'
        with open(file_name, 'wb') as pdf_file:
            for chunk in pdf_response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)
        
        logger.info(f'PDF successfully downloaded as {file_name}')
        return file_name

    def refresh(self):
        """refresh the article"""
        self.__init__(identifier=self.identifier, refresh=True)
        logger.info(f"Article Info of DOI:{self.identifier} Refreshed!")
        
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
        try:
            super().__init__(author_id, refresh, view, **kwds)
            logger.info(f"Author Info of author_id:{author_id} Get!")
        except Exception as e:
            logger.error(f"Fail to get Article Info of DOI:{author_id}! \n Mainly because of VPN Usage or Network Error, Detail:\n{e}")
        self._attrlist = ["affiliation_current", "affiliation_history", "alias", "citation_count", "cited_by_count",
                            "classificationgroup", "coauthor_count", "coauthor_link", "date_created", "document_count",
                            "eid", "given_name", "h_index", "historical_identifier", "identifier", "indexed_name",
                            "initials", "name_variants", "orcid", "publication_range", "scopus_author_link",
                            "search_link", "self_link", "status", "subject_areas", "surname", "url"]

    def refresh(self):
        """refresh the author"""
        self.__init__(author_id=self.author_id, refresh=True)
        logger.info(f"Author Info of author_id:{self.author_id} Refreshed!")



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
        try:
            super().__init__(aff_id,refresh,view,**kwds)
            logger.info(f"Affiliation Info of aff_id:{aff_id} Get!")
        except Exception as e:
            logger.error(f"Fail to get Article Info of DOI:{aff_id}! \n Mainly because of VPN Usage or Network Error, Detail:\n{e}")
        self._attrlist = ["address", "affiliation_name", "author_count", "city", "country", "date_created",
                            "document_count", "eid", "identifier", "name_variants", "org_domain", "org_type",
                            "org_URL", "postal_code", "scopus_affiliation_link", "self_link", "search_link", "state",
                            "status", "sort_name", "url"]

    def refresh(self):
        """refresh the affiliation"""
        self.__init__(aff_id=self.aff_id, refresh=True)
        logger.info(f"Affiliation Info of aff_id:{self.aff_id} Refreshed!")

if __name__ == "__main__":
    a = Article("10.1016/j.softx.2019.100263")
    pdf_file = a.get_pdf_from_scihub()
    a.refresh()
    print(a)
    print(a.authors)
    author_id1 = a.authors[0].auid
    au1 = Author(author_id1)
    print(au1)