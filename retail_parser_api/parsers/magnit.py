"""Generic parser template - will be customized"""
from typing import List
from .base import BaseParser, Product

class GenericParser(BaseParser):
    def __init__(self, name="Generic", base="https://example.com", urls=None):
        super().__init__(name)
        self.base_url = base
        self.catalog_urls = urls or [f"{base}/catalog/"]
    
    def parse(self) -> List[Product]:
        products = []
        print(f"[{self.shop_name}] Парсер-заглушка. Требуется настройка селекторов.")
        self.products = products
        return products
