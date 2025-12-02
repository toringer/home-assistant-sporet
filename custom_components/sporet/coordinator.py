"""Data update coordinator for Sporet."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SporetAPI, SporetAPIError
from .const import DOMAIN, UPDATE_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class SporetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Sporet data."""

    def __init__(
        self,
        hass: HomeAssistant,
        bearer_token: str,
        segment_id: str,
    ) -> None:
        """Initialize."""
        self.segment_id = segment_id
        self._bearer_token = bearer_token
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Sporet."""
        session = async_get_clientsession(self.hass)
        api = SporetAPI(session, self._bearer_token)

        try:
            data = await api.async_get_segment_details(self.segment_id)
            _LOGGER.debug("Updated data for segment %s: %s", self.segment_id, data)

            # Extract the selected segment data from the new API structure
            selected_segment = data.get("selectedSegment", {})
            destination = data.get("destination", {})
            routes = data.get("routes", [])

            # Try to find the route name that contains this segment
            route_name = None
            if routes:
                for route in routes:
                    if "skiTrailSegments" in route:
                        for segment in route["skiTrailSegments"]:
                            if str(segment.get("id")) == str(self.segment_id):
                                route_name = route.get("name")
                                break
                    if route_name:
                        break

            # Build a descriptive name
            segment_name = destination.get("name", "Unknown")
            if route_name:
                segment_name = f"{destination.get('name', 'Unknown')} - {route_name}"

            # Return the segment data with the new structure
            return {
                "segment_name": segment_name,
                "segment_id": selected_segment.get("id"),
                "segment": selected_segment,
                "destination": destination,
                "routes": routes,
                "prepped_by": data.get("preppedBy", []),
            }

        except SporetAPIError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

