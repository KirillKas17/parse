"""
Парсер для сети Ярче+ (yarcheplus.ru) - Камелот-А ООО
"""
from typing import List
from .base import BaseParser, Product


class YarchePlusParser(BaseParser):
    """Парсер для yarcheplus.ru"""
    
    def __init__(self):
        super().__init__("Ярче+")
        self.base_url = "https://yarcheplus.ru"
        self.catalog_urls = [
            "https://yarcheplus.ru/catalog/moloko-i-molochnye-produkty/",
            "https://yarcheplus.ru/catalog/syry/",
        ]
    
    def parse(self) -> List[Product]:
        products = []
        for url in self.catalog_urls:
            print(f"[{self.shop_name}] Загрузка: {url}")
            soup = self.get_soup(url)
            if not soup:
                continue
            cards = soup.select('.product-item, .catalog-item, [class*="product"]')
            print(f"[{self.shop_name}] Найдено элементов: {len(cards)}")
            for card in cards[:50]:
                try:
                    name_el = card.select_one('.name, .title, h3, a[href]')
                    name = name_el.get_text(strip=True) if name_el else ""
                    if not name or len(name) < 3:
                        continue
                    price_el = card.select_one('.price, .cost, [class*="price"]')
                    price = self.extract_price(price_el.get_text(strip=True) if price_el else "0")
                    link_el = card.select_one('a[href]')
                    href = link_el.get('href') if link_el else None
                    url_full = f"{self.base_url}{href}" if href and href.startswith('/') else (href or "")
                    img_el = card.select_one('img')
                    img_url = img_el.get('src') if img_el else ""
                    if self.matches_criteria(name):
                        products.append(Product(name=name, price=price, url=url_full, image_url=img_url, shop=self.shop_name))
                        print(f"  ✓ {name[:40]}... - {price} ₽")
                except Exception:
                    continue
        print(f"[{self.shop_name}] Всего: {len(products)}")
        self.products = products
        return products
