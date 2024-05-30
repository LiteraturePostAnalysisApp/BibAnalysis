from config import ZOTERO_LIBRARY_ID, ZOTERO_API_KEY, LIVRARY_TYPE
from pyzotero import zotero
from scopus_integration import Article
import os
from functools import lru_cache

class ZoteroIntegration():
    def __init__(self, zotero_api_key:str=ZOTERO_API_KEY, zotero_library_id:str=ZOTERO_LIBRARY_ID, library_type:str=LIVRARY_TYPE):
        self.zot = zotero.Zotero(zotero_library_id, library_type, zotero_api_key)
        self.storage_path = "\Zotero\storage"

    # 还没写，获取zotero在电脑上的存储路径，比如F:\Zotero\storage，则返回F:，函数完成后应修改__init__函数和单元测试代码 
    # @property
    # @lru_cache(maxsize=1)
    # def storage_path(self):
    #     """return the storage path of the zotero."""
    #     raise NotImplementedError
    #     return system_storage_path

    @lru_cache(maxsize=100)
    def _collections(self):
        """return all obj of collection."""
        return self.zot.collections()

    @property
    def collections(self):
        """return all collections name in the library."""
        return [coll['data']['name'] for coll in self._collections()]
    
    @lru_cache(maxsize=1000)
    def item(self,itemkey:str):
        """return the item by key."""
        return self.zot.item(itemkey)['data']['title']

    @lru_cache(maxsize=100)
    def findcollection(self,collname:str,full_info:bool=False):
        """find the collection by name and return the key of the collection."""
        colls = self._collections() # 所有集合对象
        # 查找待分析的集合
        for coll in colls:
            if coll['data']['name'] == collname:
                if full_info:
                    print(coll)
                return coll['key']
        raise ValueError(f"The collection:{collname} is not in the library.")

    @lru_cache(maxsize=1000)        
    def find_item_in_collection(self, collkey:str,article_doi:str):
        """find the item in the collection by key and return the key of the item."""
        items = self.get_collection_items(collkey)
        for item in items:
            print(item['data']['DOI'])
            if item['data']['DOI'] == article_doi:
                itemkey = item['key']
                return itemkey
        raise ValueError(f"The item with doi:{article_doi} is not in the collection.")

    @lru_cache(maxsize=1000)       
    def get_collection_items(self, collkey:str):
        """return all items in the collection."""
        return self.zot.collection_items(collkey)
    
    @lru_cache
    def get_file_path(self, itemkey:str):
        """get the file path of the item."""
        items = self.zot.children(item_key)
        for item in items:
            if item['data']['contentType'] == 'application/pdf':
                key = item['key']
                filename = item['data']['filename']
                attachment_path = os.path.join(self.storage_path, key, filename)
                return attachment_path
        return None


    def get_pdf_path_from_collection_name(self,collname:str,article_doi:str):
        """get the pdf path from the collection name and article doi."""
        collkey = self.findcollection(collname)
        itemkey = self.find_item_in_collection(collkey,article_doi)
        return self.get_file_path(itemkey)

if __name__ == '__main__':
    zot = ZoteroIntegration()
    colls = zot.collections # 所有集合名称
    print(colls)
    # 查找待分析的集合
    collkey = zot.findcollection('mergedris20240208')
    print(f"collkey:{collkey}")
    # 可以获得集合中的所有文献
    # pyz = zot.collection_items(collkey)

    # 在集合中查找某篇文献
    doi = "10.1016/j.engstruct.2022.115574"
    item_key = zot.find_item_in_collection(collkey,doi)
    print(f"item_key:{item_key}")

    # 获取附件（假设附件为子条目）
    filepath = zot.get_file_path(item_key)
    print(f"filepath:{filepath}")
    
    # 读取附件
    with open('F:'+ filepath, 'rb') as f:
        print(f.read(100))

