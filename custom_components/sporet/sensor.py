"""Sensor platform for Sporet."""

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_SLOPE_ID, DOMAIN
from .coordinator import SporetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="prepped_time",
        name="Prepped Time",
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="prep_symbol",
        name="Prep Symbol",
        icon="mdi:snowflake",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sporet sensor from a config entry."""
    coordinator: SporetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SporetSensor(coordinator, description, entry.data[CONF_SLOPE_ID])
            for description in SENSOR_DESCRIPTIONS
        ]
    )


class SporetSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sporet sensor."""

    def __init__(
        self,
        coordinator: SporetDataUpdateCoordinator,
        description: SensorEntityDescription,
        slope_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._slope_id = slope_id
        self._attr_unique_id = f"{DOMAIN}_{slope_id}_{description.key}"
        self._attr_attribution = ATTRIBUTION

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self.coordinator.data is None:
            return f"Sporet {self._slope_id} {self.entity_description.name}"

        slope_name = self.coordinator.data.get("slope_name", "Unknown")
        return f"{slope_name} {self.entity_description.name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information to group entities."""
        slope_name = "Unknown"
        if self.coordinator.data:
            slope_name = self.coordinator.data.get("slope_name", "Unknown")

        return DeviceInfo(
            identifiers={(DOMAIN, self._slope_id)},
            name=slope_name,
            manufacturer="Sporet",
            model="Ski Trail Route",
            entry_type=None,
        )

    @property
    def native_value(self) -> str | int | datetime | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        route_data = self.coordinator.data.get("route_data")
        if route_data is None:
            return None

        key = self.entity_description.key

        if key == "prepped_time":
            prepped_time = route_data.get("preppedTime")
            if prepped_time:
                try:
                    # Parse ISO 8601 datetime string
                    return datetime.fromisoformat(prepped_time.replace("Z", "+00:00"))
                except (ValueError, AttributeError) as err:
                    _LOGGER.error("Error parsing preppedTime: %s", err)
                    return None
            return None

        if key == "prep_symbol":
            return route_data.get("prepSymbol")

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        route_data = self.coordinator.data.get("route_data")
        if route_data is None:
            return {}

        attributes = {
            "slope_id": self._slope_id,
            "slope_name": self.coordinator.data.get("slope_name"),
        }

        # Add destination information
        destinations = self.coordinator.data.get("destinations", [])
        if destinations:
            destination = destinations[0]
            attributes["destination_name"] = destination.get("name")
            attributes["county"] = destination.get("countyName")
            attributes["municipal"] = destination.get("municipalName")
            attributes["country"] = destination.get("country")

        # Add prepped by information
        prepped_by = self.coordinator.data.get("prepped_by", [])
        if prepped_by:
            attributes["prepped_by"] = ", ".join(
                [org.get("name", "") for org in prepped_by]
            )

        # Add prepSymbolParts array to all sensors
        prep_symbol_parts = route_data.get("prepSymbolParts", [])
        if prep_symbol_parts:
            attributes["prep_symbol_parts"] = prep_symbol_parts

        # Add additional route information
        for key in [
            "hasClassic",
            "hasSkating",
            "hasFloodlight",
            "isScooterTrail",
            "routelength",
            "totalElevationGain",
            "totalElevationLoss",
        ]:
            value = route_data.get(key)
            if value is not None:
                attributes[key] = value

        return attributes
