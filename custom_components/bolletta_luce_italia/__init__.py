"""Integrazione Bolletta Luce Italia."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_ARCHIVE_MONTH,
    SERVICE_RECORD_INVOICE,
)
from .coordinator import BillCoordinator

SERVICE_INVOICE_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Required("month"): vol.Match(r"^\d{4}-(0[1-9]|1[0-2])$"),
    vol.Required("energy"): vol.Coerce(float),
    vol.Required("total"): vol.Coerce(float),
})
SERVICE_ARCHIVE_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
    vol.Optional("month"): vol.Match(r"^\d{4}-(0[1-9]|1[0-2])$"),
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura una voce dall'interfaccia di Home Assistant."""
    coordinator = BillCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def _record_invoice(call: ServiceCall) -> None:
        target = hass.data[DOMAIN].get(call.data["entry_id"])
        if target is None:
            raise ValueError("Voce di Bolletta Luce Italia non trovata")
        await target.async_record_invoice(call.data["month"], call.data["energy"], call.data["total"])

    async def _archive_month(call: ServiceCall) -> None:
        target = hass.data[DOMAIN].get(call.data["entry_id"])
        if target is None:
            raise ValueError("Voce di Bolletta Luce Italia non trovata")
        await target.async_archive_current(call.data.get("month"))

    if not hass.services.has_service(DOMAIN, SERVICE_RECORD_INVOICE):
        hass.services.async_register(DOMAIN, SERVICE_RECORD_INVOICE, _record_invoice, schema=SERVICE_INVOICE_SCHEMA)
        hass.services.async_register(DOMAIN, SERVICE_ARCHIVE_MONTH, _archive_month, schema=SERVICE_ARCHIVE_SCHEMA)

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
            hass.services.async_remove(DOMAIN, SERVICE_ARCHIVE_MONTH)
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
