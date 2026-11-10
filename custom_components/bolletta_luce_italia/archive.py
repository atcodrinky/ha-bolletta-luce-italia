"""Archivio persistente mensile e bollette reali."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION


class BillArchive:
    """Conserva stime chiuse e consuntivi reali nello storage di HA."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, STORAGE_KEY.format(entry_id=entry_id)
        )
        self.data: dict[str, Any] = {"months": {}, "invoices": {}}

    async def async_load(self) -> None:
        loaded = await self._store.async_load()
        if loaded:
            self.data.update(loaded)

    async def async_save(self) -> None:
        await self._store.async_save(self.data)

    async def async_archive(self, month: str, snapshot: dict[str, Any]) -> None:
        self.data.setdefault("months", {})[month] = snapshot
        await self.async_save()

    async def async_record_invoice(self, month: str, energy: float, total: float) -> None:
        self.data.setdefault("invoices", {})[month] = {
            "energy": round(float(energy), 3),
            "total": round(float(total), 2),
        }
        await self.async_save()

    def latest_invoice(self) -> tuple[str | None, dict[str, Any] | None]:
        invoices = self.data.get("invoices", {})
        if not invoices:
            return None, None
        key = max(invoices)
        return key, invoices[key]
