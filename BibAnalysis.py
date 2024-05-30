from tinydb import TinyDB,Query
from config import MAPTIER_API_KEY
from cerberus import Validator
# from validaterules import validate_rules
from scopus_integration import Article, Author, Affiliation
from openai_integration import GptChatBot
from excel_integration import ExcelIntegration
from zotero_integration import ZoteroIntegration
import json
import os
import requests
import re
from rich import print

class BibAnalysis:
    def __init__(self, *args, **kwargs):
        """
        Initialize the BibAnalysis class.

        Args:
            bib_database_path (str): The path to the database file. Defaults to "./data/bib_database.json".
        """
        self.bib_database_path = kwargs.get('bib_database_path', './data/bib_database.json')
        self.database = TinyDB(self.bib_database_path)
        self.chatbot = GptChatBot()
        self.zotero = ZoteroIntegration()

    def __str__(self):
        """Return the string representation of the class."""
        return f'bib class at path:{self.bib_database_path}\n have {len(self.database)} articles in database.'
    

if __name__ == '__main__':
    bib = BibAnalysis()
    print(bib.bib_database_path)
    print(bib)
    print('BibAnalysis class is working fine.')
    a = Article("10.1016/j.engstruct.2022.115574")
    # 待完善
    # pdfpath = a.get_pdf_from_zotero()
    # 待完善后删掉'F:'
    pdfpath = 'F:'+bib.zotero.get_pdf_path_from_collection_name('mergedris20240208', '10.1016/j.engstruct.2022.115574')
    bib.chatbot.add_pdf_to_chat(pdfpath)
    bib.chatbot.get_response("please analysis article 11", jsonmode=False)

