"""
Парсер для сети МЕТРО (metro-cc.ru)
"""
from typing import List
from .base import BaseParser, Product


class MetroParser(BaseParser):
    def __init__(self):
        super().__init__("МЕТРО")
        self.base_url = "https://online.metro-cc.ru"
        self.catalog_urls = ["https://online.metro-cc.ru/category/molochnye-produkty-yajca"]
    
    def parse(self) -> List[Product]:
        products = []
        for url in self.catalog_urls:
            print(f"[{self.shop_name}] Загрузка: {url}")
            soup = self.get_soup(url)
            if not soup:
                continue
            cards = soup.select('.product-tile, [class*="product"], [data-testid*="product"]')
            print(f"[{self.shop_name}] Найдено элементов: {len(cards)}")
            for card in cards[:50]:
                try:
                    name_el = card.select_one('h3, .title, [data-testid*="title"]')
                    name = name_el.get_text(strip=True) if name_el else ""
                    if not name or len(name) < 3:
                        continue
                    price_el = card.select_one('.price, [class*="price"], [data-testid*="price"]')
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
