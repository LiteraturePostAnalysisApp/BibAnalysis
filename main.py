from tinydb import TinyDB,Query
from config import MAPTIER_API_KEY
from cerberus import Validator
from validaterules import validate_rules
from excel_interaction import ExcelInteraction
import json
import os
import requests
import re

class BibAnalysis:
    def __init__(self, *args, **kwargs):
        """
        Initialize the BibAnalysis class.

        Args:
            bib_database_path (str): The path to the database file. Defaults to "./data/bib_database.json".
        """
        self.bib_database_path = kwargs.get('bib_database_path', './data/bib_database.json')
        self.database = TinyDB(self.bib_database_path)
    
    
