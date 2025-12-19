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
from homeassistant.helpers.entity_platform import AddEntitiesCallback, AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_IS_SEGMENT, CONF_SLOPE_ID, DOMAIN
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
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Sporet sensor from a config entry."""
    coordinators = entry.runtime_data

    for subentry_id, coordinator in coordinators.items():
        async_add_entities(
            [
                SporetSensor(coordinator, description, subentry_id)
                for description in SENSOR_DESCRIPTIONS
            ]
        )


class SporetSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sporet sensor."""

    def __init__(
        self,
        coordinator: SporetDataUpdateCoordinator,
        description: SensorEntityDescription,
        subentry_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._slope_id = coordinator.slope_id
        self._is_segment = coordinator.is_segment
        self.entity_description = description
        self._attr_unique_id = f"{subentry_id}-{description.key}"
        self._attr_attribution = ATTRIBUTION
        self._subentry_id = subentry_id
        _LOGGER.debug(f"Setting up Sporet-sensor uid {self._attr_unique_id}")


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
            identifiers={(DOMAIN, self._subentry_id)},
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
            if self._is_segment:
                prepped_time = route_data.get("selectedSegment", {}).get("preppedTime")
            else:
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
            if self._is_segment:
                return route_data.get("selectedSegment", {}).get("prepSymbol")
            else:
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
        if self._is_segment:
            prep_symbol_parts = route_data.get("selectedSegment", {}).get("prepSymbolParts", [])
        else:
            prep_symbol_parts = route_data.get("prepSymbolParts", [])
        if prep_symbol_parts:
            attributes["prep_symbol_parts"] = prep_symbol_parts

        # Add additional route information
        route_info_mapping = {
            "hasClassic": "has_classic",
            "hasSkating": "has_skating",
            "hasFloodlight": "has_floodlight",
            "isScooterTrail": "is_scooter_trail",
            "routelength": "route_length",
            "totalElevationGain": "total_elevation_gain",
            "totalElevationLoss": "total_elevation_loss",
        }
        for api_key, attr_key in route_info_mapping.items():
            if self._is_segment:
                value = route_data.get("selectedSegment", {}).get(api_key)
            else:
                value = route_data.get(api_key)
            if value is not None:
                attributes[attr_key] = value

        return attributes
