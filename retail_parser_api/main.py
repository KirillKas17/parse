"""
Главный скрипт для запуска парсеров всех retail-сетей.
Ищет продукцию Барнаульского Молочного Комбината и связанных брендов.
"""
import json
import csv
from datetime import datetime
from typing import List, Dict

# Импортируем все парсеры
from parsers.base import Product
from parsers.bystronom import BystronomParser
from parsers.yarcheplus import YarchePlusParser
from parsers.metro import MetroParser
from parsers.okmarket import OKMarketParser
from parsers.begemag import BegemagParser
from parsers.monetka import MonetkaParser
from parsers.yandex_lavka import YandexLavkaParser
from parsers.samokat import SamokatParser
from parsers.komandor import KomandorParser
from parsers.pyaterochka import PyaterochkaParser
from parsers.auchan import AuchanParser
from parsers.lenta import LentaParser
from parsers.chizhik import ChizhikParser
from parsers.magnit import MagnitParser


# Список всех парсеров с названиями сетей
PARSERS = [
    ("Быстроном", BystronomParser),
    ("Ярче+", YarchePlusParser),
    ("МЕТРО", MetroParser),
    ("О'КЕЙ", OKMarketParser),
    ("Бегемаг", BegemagParser),
    ("Монетка", MonetkaParser),
    ("Яндекс.Лавка", YandexLavkaParser),
    ("Самокат", SamokatParser),
    ("Командор", KomandorParser),
    ("Пятёрочка", PyaterochkaParser),
    ("АШАН", AuchanParser),
    ("ЛЕНТА", LentaParser),
    ("Чижик", ChizhikParser),
    ("Магнит", MagnitParser),
]


def run_parser(parser_class, shop_name: str) -> List[Product]:
    """Запуск одного парсера с обработкой ошибок"""
    print(f"\n{'='*60}")
    print(f"🛒 Запуск парсинга: {shop_name}")
    print(f"{'='*60}")
    
    try:
        parser = parser_class()
        products = parser.parse()
        return products
    except Exception as e:
        print(f"❌ Ошибка при парсинге {shop_name}: {e}")
        return []


def save_results(all_products: List[Product], output_format: str = "both"):
    """Сохранение результатов в JSON и CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    products_data = [p.to_dict() for p in all_products]
    
    results = {
        "timestamp": timestamp,
        "total_products": len(products_data),
        "shops": list(set(p["shop"] for p in products_data)),
        "products": products_data
    }
    
    if output_format in ("json", "both"):
        json_filename = f"results/bmk_products_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON сохранён: {json_filename}")
    
    if output_format in ("csv", "both"):
        csv_filename = f"results/bmk_products_{timestamp}.csv"
        if products_data:
            fieldnames = ["shop", "name", "price", "currency", "brand", "manufacturer", "url", "image_url", "weight"]
            with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for product in products_data:
                    writer.writerow({k: product.get(k, '') for k in fieldnames})
            print(f"✓ CSV сохранён: {csv_filename}")
    
    return results


def main():
    """Основная функция запуска"""
    print("="*60)
    print("🔍 Парсер продукции Барнаульского Молочного Комбината")
    print("   Производители: БМК, Логовская сыроварня")
    print("   Бренды: Лакт, Молочная сказка, Модест, Чуйский, Частица Алтая, Сибирское подворье, Ромбер")
    print("="*60)
    
    all_products: List[Product] = []
    
    for shop_name, parser_class in PARSERS:
        products = run_parser(parser_class, shop_name)
        all_products.extend(products)
    
    print(f"\n{'='*60}")
    print("📊 ИТОГИ ПАРСИНГА")
    print(f"{'='*60}")
    print(f"Всего найдено товаров: {len(all_products)}")
    
    by_shop: Dict[str, int] = {}
    for p in all_products:
        by_shop[p.shop] = by_shop.get(p.shop, 0) + 1
    
    print("\nПо магазинам:")
    for shop, count in sorted(by_shop.items()):
        print(f"  • {shop}: {count} товаров")
    
    if all_products:
        save_results(all_products, "both")
    else:
        print("\n⚠️ Товары не найдены. Возможно, сайты используют JS или защиту от ботов.")
        print("   Попробуйте запустить с другими настройками или проверить селекторы.")
    
    print(f"\n{'='*60}")
    print("✅ Парсинг завершён!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
