"""
Базовый класс для парсеров ритейл-сетей.
Реализует фильтрацию по производителям и брендам.
Использует httpx + BeautifulSoup для парсинга.
"""
import re
import httpx
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup


@dataclass
class Product:
    """Модель товара"""
    name: str
    price: float
    currency: str = "RUB"
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    weight: Optional[str] = None
    shop: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseParser(ABC):
    """Базовый класс парсера"""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    # Ключевые слова производителей (ищем в названии и описании)
    MANUFACTURERS = [
        "барнаульский молочный комбинат",
        "барнаульский молочный",
        "бмк",
        "логовская сыроварня",
        "ао бмк",
        "ао барнаульский молочный комбинат"
    ]
    
    # Бренды (ищем в названии товара и поле бренда)
    BRANDS = [
        "лакт",
        "молочная сказка",
        "модест",
        "чуйский",
        "логовская сыроварня",
        "частица алтая",
        "сибирское подворье",
        "ромбер",
        "romber"
    ]
    
    def __init__(self, shop_name: str):
        self.shop_name = shop_name
        self.products: List[Product] = []
        self.client = httpx.Client(headers=self.HEADERS, timeout=30.0, follow_redirects=True)
    
    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Получение HTML и парсинг через BeautifulSoup"""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"[{self.shop_name}] Ошибка загрузки {url}: {e}")
            return None
    
    @abstractmethod
    def parse(self) -> List[Product]:
        """Основной метод парсинга. Должен быть реализован в наследниках."""
        pass
    
    def matches_criteria(self, name: str, brand: Optional[str] = None, 
                        description: Optional[str] = None) -> bool:
        """
        Проверка товара на соответствие критериям поиска.
        Возвращает True, если товар подходит по производителю ИЛИ бренду.
        """
        text_to_check = f"{name} {brand or ''} {description or ''}".lower()
        
        # Проверка по производителям
        for manufacturer in self.MANUFACTURERS:
            if manufacturer in text_to_check:
                return True
        
        # Проверка по брендам
        for brand_name in self.BRANDS:
            if brand_name in text_to_check:
                return True
        
        return False
    
    def extract_price(self, price_str: str) -> float:
        """Извлечение цены из строки"""
        if not price_str:
            return 0.0
        
        # Удаляем всё кроме цифр, точки и запятой
        cleaned = re.sub(r'[^\d.,]', '', str(price_str))
        if not cleaned:
            return 0.0
        
        # Заменяем запятую на точку
        cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def save_results(self, filename: Optional[str] = None):
        """Сохранение результатов в JSON"""
        import json
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/{self.shop_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([p.to_dict() for p in self.products], f, ensure_ascii=False, indent=2)
        
        print(f"✓ Сохранено {len(self.products)} товаров в {filename}")
        return filename
