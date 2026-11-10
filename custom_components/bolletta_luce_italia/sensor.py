"""Sensori di Bolletta Luce Italia."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DOMAIN
from .coordinator import BillCoordinator


@dataclass(frozen=True, kw_only=True)
class BillSensorDescription(SensorEntityDescription):
    attribute_keys: tuple[str, ...] = ()


ENERGY = {"native_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR, "device_class": SensorDeviceClass.ENERGY, "state_class": SensorStateClass.MEASUREMENT}
MONEY = {"native_unit_of_measurement": CURRENCY_EURO, "device_class": SensorDeviceClass.MONETARY, "state_class": SensorStateClass.MEASUREMENT}
PRICE = {"native_unit_of_measurement": "€/kWh", "state_class": SensorStateClass.MEASUREMENT}

SENSORS: tuple[BillSensorDescription, ...] = (
    BillSensorDescription(key="energy_f1", name="Energia fatturabile F1", **ENERGY),
    BillSensorDescription(key="energy_f2", name="Energia fatturabile F2", **ENERGY),
    BillSensorDescription(key="energy_f3", name="Energia fatturabile F3", **ENERGY),
    BillSensorDescription(key="energy_total", name="Energia fatturabile totale", **ENERGY),
    BillSensorDescription(key="unit_price_f1", name="Prezzo energia F1", **PRICE),
    BillSensorDescription(key="unit_price_f2", name="Prezzo energia F2", **PRICE),
    BillSensorDescription(key="unit_price_f3", name="Prezzo energia F3", **PRICE),
    BillSensorDescription(key="cost_f1", name="Costo fascia F1", **MONEY),
    BillSensorDescription(key="cost_f2", name="Costo fascia F2", **MONEY),
    BillSensorDescription(key="cost_f3", name="Costo fascia F3", **MONEY),
    BillSensorDescription(key="matter", name="Costo materia energia", **MONEY),
    BillSensorDescription(key="cdispd_cost", name="Costo CdispD", **MONEY),
    BillSensorDescription(key="network_cost", name="Servizi di rete e oneri", **MONEY),
    BillSensorDescription(key="fixed_cost", name="Quote fisse", **MONEY),
    BillSensorDescription(key="excise", name="Accise", **MONEY),
    BillSensorDescription(key="vat", name="IVA", **MONEY),
    BillSensorDescription(key="rai", name="Canone RAI", **MONEY),
    BillSensorDescription(key="estimate", name="Stima bolletta del mese", attribute_keys=("month", "energy_total", "matter", "network_cost", "fixed_cost", "excise", "vat", "rai"), **MONEY),
    BillSensorDescription(key="effective_price", name="Costo medio effettivo", **PRICE),
    BillSensorDescription(key="ev_grid_energy", name="Auto: energia da rete", **ENERGY),
    BillSensorDescription(key="ev_pv_energy", name="Auto: energia da fotovoltaico", **ENERGY),
    BillSensorDescription(key="ev_cost", name="Auto: quota bolletta", attribute_keys=("ev_share",), **MONEY),
    BillSensorDescription(key="latest_real_energy", name="Ultima bolletta: consumi fatturati", attribute_keys=("latest_invoice_month",), **ENERGY),
    BillSensorDescription(key="latest_real_total", name="Ultima bolletta: totale reale", attribute_keys=("latest_invoice_month",), **MONEY),
    BillSensorDescription(key="deviation", name="Scostamento ultima bolletta", **MONEY),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: BillCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(BillSensor(coordinator, entry, description) for description in SENSORS)


class BillSensor(CoordinatorEntity[BillCoordinator], SensorEntity):
    """Espone un risultato del calcolo coordinato."""

    entity_description: BillSensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: BillCoordinator, entry: ConfigEntry, description: BillSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.config.get(CONF_NAME, "Bolletta luce"),
            manufacturer="Bolletta Luce Italia",
            model="Calcolatore bolletta elettrica",
            sw_version="0.1.0",
        )

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        attrs = {
            key: self.coordinator.data.get(key)
            for key in self.entity_description.attribute_keys
            if key in self.coordinator.data
        }
        return attrs or None
