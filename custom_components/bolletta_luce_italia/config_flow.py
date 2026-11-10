"""Configurazione grafica di Bolletta Luce Italia."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import *  # noqa: F403


def _value(values: dict[str, Any], key: str) -> Any:
    return values.get(key, DEFAULTS.get(key))  # noqa: F405


def _entity() -> selector.EntitySelector:
    return selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor"))


def _number(minimum: float = 0, maximum: float = 10000, step: float = 0.001) -> selector.NumberSelector:
    return selector.NumberSelector(selector.NumberSelectorConfig(min=minimum, max=maximum, step=step, mode=selector.NumberSelectorMode.BOX))


def _schema(values: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {
        vol.Required(CONF_NAME, default=_value(values, CONF_NAME)): selector.TextSelector(),  # noqa: F405
        vol.Required(CONF_ENERGY_F1, description={"suggested_value": values.get(CONF_ENERGY_F1)}): _entity(),  # noqa: F405
        vol.Required(CONF_ENERGY_F2, description={"suggested_value": values.get(CONF_ENERGY_F2)}): _entity(),  # noqa: F405
        vol.Required(CONF_ENERGY_F3, description={"suggested_value": values.get(CONF_ENERGY_F3)}): _entity(),  # noqa: F405
        vol.Required(CONF_TARIFF_MODEL, default=_value(values, CONF_TARIFF_MODEL)): selector.SelectSelector(  # noqa: F405
            selector.SelectSelectorConfig(options=[TARIFF_INDEXED, TARIFF_FIXED], mode=selector.SelectSelectorMode.DROPDOWN)  # noqa: F405
        ),
        vol.Optional(CONF_PUN_F1, description={"suggested_value": values.get(CONF_PUN_F1)}): _entity(),  # noqa: F405
        vol.Optional(CONF_PUN_F2, description={"suggested_value": values.get(CONF_PUN_F2)}): _entity(),  # noqa: F405
        vol.Optional(CONF_PUN_F3, description={"suggested_value": values.get(CONF_PUN_F3)}): _entity(),  # noqa: F405
        vol.Required(CONF_FIXED_F1, default=_value(values, CONF_FIXED_F1)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_FIXED_F2, default=_value(values, CONF_FIXED_F2)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_FIXED_F3, default=_value(values, CONF_FIXED_F3)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_LOSS_FACTOR, default=_value(values, CONF_LOSS_FACTOR)): _number(0.5, 2, 0.001),  # noqa: F405
        vol.Required(CONF_SPREAD_F1, default=_value(values, CONF_SPREAD_F1)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_SPREAD_F2, default=_value(values, CONF_SPREAD_F2)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_SPREAD_F3, default=_value(values, CONF_SPREAD_F3)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_CORRECTION_FACTOR, default=_value(values, CONF_CORRECTION_FACTOR)): _number(0.1, 10, 0.001),  # noqa: F405
        vol.Required(CONF_SALES_FIXED_YEAR, default=_value(values, CONF_SALES_FIXED_YEAR)): _number(),  # noqa: F405
        vol.Required(CONF_DISTRIBUTION_FIXED_YEAR, default=_value(values, CONF_DISTRIBUTION_FIXED_YEAR)): _number(),  # noqa: F405
        vol.Required(CONF_POWER_RATE_YEAR, default=_value(values, CONF_POWER_RATE_YEAR)): _number(),  # noqa: F405
        vol.Required(CONF_COMMITTED_POWER, default=_value(values, CONF_COMMITTED_POWER)): _number(0, 100, 0.1),  # noqa: F405
        vol.Required(CONF_DISTRIBUTION_VARIABLE, default=_value(values, CONF_DISTRIBUTION_VARIABLE)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_SYSTEM_CHARGES, default=_value(values, CONF_SYSTEM_CHARGES)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_CDISPD, default=_value(values, CONF_CDISPD)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_EXCISE, default=_value(values, CONF_EXCISE)): _number(0, 5),  # noqa: F405
        vol.Required(CONF_VAT, default=_value(values, CONF_VAT)): _number(0, 100, 0.1),  # noqa: F405
        vol.Required(CONF_RAI_YEAR, default=_value(values, CONF_RAI_YEAR)): _number(),  # noqa: F405
        vol.Required(CONF_RAI_INSTALLMENTS, default=_value(values, CONF_RAI_INSTALLMENTS)): _number(1, 12, 1),  # noqa: F405
        vol.Required(CONF_EV_ENABLED, default=_value(values, CONF_EV_ENABLED)): selector.BooleanSelector(),  # noqa: F405
        vol.Optional(CONF_EV_GRID, description={"suggested_value": values.get(CONF_EV_GRID)}): _entity(),  # noqa: F405
        vol.Optional(CONF_EV_PV, description={"suggested_value": values.get(CONF_EV_PV)}): _entity(),  # noqa: F405
        vol.Required(CONF_EV_INCLUDE_FIXED, default=_value(values, CONF_EV_INCLUDE_FIXED)): selector.BooleanSelector(),  # noqa: F405
    }
    return vol.Schema(fields)


def _validate(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if data.get(CONF_TARIFF_MODEL) == TARIFF_INDEXED and not all(data.get(key) for key in (CONF_PUN_F1, CONF_PUN_F2, CONF_PUN_F3)):  # noqa: F405
        errors["base"] = "pun_required"
    if data.get(CONF_EV_ENABLED) and not data.get(CONF_EV_GRID):  # noqa: F405
        errors["base"] = "ev_grid_required"
    return errors


class BollettaLuceItaliaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # noqa: F405
    """Crea una nuova configurazione."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate(user_input)
            if not errors:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)  # noqa: F405
        return self.async_show_form(step_id="user", data_schema=_schema(user_input or {}), errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return BollettaLuceItaliaOptionsFlow()


class BollettaLuceItaliaOptionsFlow(config_entries.OptionsFlow):
    """Modifica tutte le opzioni e ricarica solo l'integrazione."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        values = {**self.config_entry.data, **self.config_entry.options}
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=_schema(user_input or values), errors=errors)
