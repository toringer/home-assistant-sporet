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

from .const import CONF_SEGMENT_ID, DOMAIN
from .coordinator import SporetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="preppedTime",
        name="Prepped Time",
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="prepSymbol",
        name="Prep Symbol",
        icon="mdi:snowflake",
    ),
    SensorEntityDescription(
        key="warningText",
        name="Warning Text",
        icon="mdi:alert-outline",
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
            SporetSensor(coordinator, description, entry.data[CONF_SEGMENT_ID])
            for description in SENSOR_DESCRIPTIONS
        ]
    )


class SporetSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sporet sensor."""

    def __init__(
        self,
        coordinator: SporetDataUpdateCoordinator,
        description: SensorEntityDescription,
        segment_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._segment_id = segment_id
        self._attr_unique_id = f"{DOMAIN}_{segment_id}_{description.key}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self.coordinator.data is None:
            return f"Sporet {self._segment_id} {self.entity_description.name}"

        segment_name = self.coordinator.data.get("segment_name", "Unknown")
        return f"{segment_name} {self.entity_description.name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information to group entities."""
        segment_name = "Unknown"
        if self.coordinator.data:
            segment_name = self.coordinator.data.get("segment_name", "Unknown")

        return DeviceInfo(
            identifiers={(DOMAIN, self._segment_id)},
            name=segment_name,
            manufacturer="Sporet",
            model="Ski Trail Segment",
            entry_type=None,
        )

    @property
    def native_value(self) -> str | int | datetime | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        segment = self.coordinator.data.get("segment")
        if segment is None:
            return None

        key = self.entity_description.key

        if key == "preppedTime":
            prepped_time = segment.get("preppedTime")
            if prepped_time:
                try:
                    # Parse ISO 8601 datetime string
                    return datetime.fromisoformat(prepped_time.replace("Z", "+00:00"))
                except (ValueError, AttributeError) as err:
                    _LOGGER.error("Error parsing preppedTime: %s", err)
                    return None
            return None

        if key == "prepSymbol":
            return segment.get("prepSymbol")

        if key == "warningText":
            return segment.get("warningText")

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        segment = self.coordinator.data.get("segment")
        if segment is None:
            return {}

        attributes = {
            "segment_id": self._segment_id,
            "segment_name": self.coordinator.data.get("segment_name"),
        }

        # Add destination information
        destination = self.coordinator.data.get("destination", {})
        if destination:
            attributes["destination_name"] = destination.get("name")
            attributes["county"] = destination.get("countyName")
            attributes["municipal"] = destination.get("municipalName")
            attributes["country"] = destination.get("country")

        # Add prepped by information
        prepped_by = self.coordinator.data.get("prepped_by", [])
        if prepped_by:
            attributes["prepped_by"] = ", ".join([org.get("name", "") for org in prepped_by])

        # Add additional segment information
        for key in [
            "hasClassic",
            "hasSkating",
            "hasFloodlight",
            "statusId",
            "segmentLength",
            "destinationId",
            "isScooterTrail",
            "trailTypeSymbol",
            "totalElevationGain",
            "totalElevationLoss",
        ]:
            value = segment.get(key)
            if value is not None:
                attributes[key] = value

        return attributes

