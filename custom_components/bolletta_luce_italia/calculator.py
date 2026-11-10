"""Motore di calcolo, indipendente da Home Assistant."""

from __future__ import annotations

from typing import Any

from .const import *  # noqa: F403


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _money(value: float) -> float:
    return round(value + 1e-10, 2)


def calculate(values: dict[str, Any], config: dict[str, Any], month: int) -> dict[str, Any]:
    """Calcola consumi, voci di costo e stima totale del mese."""
    correction = _number(config.get(CONF_CORRECTION_FACTOR), 1.0)  # noqa: F405
    energies = [
        _number(values.get("raw_energy_f1")) * correction,
        _number(values.get("raw_energy_f2")) * correction,
        _number(values.get("raw_energy_f3")) * correction,
    ]

    if config.get(CONF_TARIFF_MODEL) == TARIFF_FIXED:  # noqa: F405
        prices = [
            _number(config.get(CONF_FIXED_F1)),  # noqa: F405
            _number(config.get(CONF_FIXED_F2)),  # noqa: F405
            _number(config.get(CONF_FIXED_F3)),  # noqa: F405
        ]
    else:
        loss = _number(config.get(CONF_LOSS_FACTOR), 1.0)  # noqa: F405
        prices = [
            _number(values.get("pun_f1")) * loss + _number(config.get(CONF_SPREAD_F1)),  # noqa: F405
            _number(values.get("pun_f2")) * loss + _number(config.get(CONF_SPREAD_F2)),  # noqa: F405
            _number(values.get("pun_f3")) * loss + _number(config.get(CONF_SPREAD_F3)),  # noqa: F405
        ]

    band_costs = [energies[index] * prices[index] for index in range(3)]
    energy_total = sum(energies)
    matter = sum(band_costs)
    cdispd_cost = energy_total * _number(config.get(CONF_CDISPD))  # noqa: F405
    network_unit = _number(config.get(CONF_DISTRIBUTION_VARIABLE)) + _number(config.get(CONF_SYSTEM_CHARGES))  # noqa: F405
    network_cost = energy_total * network_unit
    fixed_cost = (
        _number(config.get(CONF_SALES_FIXED_YEAR))  # noqa: F405
        + _number(config.get(CONF_DISTRIBUTION_FIXED_YEAR))  # noqa: F405
        + _number(config.get(CONF_POWER_RATE_YEAR)) * _number(config.get(CONF_COMMITTED_POWER))  # noqa: F405
    ) / 12
    excise = energy_total * _number(config.get(CONF_EXCISE))  # noqa: F405
    taxable = matter + cdispd_cost + network_cost + fixed_cost + excise
    vat = taxable * _number(config.get(CONF_VAT), 10.0) / 100
    installments = max(1, int(_number(config.get(CONF_RAI_INSTALLMENTS), 10)))  # noqa: F405
    rai = _number(config.get(CONF_RAI_YEAR)) / installments if 1 <= month <= installments else 0.0  # noqa: F405
    estimate = taxable + vat + rai

    variable_before_vat = matter + cdispd_cost + network_cost + excise
    ev_grid = _number(values.get("ev_grid")) if config.get(CONF_EV_ENABLED) else 0.0  # noqa: F405
    ev_pv = _number(values.get("ev_pv")) if config.get(CONF_EV_ENABLED) else 0.0  # noqa: F405
    ev_ratio = ev_grid / energy_total if energy_total > 0 else 0.0
    ev_cost = variable_before_vat * ev_ratio
    if config.get(CONF_EV_INCLUDE_FIXED):  # noqa: F405
        ev_cost += (fixed_cost + rai) * ev_ratio
    ev_cost *= 1 + _number(config.get(CONF_VAT), 10.0) / 100  # noqa: F405

    return {
        "energy_f1": round(energies[0], 3),
        "energy_f2": round(energies[1], 3),
        "energy_f3": round(energies[2], 3),
        "energy_total": round(energy_total, 3),
        "unit_price_f1": round(prices[0], 6),
        "unit_price_f2": round(prices[1], 6),
        "unit_price_f3": round(prices[2], 6),
        "cost_f1": _money(band_costs[0]),
        "cost_f2": _money(band_costs[1]),
        "cost_f3": _money(band_costs[2]),
        "matter": _money(matter),
        "cdispd_cost": _money(cdispd_cost),
        "network_cost": _money(network_cost),
        "fixed_cost": _money(fixed_cost),
        "excise": _money(excise),
        "vat": _money(vat),
        "rai": _money(rai),
        "estimate": _money(estimate),
        "effective_price": round(estimate / energy_total, 4) if energy_total else 0.0,
        "ev_grid_energy": round(ev_grid, 3),
        "ev_pv_energy": round(ev_pv, 3),
        "ev_cost": _money(ev_cost),
        "ev_share": round(ev_ratio * 100, 2),
    }
