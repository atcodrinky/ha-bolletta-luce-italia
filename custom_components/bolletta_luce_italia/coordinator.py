"""Coordinatore dati di Bolletta Luce Italia."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .archive import BillArchive
from .calculator import calculate
from .const import *  # noqa: F403


class BillCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Legge le entità sorgente e aggiorna tutti i risultati insieme."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,  # noqa: F405
            update_interval=timedelta(minutes=5),
        )
        self.entry = entry
        self.archive = BillArchive(hass, entry.entry_id)
        self._active_month: str | None = None
        self._active_snapshot: dict[str, Any] | None = None

    @property
    def config(self) -> dict[str, Any]:
        return {**self.entry.data, **self.entry.options}

    async def _async_setup(self) -> None:
        await self.archive.async_load()

    def _state_number(self, entity_id: str | None, required: bool = False) -> float:
        if not entity_id:
            if required:
                raise UpdateFailed("Entità sorgente non configurata")
            return 0.0
        state = self.hass.states.get(entity_id)
        if state is None or state.state in {"unknown", "unavailable", "none", ""}:
            if required:
                raise UpdateFailed(f"Sorgente non disponibile: {entity_id}")
            return 0.0
        try:
            return float(state.state)
        except ValueError as err:
            raise UpdateFailed(f"Valore non numerico: {entity_id}") from err

    async def _async_update_data(self) -> dict[str, Any]:
        cfg = self.config
        values = {
            "raw_energy_f1": self._state_number(cfg.get(CONF_ENERGY_F1), True),  # noqa: F405
            "raw_energy_f2": self._state_number(cfg.get(CONF_ENERGY_F2), True),  # noqa: F405
            "raw_energy_f3": self._state_number(cfg.get(CONF_ENERGY_F3), True),  # noqa: F405
        }
        if cfg.get(CONF_TARIFF_MODEL) == TARIFF_INDEXED:  # noqa: F405
            values.update({
                "pun_f1": self._state_number(cfg.get(CONF_PUN_F1), True),  # noqa: F405
                "pun_f2": self._state_number(cfg.get(CONF_PUN_F2), True),  # noqa: F405
                "pun_f3": self._state_number(cfg.get(CONF_PUN_F3), True),  # noqa: F405
            })
        if cfg.get(CONF_EV_ENABLED):  # noqa: F405
            values["ev_grid"] = self._state_number(cfg.get(CONF_EV_GRID))  # noqa: F405
            values["ev_pv"] = self._state_number(cfg.get(CONF_EV_PV))  # noqa: F405

        now = dt_util.now()
        month_key = now.strftime("%Y-%m")
        result = calculate(values, cfg, now.month)
        result["month"] = month_key

        if self._active_month and self._active_month != month_key and self._active_snapshot:
            await self.archive.async_archive(self._active_month, self._active_snapshot)
        self._active_month = month_key
        self._active_snapshot = dict(result)

        invoice_month, invoice = self.archive.latest_invoice()
        invoices = self.archive.data.get("invoices", {})
        result["invoice_count"] = len(invoices)
        result["invoice_archive"] = invoices
        result["latest_invoice_month"] = invoice_month
        result["latest_invoice"] = invoice
        result["latest_real_energy"] = invoice.get("energy") if invoice else None
        result["latest_real_total"] = invoice.get("total") if invoice else None
        result["latest_energy_bill_total"] = (
            invoice.get("energy_bill_total") if invoice else None
        )
        result["latest_invoice_rai"] = invoice.get("rai") if invoice else None
        result["latest_bonus"] = invoice.get("bonus") if invoice else None
        result["latest_amount_due"] = invoice.get("amount_due") if invoice else None
        archived = (
            self.archive.data.get("months", {}).get(invoice_month, {})
            if invoice_month
            else {}
        )
        estimate = archived.get("estimate")
        result["deviation"] = (
            round(invoice["total"] - estimate, 2)
            if invoice and estimate is not None
            else None
        )
        return result

    async def async_record_invoice(
        self,
        month: str,
        energy: float,
        total: float,
        **details: Any,
    ) -> None:
        await self.archive.async_record_invoice(month, energy, total, **details)
        await self.async_request_refresh()

    async def async_import_invoices(
        self,
        invoices: list[dict[str, Any]],
    ) -> None:
        await self.archive.async_import_invoices(invoices)
        await self.async_request_refresh()

    async def async_archive_current(self, month: str | None = None) -> None:
        if not self.data:
            return
        key = month or self.data["month"]
        await self.archive.async_archive(key, dict(self.data))
        await self.async_request_refresh()
