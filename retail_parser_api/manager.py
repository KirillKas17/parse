from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from camoufox import AsyncCamoufox
from human_requests import (
    ApiParent,
    HumanBrowser,
    HumanContext,
    HumanPage,
    api_child_field,
)
from human_requests.abstraction import FetchResponse, HttpMethod, Proxy
from human_requests.network_analyzer.anomaly_sniffer import (
    HeaderAnomalySniffer,
    WaitHeader,
    WaitSource,
)
from playwright.async_api import Error as PWError
from playwright.async_api import TimeoutError as PWTimeoutError

from .endpoints.catalog import ClassCatalog
from .endpoints.geolocation import ClassGeolocation
from .endpoints.general import ClassGeneral


@dataclass
class RetailParserAPI(ApiParent):
    """Клиент для парсинга данных из различных retail-сетей."""

    timeout_ms: float = 20000.0
    """Время ожидания ответа от сервера в миллисекундах."""
    headless: bool = False
    """Запускать браузер в headless режиме?"""
    proxy: str | dict | Proxy | None = field(default_factory=Proxy.from_env)
    """Прокси для всех запросов. По умолчанию берётся из окружения."""
    browser_opts: dict[str, Any] = field(default_factory=dict)
    """Дополнительные опции браузера."""

    session: HumanBrowser = field(init=False, repr=False)
    """Внутренняя сессия браузера для выполнения HTTP-запросов."""
    ctx: HumanContext = field(init=False, repr=False)
    """Внутренний контекст сессии браузера."""
    page: HumanPage = field(init=False, repr=False)
    """Внутренняя страница сессии браузера."""

    unstandard_headers: dict[str, str] = field(init=False, repr=False)
    """Нестандартные заголовки, собранные при прогреве."""

    Geolocation: ClassGeolocation = api_child_field(ClassGeolocation)
    """API для работы с геолокацией."""
    Catalog: ClassCatalog = api_child_field(ClassCatalog)
    """API для работы с каталогом товаров."""
    General: ClassGeneral = api_child_field(ClassGeneral)
    """API для общих функций."""

    # Список сетей для парсинга
    CHAINS: list[dict[str, str]] = field(
        default_factory=lambda: [
            {"name": "Быстроном", "url": "https://bystronom.ru"},
            {"name": "Лама", "url": "https://lama-shop.ru"},
            {"name": "Камелот-А ООО", "url": "https://camelot-a.ru"},
            {"name": "МЕТРО Кеш энд Керри ООО", "url": "https://metro-cc.ru"},
            {"name": "О'КЕЙ ООО", "url": "https://okei.ru"},
            {"name": "Доброцен", "url": "https://dobrotsen.ru"},
            {"name": "универсамы Бегемаг ООО", "url": "https://begemag.ru"},
            {"name": "Элемент-Трейд ООО (ТС Монетка)", "url": "https://monetka.ru"},
            {"name": "Яндекс.Лавка ООО", "url": "https://lavka.yandex.ru"},
            {"name": "Самокат", "url": "https://samokat.ru"},
            {"name": "Командор", "url": "https://komandor.ru"},
            {"name": "Агроторг ООО (Х5)", "url": "https://5post.ru"},
            {"name": "АШАН ООО", "url": "https://auchan.ru"},
            {"name": "ЛЕНТА ООО", "url": "https://lenta.com"},
            {"name": "ПРОДТОРГ АО", "url": "https://prodtorg.ru"},
            {"name": "Тандер АО", "url": "https://magnit.ru"},
        ]
    )
    """Список retail-сетей для парсинга."""

    # Ключевые слова для фильтрации производителей
    MANUFACTURERS: list[str] = field(
        default_factory=lambda: [
            "Барнаульский Молочный комбинат",
            "АО Барнаульский Молочный комбинат",
            "АО БМК",
            "Логовская сыроварня",
        ]
    )
    """Названия компаний-производителей для фильтрации."""

    # Ключевые слова для фильтрации брендов
    BRANDS: list[str] = field(
        default_factory=lambda: [
            "Лакт",
            "Молочная сказка",
            "Модест",
            "Чуйский",
            "Логовская сыроварня",
            "Частица Алтая",
            "Сибирское подворье",
            "Ромбер",
            "Romber",
        ]
    )
    """Бренды для фильтрации."""

    async def __aenter__(self) -> "RetailParserAPI":
        await self._warmup()
        return self

    async def _warmup(self) -> None:
        """Прогрев сессии через браузер для захвата обязательных заголовков."""
        px = self.proxy if isinstance(self.proxy, Proxy) else Proxy(self.proxy)
        br = await AsyncCamoufox(
            locale="ru-RU",
            headless=self.headless,
            proxy=px.as_dict(),
            block_images=False,
            **self.browser_opts,
        ).start()

        self.session = HumanBrowser.replace(br)
        self.ctx = await self.session.new_context()
        self.page = await self.ctx.new_page()
        self.page.on_error_screenshot_path = "screenshot.png"

        # Прогрев для первой сети (можно адаптировать под конкретную сеть)
        first_chain_url = self.CHAINS[0]["url"] if self.CHAINS else "https://5ka.ru"
        
        sniffer = HeaderAnomalySniffer(
            include_subresources=True,
            url_filter=lambda u: "api" in u.lower(),
        )
        await sniffer.start(self.ctx)

        await self.page.goto(first_chain_url, wait_until="networkidle")

        async def _click_robot_if_present() -> None:
            try:
                await self.page.locator('label[for="is-robot"]').click(
                    timeout=self.timeout_ms,
                )
            except (PWTimeoutError, PWError):
                return

        app_ready = asyncio.create_task(
            self.page.wait_for_selector("body", timeout=self.timeout_ms)
        )
        captcha_click = asyncio.create_task(_click_robot_if_present())

        done, _pending = await asyncio.wait(
            {app_ready, captcha_click},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if app_ready in done and not captcha_click.done():
            captcha_click.cancel()
            await asyncio.gather(captcha_click, return_exceptions=True)

        await app_ready

        await sniffer.wait(
            tasks=[
                WaitHeader(
                    source=WaitSource.REQUEST,
                    headers=["x-app-version", "x-device-id", "x-platform"],
                )
            ],
            timeout_ms=self.timeout_ms,
        )

        result_sniffer = await sniffer.complete()
        unique_headers: defaultdict[str, set[str]] = defaultdict(set)

        for _url, headers in result_sniffer["request"].items():
            for header, values in headers.items():
                unique_headers[header].update(values)

        self.unstandard_headers = {
            key: list(values)[0] for key, values in unique_headers.items()
        }

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def device_id(self) -> str:
        """Анонимный идентификатор устройства."""
        value = (await self.page.local_storage()).get("deviceId")
        return str(value)

    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
        add_unstandard_headers: bool = True,
        credentials: bool = True,
        referer: str | None = None,
    ) -> FetchResponse:
        """Выполнить HTTP-запрос через внутреннюю браузерную сессию."""
        return await self.page.fetch(
            url=url,
            method=method,
            body=json_body,
            mode="cors",
            credentials="include" if credentials else "omit",
            timeout_ms=self.timeout_ms,
            referrer=referer or self.CHAINS[0]["url"] if self.CHAINS else "https://5ka.ru",
            headers={"Accept": "application/json, text/plain, */*"}
            | (self.unstandard_headers if add_unstandard_headers else {}),
        )

    def matches_manufacturer(self, manufacturer: str) -> bool:
        """Проверка соответствия производителя ключевым словам."""
        manufacturer_lower = manufacturer.lower()
        return any(
            keyword.lower() in manufacturer_lower for keyword in self.MANUFACTURERS
        )

    def matches_brand(self, brand: str) -> bool:
        """Проверка соответствия бренда ключевым словам."""
        brand_lower = brand.lower()
        return any(keyword.lower() in brand_lower for keyword in self.BRANDS)

    def filter_products(self, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Фильтрация товаров по производителям и брендам."""
        filtered = []
        for product in products:
            manufacturer = product.get("manufacturer", "") or product.get("brand", "")
            brand = product.get("brand", "") or product.get("name", "")
            
            if self.matches_manufacturer(manufacturer) or self.matches_brand(brand):
                filtered.append(product)
        return filtered
