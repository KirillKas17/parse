from typing import List
from .base import BaseParser, Product
class ChizhikParser(BaseParser):
    def __init__(self):
        super().__init__("Чижик")
        self.base_url = "https://chizhik.club"
        self.catalog_urls = ["https://chizhik.club/catalog/moloko-i-molochnye-produkty/"]
    def parse(self) -> List[Product]:
        products = []
        for url in self.catalog_urls:
            print(f"[{self.shop_name}] Загрузка: {url}")
            soup = self.get_soup(url)
            if not soup: continue
            cards = soup.select('.product-item, [class*="product"]')
            print(f"[{self.shop_name}] Найдено: {len(cards)}")
            for c in cards[:50]:
                try:
                    n = c.select_one('.name, .title, h3')
                    name = n.get_text(strip=True) if n else ""
                    if len(name) < 3: continue
                    p = c.select_one('.price, [class*="price"]')
                    price = self.extract_price(p.get_text(strip=True) if p else "0")
                    a = c.select_one('a[href]')
                    href = a.get('href') if a else None
                    url_f = f"{self.base_url}{href}" if href and href.startswith('/') else (href or "")
                    i = c.select_one('img')
                    img = i.get('src') if i else ""
                    if self.matches_criteria(name):
                        products.append(Product(name=name, price=price, url=url_f, image_url=img, shop=self.shop_name))
                except: pass
        print(f"[{self.shop_name}] Всего: {len(products)}")
        self.products = products
        return products
