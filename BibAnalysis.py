from tinydb import TinyDB,Query
from config import MAPTIER_API_KEY
from cerberus import Validator
# from validaterules import validate_rules
from scopus_integration import Article, Author, Affiliation
from openai_integration import GptChatBot
from excel_interaction import ExcelInteraction
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

    def __str__(self):
        """Return the string representation of the class."""
        return f'bib class at path:{self.bib_database_path}\n have {len(self.database)} articles in database.'
    

if __name__ == '__main__':
    bib = BibAnalysis()
    print(bib.bib_database_path)
    print(bib)
    print('BibAnalysis class is working fine.')
    a = Article("10.1016/j.engstruct.2022.115574")
    pdfpath = a.get_pdf_from_zotero()
    bib.chatbot.add_pdf_to_chat(pdfpath)
    bib.chatbot.get_response("please analysis article 11", jsonmode=False)

