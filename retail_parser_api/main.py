"""
Парсер retail-сетей для поиска товаров производителей:
- Барнаульский Молочный комбинат (АО БМК)
- Логовская сыроварня

И брендов:
- Лакт, Молочная сказка, Модест, Чуйский
- Логовская сыроварня, Частица Алтая, Сибирское подворье
- Ромбер, Romber
"""

import asyncio
import json
from datetime import datetime

from retail_parser_api import RetailParserAPI


async def parse_all_chains():
    """Основная функция для парсинга всех сетей."""
    
    # Создаем конфигуратор с headless=True для работы без GUI
    async with RetailParserAPI(headless=True) as api:
        print("=" * 60)
        print("ПАРСЕР RETAIL-СЕТЕЙ")
        print("=" * 60)
        print(f"\nЦелевые производители:")
        for mfr in api.MANUFACTURERS:
            print(f"  - {mfr}")
        print(f"\nЦелевые бренды:")
        for brand in api.BRANDS:
            print(f"  - {brand}")
        print(f"\nСети для парсинга ({len(api.CHAINS)}):")
        for chain in api.CHAINS:
            print(f"  - {chain['name']}: {chain['url']}")
        print()

        all_found_products = []

        # Проходим по каждой сети
        for chain in api.CHAINS:
            print(f"\n{'='*60}")
            print(f"Парсинг сети: {chain['name']}")
            print(f"URL: {chain['url']}")
            print(f"{'='*60}")

            try:
                # Поиск целевых товаров в сети
                products = await api.Catalog.find_target_products(chain)
                
                if products:
                    print(f"✓ Найдено {len(products)} товаров")
                    
                    # Добавляем информацию о сети к каждому товару
                    for product in products:
                        product['chain_name'] = chain['name']
                        product['chain_url'] = chain['url']
                        product['parsed_at'] = datetime.now().isoformat()
                    
                    all_found_products.extend(products)
                    
                    # Выводим краткую информацию о найденных товарах
                    for i, product in enumerate(products[:10], 1):  # Первые 10
                        name = product.get('name', 'Без названия')
                        brand = product.get('brand', product.get('manufacturer', 'Н/Д'))
                        price = product.get('price', product.get('current_price', 'Н/Д'))
                        print(f"  {i}. {name[:50]}... - {brand} ({price} ₽)")
                    
                    if len(products) > 10:
                        print(f"  ... и ещё {len(products) - 10} товаров")
                else:
                    print(f"✗ Товары не найдены")
                    
            except Exception as e:
                print(f"✗ Ошибка при парсинге {chain['name']}: {e}")

        # Итоги
        print(f"\n{'='*60}")
        print(f"ИТОГИ ПАРСИНГА")
        print(f"{'='*60}")
        print(f"Всего найдено товаров: {len(all_found_products)}")
        
        # Группировка по сетям
        by_chain = {}
        for product in all_found_products:
            chain_name = product.get('chain_name', 'unknown')
            if chain_name not in by_chain:
                by_chain[chain_name] = []
            by_chain[chain_name].append(product)
        
        print("\nРаспределение по сетям:")
        for chain_name, products in sorted(by_chain.items(), key=lambda x: -len(x[1])):
            print(f"  {chain_name}: {len(products)} товаров")

        # Сохранение результатов
        if all_found_products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bmk_products_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_found_products, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Данные сохранены в файл: {filename}")
            
            # Также сохраняем CSV для удобства
            csv_filename = f"bmk_products_{timestamp}.csv"
            save_to_csv(all_found_products, csv_filename)
            print(f"✓ Данные сохранены в CSV: {csv_filename}")
        
        return all_found_products


def save_to_csv(products: list[dict], filename: str):
    """Сохранение товаров в CSV формат."""
    import csv
    
    if not products:
        return
    
    # Определяем все возможные поля
    all_fields = set()
    for product in products:
        all_fields.update(product.keys())
    
    # Основные поля в нужном порядке
    main_fields = [
        'chain_name', 'name', 'brand', 'manufacturer', 
        'price', 'current_price', 'old_price',
        'id', 'sku', 'plu', 'category',
        'image_url', 'product_url', 'parsed_at'
    ]
    
    # Добавляем остальные поля
    other_fields = sorted(all_fields - set(main_fields))
    fieldnames = main_fields + other_fields
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(products)


if __name__ == "__main__":
    asyncio.run(parse_all_chains())
