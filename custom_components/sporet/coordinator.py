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
        slope_id: str,
        is_segment: bool = False,
    ) -> None:
        """Initialize."""
        self.slope_id = slope_id
        self._bearer_token = bearer_token
        self.is_segment = is_segment
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
            if self.is_segment:
                data = await api.async_get_segment_details(self.slope_id)
                _LOGGER.debug("Updated data for segment %s: %s", self.slope_id, data)

                # Extract data from the new API structure (top-level fields)
                slope_id = data.get('selectedSegment', {}).get('id')
                slope_name = f"Segment {slope_id}"

                destinations = [data.get('destination', {})]
                destination_name = destinations[0].get("name") if destinations else "Unknown"
            else:
                data = await api.async_get_route_details(self.slope_id)
                _LOGGER.debug("Updated data for route %s: %s", self.slope_id, data)

                # Extract data from the new API structure (top-level fields)
                slope_id = data.get("id")
                slope_name = data.get("name", "Unknown")

                # Get destination name from destinations array
                destinations = data.get("destinations", [])
                destination_name = destinations[0].get("name") if destinations else "Unknown"

            # Return the route data with the new structure
            return {
                "slope_name": slope_name,
                "slope_id": slope_id,
                "route_data": data,  # Store full route data for sensor access
                "destinations": destinations,
                "prepped_by": data.get("preppedBy", []),
            }

        except SporetAPIError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

