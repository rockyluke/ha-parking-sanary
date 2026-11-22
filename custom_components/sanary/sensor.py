"""Sensor platform for the Sanary-sur-Mer integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONFIGURATION_URL, DOMAIN, PARKINGS
from .coordinator import SanaryUpdateCoordinator

_AVAILABLE_DESCRIPTION = SensorEntityDescription(
    key="available",
    native_unit_of_measurement="places",
    icon="mdi:parking",
)

_TOTAL_DESCRIPTION = SensorEntityDescription(
    key="total",
    native_unit_of_measurement="places",
    icon="mdi:counter",
)


def _device_info(counter_id: str, parking: dict[str, Any]) -> DeviceInfo:
    """One device per parking."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"sanary_{counter_id}")},
        name=f"Parking - Sanary - {parking['name']}",
        manufacturer="City of Sanary-sur-Mer",
        model="Parking space counter",
        configuration_url=CONFIGURATION_URL,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create an available and a total sensor per parking."""
    coordinator: SanaryUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []
    for counter_id, parking in PARKINGS.items():
        entities.append(
            SanaryParkingAvailableSensor(coordinator, counter_id, parking)
        )
        entities.append(SanaryParkingTotalSensor(counter_id, parking))
    async_add_entities(entities)


class SanaryParkingAvailableSensor(
    CoordinatorEntity[SanaryUpdateCoordinator], SensorEntity
):
    """Free spaces for one parking of Sanary-sur-Mer."""

    entity_description = _AVAILABLE_DESCRIPTION

    def __init__(
        self,
        coordinator: SanaryUpdateCoordinator,
        counter_id: str,
        parking: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._counter_id = counter_id
        self._attr_has_entity_name = True
        self._attr_unique_id = f"sanary_{counter_id}_available"
        self._attr_device_info = _device_info(counter_id, parking)
        # Entity name is the metric only: with has_entity_name, the friendly
        # name becomes "<device name> available", which naturally slugifies
        # to parking_sanary_<parking>_available.
        self._attr_name = "available"

    @property
    def available(self) -> bool:
        """Available while the data is valid and fresh."""
        counter = self.coordinator.data.get(self._counter_id)
        return super().available and counter is not None and counter["free"] is not None

    @property
    def native_value(self) -> int | None:
        """Number of free spaces."""
        counter = self.coordinator.data.get(self._counter_id)
        if counter is None or counter["free"] is None:
            return None
        return counter["free"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Counter status, official message, data age and GPS location."""
        counter = self.coordinator.data.get(self._counter_id)
        if not counter:
            return {}
        parking = PARKINGS[self._counter_id]
        attributes: dict[str, Any] = {
            "status": counter["status"],
            "latitude": parking["latitude"],
            "longitude": parking["longitude"],
        }
        if counter["message"]:
            attributes["message"] = counter["message"]
        if counter["age"] is not None:
            attributes["data_age"] = round(counter["age"])
        return attributes


class SanaryParkingTotalSensor(SensorEntity):
    """Total capacity of one parking, from the city's documentation."""

    entity_description = _TOTAL_DESCRIPTION

    def __init__(self, counter_id: str, parking: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._counter_id = counter_id
        self._attr_has_entity_name = True
        self._attr_unique_id = f"sanary_{counter_id}_total"
        self._attr_device_info = _device_info(counter_id, parking)
        self._attr_name = "total"
        self._attr_native_value = parking["total"]
