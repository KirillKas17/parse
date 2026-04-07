# Retail Parser API

Парсер для поиска товаров целевых производителей и брендов в различных retail-сетях России.

## Целевые производители
- Барнаульский Молочный комбинат
- АО Барнаульский Молочный комбинат
- АО БМК
- Логовская сыроварня

## Целевые бренды
- Лакт
- Молочная сказка
- Модест
- Чуйский
- Логовская сыроварня
- Частица Алтая
- Сибирское подворье
- Ромбер
- Romber

## Поддерживаемые сети
1. Быстроном
2. Лама
3. Камелот-А ООО
4. МЕТРО Кеш энд Керри ООО
5. О'КЕЙ ООО
6. Доброцен
7. универсамы Бегемаг ООО
8. Элемент-Трейд ООО (ТС Монетка)
9. Яндекс.Лавка ООО
10. Самокат
11. Командор
12. Агроторг ООО (Х5)
13. АШАН ООО
14. ЛЕНТА ООО
15. ПРОДТОРГ АО
16. Тандер АО

## Установка

```bash
pip install -r requirements.txt
playwright install
```

## Использование

### Запуск парсера всех сетей

```bash
python -m retail_parser_api.main
```

### Программное использование

```python
import asyncio
from retail_parser_api import RetailParserAPI

async def main():
    async with RetailParserAPI(headless=True) as api:
        # Поиск товаров в конкретной сети
        chain = {"name": "ЛЕНТА ООО", "url": "https://lenta.com"}
        products = await api.Catalog.find_target_products(chain)
        
        print(f"Найдено {len(products)} товаров")
        
        # Фильтрация товаров
        for product in products:
            if api.matches_manufacturer(product.get('manufacturer', '')):
                print(f"Товар от БМК: {product.get('name')}")
            
            if api.matches_brand(product.get('brand', '')):
                print(f"Товар бренда: {product.get('name')}")

asyncio.run(main())
```

## Структура проекта

```
retail_parser_api/
├── __init__.py           # Экспорт основных классов
├── enums.py              # Перечисления (PurchaseMode, Sorting)
├── manager.py            # Основной класс RetailParserAPI
├── main.py               # Скрипт для запуска парсинга
├── requirements.txt      # Зависимости
├── endpoints/
│   ├── catalog.py        # API для работы с каталогом товаров
│   ├── geolocation.py    # API для работы с геолокацией
│   └── general.py        # Общие функции (скачивание изображений, сохранение)
```

## Выходные данные

Парсер сохраняет результаты в двух форматах:
- `bmk_products_YYYYMMDD_HHMMSS.json` - полный JSON с данными
- `bmk_products_YYYYMMDD_HHMMSS.csv` - CSV для удобного анализа

## Примечания

- Для работы требуется установленный браузер Playwright
- Некоторые сети могут требовать авторизации или иметь защиту от ботов
- Рекомендуется использовать прокси для массового парсинга

## Лицензия

MIT
