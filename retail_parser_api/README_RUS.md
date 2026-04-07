# Парсеры retail-сетей для поиска продукции Барнаульского Молочного Комбината

## Описание
Парсер для поиска товаров целевых производителей и брендов в российских retail-сетях.

### Целевые производители:
- Барнаульский Молочный комбинат
- АО Барнаульский Молочный комбинат
- АО БМК
- Логовская сыроварня

### Целевые бренды:
- Лакт
- Молочная сказка
- Модест
- Чуйский
- Логовская сыроварня
- Частица Алтая
- Сибирское подворье
- Ромбер / Romber

## Структура проекта

```
retail_parser_api/
├── parsers/
│   ├── base.py              # Базовый класс и конфигурация фильтрации
│   ├── prodtorg_chizhik.py  # Парсер Чижик (HTML через Playwright)
│   ├── lenta.py             # Парсер Лента (HTML через Playwright)
│   └── __init__.py
├── run_parsers.py           # Главный скрипт запуска
└── requirements.txt
```

## Установка

```bash
pip install -r requirements.txt
playwright install chromium
```

## Запуск

### Запуск всех парсеров:
```bash
python run_parsers.py
```

### Запуск отдельного парсера:
```bash
# Тест структуры парсера Чижик
python parsers/prodtorg_chizhik.py

# Тест структуры парсера Лента
python parsers/lenta.py
```

## Добавление новых сетей

1. Создайте новый файл в `parsers/` например `magnit.py`
2. Унаследуйтесь от `BaseParser`
3. Реализуйте метод `parse()`
4. Добавьте парсер в `run_parsers.py`

Пример:
```python
from parsers.base import BaseParser, TARGET_MANUFACTURERS, TARGET_BRANDS

class MagnitParser(BaseParser):
    async def parse(self):
        # Ваша логика парсинга
        pass
```

## Результаты
Результаты сохраняются в JSON файлы с временной меткой:
- `results_LentaParser_YYYYMMDD_HHMMSS.json`
- `results_ProdTorgChizhikParser_YYYYMMDD_HHMMSS.json`

## Примечания
- Для парсинга используется Playwright (headless браузер)
- Селекторы CSS могут требовать уточнения под актуальную верстку сайтов
- Рекомендуется запускать с задержками между запросами
