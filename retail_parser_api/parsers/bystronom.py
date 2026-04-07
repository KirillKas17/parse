"""
Парсер для сети Быстроном (bystronom.ru)
"""
from typing import List
from .base import BaseParser, Product


class BystronomParser(BaseParser):
    """Парсер для bystronom.ru"""
    
    def __init__(self):
        super().__init__("Быстроном")
        self.base_url = "https://bystronom.ru"
        self.catalog_urls = [
            "https://bystronom.ru/catalog/moloko-i-molochnye-produkty/",
            "https://bystronom.ru/catalog/syry/",
        ]
    
    def parse(self) -> List[Product]:
        """Парсинг каталога Быстроном"""
        products = []
        
        for catalog_url in self.catalog_urls:
            print(f"[{self.shop_name}] Загрузка: {catalog_url}")
            soup = self.get_soup(catalog_url)
            
            if not soup:
                continue
            
            product_cards = soup.select('.product-item, .catalog-item, .item-card, .product-card')
            if not product_cards:
                product_cards = soup.select('[class*="product"], [class*="item"]')
            
            print(f"[{self.shop_name}] Найдено элементов: {len(product_cards)}")
            
            for card in product_cards[:50]:
                try:
                    name_el = card.select_one('.name, .title, h3, a[href*="/product/"]')
                    name = name_el.get_text(strip=True) if name_el else ""
                    
                    if not name or len(name) < 3:
                        continue
                    
                    price_el = card.select_one('.price, .cost, [class*="price"]')
                    price_str = price_el.get_text(strip=True) if price_el else "0"
                    price = self.extract_price(price_str)
                    
                    link_el = card.select_one('a[href]')
                    href = link_el.get('href') if link_el else None
                    url_full = f"{self.base_url}{href}" if href and href.startswith('/') else (href or "")
                    
                    img_el = card.select_one('img')
                    img_src = img_el.get('src') if img_el else None
                    img_url = f"{self.base_url}{img_src}" if img_src and img_src.startswith('/') else (img_src or "")
                    
                    if self.matches_criteria(name):
                        product = Product(name=name, price=price, url=url_full, image_url=img_url, shop=self.shop_name)
                        products.append(product)
                        print(f"  ✓ Найдено: {name[:50]}... - {price} ₽")
                except Exception:
                    continue
        
        print(f"[{self.shop_name}] Всего найдено целевых товаров: {len(products)}")
        self.products = products
        return products
