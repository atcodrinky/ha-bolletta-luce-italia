"""Integrazione Bolletta Luce Italia."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_ARCHIVE_MONTH,
    SERVICE_IMPORT_HISTORY,
    SERVICE_RECORD_INVOICE,
)
from .coordinator import BillCoordinator

_NON_NEGATIVE = vol.All(vol.Coerce(float), vol.Range(min=0))
_MONTH = vol.Match(r"^\d{4}-(0[1-9]|1[0-2])$")
_DATE = vol.Match(r"^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$")

SERVICE_INVOICE_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("month"): _MONTH,
    vol.Required("energy"): _NON_NEGATIVE,
    vol.Required("total"): _NON_NEGATIVE,
})
SERVICE_ARCHIVE_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Optional("month"): _MONTH,
})

INVOICE_IMPORT_SCHEMA = vol.Schema({
    vol.Required("month"): _MONTH,
    vol.Optional("period_start"): _DATE,
    vol.Optional("period_end"): _DATE,
    vol.Required("energy_f1"): _NON_NEGATIVE,
    vol.Required("energy_f2"): _NON_NEGATIVE,
    vol.Required("energy_f3"): _NON_NEGATIVE,
    vol.Required("energy_bill_total"): _NON_NEGATIVE,
    vol.Optional("rai", default=0.0): _NON_NEGATIVE,
    vol.Optional("bonus", default=0.0): vol.Coerce(float),
    vol.Optional("amount_due"): _NON_NEGATIVE,
    vol.Optional("matter"): _NON_NEGATIVE,
    vol.Optional("transport"): _NON_NEGATIVE,
    vol.Optional("system_charges"): _NON_NEGATIVE,
    vol.Optional("excise"): _NON_NEGATIVE,
    vol.Optional("vat"): _NON_NEGATIVE,
})
SERVICE_IMPORT_HISTORY_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("invoices"): vol.All(
        cv.ensure_list,
        [INVOICE_IMPORT_SCHEMA],
        vol.Length(min=1),
    ),
})


def _prepare_invoice(values: dict[str, Any]) -> dict[str, Any]:
    """Calcola i campi comuni senza perdere i valori originali."""
    invoice = dict(values)
    energy = sum(
        float(invoice[key])
        for key in ("energy_f1", "energy_f2", "energy_f3")
    )
    comparison_total = (
        float(invoice["energy_bill_total"]) + float(invoice.get("rai", 0))
    )
    invoice["energy"] = energy
    invoice["total"] = comparison_total
    invoice.setdefault(
        "amount_due",
        comparison_total + float(invoice.get("bonus", 0)),
    )
    return invoice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura una voce dall'interfaccia di Home Assistant."""
    coordinator = BillCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def _record_invoice(call: ServiceCall) -> None:
        target = hass.data[DOMAIN].get(call.data["entry_id"])
        if target is None:
            raise ValueError("Voce di Bolletta Luce Italia non trovata")
        await target.async_record_invoice(
            call.data["month"],
            call.data["energy"],
            call.data["total"],
        )

    async def _import_history(call: ServiceCall) -> None:
        target = hass.data[DOMAIN].get(call.data["entry_id"])
        if target is None:
            raise ValueError("Voce di Bolletta Luce Italia non trovata")
        invoices = [
            _prepare_invoice(dict(invoice))
            for invoice in call.data["invoices"]
        ]
        await target.async_import_invoices(invoices)

    async def _archive_month(call: ServiceCall) -> None:
        target = hass.data[DOMAIN].get(call.data["entry_id"])
        if target is None:
            raise ValueError("Voce di Bolletta Luce Italia non trovata")
        await target.async_archive_current(call.data.get("month"))

    if not hass.services.has_service(DOMAIN, SERVICE_RECORD_INVOICE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RECORD_INVOICE,
            _record_invoice,
            schema=SERVICE_INVOICE_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_IMPORT_HISTORY,
            _import_history,
            schema=SERVICE_IMPORT_HISTORY_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_ARCHIVE_MONTH,
            _archive_month,
            schema=SERVICE_ARCHIVE_SCHEMA,
        )

    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Scarica una voce senza richiedere il riavvio di Home Assistant."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_RECORD_INVOICE)
            hass.services.async_remove(DOMAIN, SERVICE_IMPORT_HISTORY)
            hass.services.async_remove(DOMAIN, SERVICE_ARCHIVE_MONTH)
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
