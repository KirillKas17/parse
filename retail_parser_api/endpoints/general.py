"""Общий (не классифицируемый) функционал."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from aiohttp_retry import ExponentialRetry, RetryClient
from human_requests import ApiChild
from human_requests.abstraction import Proxy

if TYPE_CHECKING:
    from ..manager import RetailParserAPI


class ClassGeneral(ApiChild["RetailParserAPI"]):
    """Общие методы API для парсинга retail-сетей."""

    async def download_image(
        self, url: str, retry_attempts: int = 3, timeout: float = 10
    ) -> BytesIO:
        """Скачать изображение по URL."""
        retry_options = ExponentialRetry(
            attempts=retry_attempts,
            start_timeout=3.0,
            max_timeout=timeout,
        )

        px = (
            self._parent.proxy
            if isinstance(self._parent.proxy, Proxy)
            else Proxy(self._parent.proxy)
        )
        async with RetryClient(retry_options=retry_options) as retry_client:
            async with retry_client.get(
                url,
                raise_for_status=True,
                proxy=px.as_str(),
            ) as resp:
                body = await resp.read()
                file = BytesIO(body)
                file.name = url.split("/")[-1]
        return file

    async def save_to_json(self, data: list[dict], filename: str) -> None:
        """Сохранить данные в JSON файл."""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {filename}")
