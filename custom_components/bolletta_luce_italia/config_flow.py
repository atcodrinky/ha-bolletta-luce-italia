"""Configurazione grafica di Bolletta Luce Italia."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import *  # noqa: F403

CONF_GO_BACK = "_go_back"


def _value(values: dict[str, Any], key: str) -> Any:
    return values.get(key, DEFAULTS.get(key))  # noqa: F405


def _entity() -> selector.EntitySelector:
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor")
    )


def _number(
    minimum: float = 0,
    maximum: float = 10000,
    step: float = 0.001,
) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _required_entity(values: dict[str, Any], key: str) -> vol.Required:
    current = values.get(key)
    if current:
        return vol.Required(key, description={"suggested_value": current})
    return vol.Required(key)


def _optional_entity(values: dict[str, Any], key: str) -> vol.Optional:
    current = values.get(key)
    if current:
        return vol.Optional(key, description={"suggested_value": current})
    return vol.Optional(key)


def _back_field() -> dict[Any, Any]:
    return {
        vol.Optional(CONF_GO_BACK, default=False): selector.BooleanSelector()
    }


def _sources_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME, default=_value(values, CONF_NAME)
            ): selector.TextSelector(),
            _required_entity(values, CONF_ENERGY_F1): _entity(),
            _required_entity(values, CONF_ENERGY_F2): _entity(),
            _required_entity(values, CONF_ENERGY_F3): _entity(),
        }
    )


def _tariff_schema(values: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {
        vol.Required(
            CONF_TARIFF_MODEL,
            default=_value(values, CONF_TARIFF_MODEL),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(
                        value=TARIFF_INDEXED,
                        label="Indicizzata al PUN",
                    ),
                    selector.SelectOptionDict(
                        value=TARIFF_FIXED,
                        label="Prezzo fisso",
                    ),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        _optional_entity(values, CONF_PUN_F1): _entity(),
        _optional_entity(values, CONF_PUN_F2): _entity(),
        _optional_entity(values, CONF_PUN_F3): _entity(),
        vol.Required(
            CONF_FIXED_F1, default=_value(values, CONF_FIXED_F1)
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_FIXED_F2, default=_value(values, CONF_FIXED_F2)
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_FIXED_F3, default=_value(values, CONF_FIXED_F3)
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_LOSS_FACTOR, default=_value(values, CONF_LOSS_FACTOR)
        ): _number(0.5, 2),
        vol.Required(
            CONF_SPREAD_F1, default=_value(values, CONF_SPREAD_F1)
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_SPREAD_F2, default=_value(values, CONF_SPREAD_F2)
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_SPREAD_F3, default=_value(values, CONF_SPREAD_F3)
        ): _number(0, 5, 0.000001),
    }
    fields.update(_back_field())
    return vol.Schema(fields)


def _network_schema(values: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {
        vol.Required(
            CONF_SALES_FIXED_YEAR,
            default=_value(values, CONF_SALES_FIXED_YEAR),
        ): _number(),
        vol.Required(
            CONF_DISTRIBUTION_FIXED_YEAR,
            default=_value(values, CONF_DISTRIBUTION_FIXED_YEAR),
        ): _number(),
        vol.Required(
            CONF_POWER_RATE_YEAR,
            default=_value(values, CONF_POWER_RATE_YEAR),
        ): _number(),
        vol.Required(
            CONF_COMMITTED_POWER,
            default=_value(values, CONF_COMMITTED_POWER),
        ): _number(0, 100, 0.1),
        vol.Required(
            CONF_DISTRIBUTION_VARIABLE,
            default=_value(values, CONF_DISTRIBUTION_VARIABLE),
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_SYSTEM_CHARGES,
            default=_value(values, CONF_SYSTEM_CHARGES),
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_CDISPD, default=_value(values, CONF_CDISPD)
        ): _number(0, 5, 0.000001),
    }
    fields.update(_back_field())
    return vol.Schema(fields)


def _taxes_schema(values: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {
        vol.Required(
            CONF_CORRECTION_FACTOR,
            default=_value(values, CONF_CORRECTION_FACTOR),
        ): _number(0.1, 10),
        vol.Required(
            CONF_EXCISE, default=_value(values, CONF_EXCISE)
        ): _number(0, 5, 0.000001),
        vol.Required(
            CONF_VAT, default=_value(values, CONF_VAT)
        ): _number(0, 100, 0.1),
        vol.Required(
            CONF_RAI_YEAR, default=_value(values, CONF_RAI_YEAR)
        ): _number(),
        vol.Required(
            CONF_RAI_INSTALLMENTS,
            default=_value(values, CONF_RAI_INSTALLMENTS),
        ): _number(1, 12, 1),
    }
    fields.update(_back_field())
    return vol.Schema(fields)


def _ev_schema(values: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {
        vol.Required(
            CONF_EV_ENABLED, default=_value(values, CONF_EV_ENABLED)
        ): selector.BooleanSelector(),
        _optional_entity(values, CONF_EV_GRID): _entity(),
        _optional_entity(values, CONF_EV_PV): _entity(),
        vol.Required(
            CONF_EV_INCLUDE_FIXED,
            default=_value(values, CONF_EV_INCLUDE_FIXED),
        ): selector.BooleanSelector(),
    }
    fields.update(_back_field())
    return vol.Schema(fields)


class _WizardMixin:
    """Passaggi condivisi dalla configurazione e dalle opzioni."""

    _data: dict[str, Any]

    def _ensure_data(self) -> None:
        if not hasattr(self, "_data"):
            self._data = {}

    def _store(
        self,
        user_input: dict[str, Any],
        optional_keys: tuple[str, ...] = (),
    ) -> bool:
        values = dict(user_input)
        go_back = bool(values.pop(CONF_GO_BACK, False))
        for key in optional_keys:
            if key not in values:
                self._data.pop(key, None)
        self._data.update(values)
        return go_back

    async def async_step_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        self._ensure_data()
        if user_input is not None:
            self._store(user_input)
            return await self.async_step_tariff()
        return self.async_show_form(
            step_id="sources",
            data_schema=_sources_schema(self._data),
        )

    async def async_step_tariff(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            go_back = self._store(
                user_input,
                (CONF_PUN_F1, CONF_PUN_F2, CONF_PUN_F3),
            )
            if go_back:
                return await self.async_step_sources()
            if (
                self._data.get(CONF_TARIFF_MODEL) == TARIFF_INDEXED
                and not all(
                    self._data.get(key)
                    for key in (CONF_PUN_F1, CONF_PUN_F2, CONF_PUN_F3)
                )
            ):
                errors["base"] = "pun_required"
            else:
                return await self.async_step_network()
        return self.async_show_form(
            step_id="tariff",
            data_schema=_tariff_schema(self._data),
            errors=errors,
        )

    async def async_step_network(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            if self._store(user_input):
                return await self.async_step_tariff()
            return await self.async_step_taxes()
        return self.async_show_form(
            step_id="network",
            data_schema=_network_schema(self._data),
        )

    async def async_step_taxes(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            if self._store(user_input):
                return await self.async_step_network()
            return await self.async_step_ev()
        return self.async_show_form(
            step_id="taxes",
            data_schema=_taxes_schema(self._data),
        )

    async def async_step_ev(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            go_back = self._store(
                user_input,
                (CONF_EV_GRID, CONF_EV_PV),
            )
            if go_back:
                return await self.async_step_taxes()
            if (
                self._data.get(CONF_EV_ENABLED)
                and not self._data.get(CONF_EV_GRID)
            ):
                errors["base"] = "ev_grid_required"
            else:
                return await self._async_finish_wizard()
        return self.async_show_form(
            step_id="ev",
            data_schema=_ev_schema(self._data),
            errors=errors,
            last_step=True,
        )

    async def _async_finish_wizard(self) -> FlowResult:
        raise NotImplementedError


class BollettaLuceItaliaConfigFlow(
    _WizardMixin,
    config_entries.ConfigFlow,
    domain=DOMAIN,  # noqa: F405
):
    """Crea una nuova configurazione."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        self._ensure_data()
        return await self.async_step_sources(user_input)

    async def _async_finish_wizard(self) -> FlowResult:
        return self.async_create_entry(
            title=self._data[CONF_NAME],  # noqa: F405
            data=self._data,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return BollettaLuceItaliaOptionsFlow()


class BollettaLuceItaliaOptionsFlow(
    _WizardMixin,
    config_entries.OptionsFlow,
):
    """Modifica le opzioni e ricarica soltanto l'integrazione."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if not hasattr(self, "_data"):
            self._data = {
                **self.config_entry.data,
                **self.config_entry.options,
            }
        return await self.async_step_sources(user_input)

    async def _async_finish_wizard(self) -> FlowResult:
        return self.async_create_entry(title="", data=self._data)
