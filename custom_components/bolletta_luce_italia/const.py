"""Costanti di Bolletta Luce Italia."""

from __future__ import annotations

DOMAIN = "bolletta_luce_italia"
PLATFORMS = ["sensor"]

CONF_NAME = "name"
CONF_ENERGY_F1 = "energy_f1"
CONF_ENERGY_F2 = "energy_f2"
CONF_ENERGY_F3 = "energy_f3"
CONF_TARIFF_MODEL = "tariff_model"
CONF_PUN_F1 = "pun_f1"
CONF_PUN_F2 = "pun_f2"
CONF_PUN_F3 = "pun_f3"
CONF_FIXED_F1 = "fixed_f1"
CONF_FIXED_F2 = "fixed_f2"
CONF_FIXED_F3 = "fixed_f3"
CONF_LOSS_FACTOR = "loss_factor"
CONF_SPREAD_F1 = "spread_f1"
CONF_SPREAD_F2 = "spread_f2"
CONF_SPREAD_F3 = "spread_f3"
CONF_CORRECTION_FACTOR = "correction_factor"
CONF_SALES_FIXED_YEAR = "sales_fixed_year"
CONF_DISTRIBUTION_FIXED_YEAR = "distribution_fixed_year"
CONF_POWER_RATE_YEAR = "power_rate_year"
CONF_COMMITTED_POWER = "committed_power"
CONF_DISTRIBUTION_VARIABLE = "distribution_variable"
CONF_SYSTEM_CHARGES = "system_charges"
CONF_CDISPD = "cdispd"
CONF_EXCISE = "excise"
CONF_VAT = "vat"
CONF_RAI_YEAR = "rai_year"
CONF_RAI_INSTALLMENTS = "rai_installments"
CONF_EV_ENABLED = "ev_enabled"
CONF_EV_GRID = "ev_grid"
CONF_EV_PV = "ev_pv"
CONF_EV_INCLUDE_FIXED = "ev_include_fixed"

TARIFF_INDEXED = "indexed"
TARIFF_FIXED = "fixed"

DEFAULTS = {
    CONF_NAME: "Bolletta luce",
    CONF_TARIFF_MODEL: TARIFF_INDEXED,
    CONF_FIXED_F1: 0.0,
    CONF_FIXED_F2: 0.0,
    CONF_FIXED_F3: 0.0,
    CONF_LOSS_FACTOR: 1.10,
    CONF_SPREAD_F1: 0.0088,
    CONF_SPREAD_F2: 0.0088,
    CONF_SPREAD_F3: 0.0088,
    CONF_CORRECTION_FACTOR: 1.0,
    CONF_SALES_FIXED_YEAR: 72.0,
    CONF_DISTRIBUTION_FIXED_YEAR: 0.0,
    CONF_POWER_RATE_YEAR: 0.0,
    CONF_COMMITTED_POWER: 3.0,
    CONF_DISTRIBUTION_VARIABLE: 0.0,
    CONF_SYSTEM_CHARGES: 0.0,
    CONF_CDISPD: 0.0,
    CONF_EXCISE: 0.0227,
    CONF_VAT: 10.0,
    CONF_RAI_YEAR: 90.0,
    CONF_RAI_INSTALLMENTS: 10,
    CONF_EV_ENABLED: False,
    CONF_EV_INCLUDE_FIXED: False,
}

STORAGE_VERSION = 1
STORAGE_KEY = DOMAIN + ".{entry_id}"
SERVICE_RECORD_INVOICE = "registra_bolletta"
SERVICE_IMPORT_HISTORY = "importa_storico"
SERVICE_ARCHIVE_MONTH = "archivia_mese"
