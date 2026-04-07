"""Работа с каталогом товаров."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote

from human_requests import ApiChild, ApiParent, api_child_field, autotest
from human_requests.abstraction import FetchResponse, HttpMethod

if TYPE_CHECKING:
    from ..manager import RetailParserAPI


@dataclass(init=False)
class ClassCatalog(ApiChild["RetailParserAPI"], ApiParent):
    """Методы для работы с каталогом товаров."""

    Product: ProductService = api_child_field(
        lambda parent: ProductService(parent.parent)
    )
    """Сервис для работы с товарами в каталоге."""

    def __init__(self, parent: "RetailParserAPI"):
        super().__init__(parent)
        ApiParent.__post_init__(self)

    @autotest
    async def search(
        self,
        chain_url: str,
        query: str,
        limit: int = 50,
    ) -> FetchResponse:
        """Поиск товаров по ключевым словам в конкретной сети."""
        encoded_query = quote(query)
        request_url = (
            f"{chain_url}/api/catalog/search"
            f"?q={encoded_query}&limit={limit}"
        )
        return await self._parent._request(
            HttpMethod.GET, 
            request_url,
            referer=chain_url
        )

    @autotest
    async def search_by_manufacturer(
        self,
        chain_url: str,
        manufacturer: str,
        limit: int = 100,
    ) -> FetchResponse:
        """Поиск товаров по производителю."""
        encoded_manufacturer = quote(manufacturer)
        request_url = (
            f"{chain_url}/api/catalog/manufacturer"
            f"?name={encoded_manufacturer}&limit={limit}"
        )
        return await self._parent._request(
            HttpMethod.GET,
            request_url,
            referer=chain_url
        )

    @autotest
    async def search_by_brand(
        self,
        chain_url: str,
        brand: str,
        limit: int = 100,
    ) -> FetchResponse:
        """Поиск товаров по бренду."""
        encoded_brand = quote(brand)
        request_url = (
            f"{chain_url}/api/catalog/brand"
            f"?name={encoded_brand}&limit={limit}"
        )
        return await self._parent._request(
            HttpMethod.GET,
            request_url,
            referer=chain_url
        )

    @autotest
    async def products_list(
        self,
        chain_url: str,
        category_id: str | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        brands: list[str] | None = None,
        limit: int = 50,
    ) -> FetchResponse:
        """Список товаров категории или все товары."""
        request_url = f"{chain_url}/api/catalog/products?limit={limit}"
        
        if category_id:
            request_url += f"&category_id={category_id}"
        if price_min is not None:
            request_url += f"&price_min={price_min}"
        if price_max is not None:
            request_url += f"&price_max={price_max}"
        if brands:
            for brand in brands:
                request_url += f"&brands={quote(brand)}"

        return await self._parent._request(
            HttpMethod.GET,
            request_url,
            referer=chain_url
        )

    async def find_target_products(
        self,
        chain: dict[str, str],
    ) -> list[dict]:
        """
        Поиск целевых товаров (БМК и бренды) в конкретной сети.
        Возвращает отфильтрованные товары.
        """
        all_products = []
        
        # Поиск по каждому производителю
        for manufacturer in self._parent.MANUFACTURERS:
            try:
                resp = await self.search_by_manufacturer(
                    chain_url=chain["url"],
                    manufacturer=manufacturer,
                    limit=100
                )
                if resp.ok:
                    products = resp.json().get("products", [])
                    filtered = self._parent.filter_products(products)
                    all_products.extend(filtered)
            except Exception as e:
                print(f"Ошибка поиска производителя {manufacturer}: {e}")

        # Поиск по каждому бренду
        for brand in self._parent.BRANDS:
            try:
                resp = await self.search_by_brand(
                    chain_url=chain["url"],
                    brand=brand,
                    limit=100
                )
                if resp.ok:
                    products = resp.json().get("products", [])
                    filtered = self._parent.filter_products(products)
                    all_products.extend(filtered)
            except Exception as e:
                print(f"Ошибка поиска бренда {brand}: {e}")

        # Удаление дубликатов по ID товара
        seen_ids = set()
        unique_products = []
        for product in all_products:
            product_id = product.get("id") or product.get("sku") or product.get("plu")
            if product_id and product_id not in seen_ids:
                seen_ids.add(product_id)
                unique_products.append(product)

        return unique_products


class ProductService(ApiChild["RetailParserAPI"]):
    """Сервис для работы с товарами в каталоге."""

    @autotest
    async def info(
        self,
        chain_url: str,
        product_id: int | str,
    ) -> FetchResponse:
        """Подробная информация о конкретном товаре."""
        request_url = f"{chain_url}/api/catalog/products/{product_id}"
        return await self._parent._request(
            HttpMethod.GET,
            request_url,
            referer=chain_url
        )
