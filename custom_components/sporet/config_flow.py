"""Config flow for Sporet integration."""

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_BASE_URL,
    CONF_BEARER_TOKEN,
    CONF_SEGMENT_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    bearer_token = data[CONF_BEARER_TOKEN]
    segment_id = data[CONF_SEGMENT_ID]

    session = async_get_clientsession(hass)
    url = f"{API_BASE_URL}/{segment_id}/details"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 401:
                raise InvalidAuth
            response.raise_for_status()
            api_data = await response.json()

            # Extract data from the new API structure
            selected_segment = api_data.get("selectedSegment", {})
            destination = api_data.get("destination", {})
            routes = api_data.get("routes", [])

            # Verify the segment exists
            if not selected_segment or selected_segment.get("id") != int(segment_id):
                raise CannotConnect

            # Try to find the route name that contains this segment
            route_name = None
            if routes:
                for route in routes:
                    if "skiTrailSegments" in route:
                        for segment in route["skiTrailSegments"]:
                            if str(segment.get("id")) == str(segment_id):
                                route_name = route.get("name")
                                break
                    if route_name:
                        break

            # Build a descriptive name
            segment_name = destination.get("name", f"Segment {segment_id}")
            if route_name:
                segment_name = f"{destination.get('name', 'Unknown')} - {route_name}"

            # Return segment name for display
            return {
                "title": segment_name,
                "segment_name": segment_name,
            }

    except aiohttp.ClientResponseError as err:
        if err.status == 401:
            raise InvalidAuth
        raise CannotConnect
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to Sporet API: %s", err)
        raise CannotConnect


class SporetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sporet."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except SegmentNotFound:
                errors["base"] = "segment_not_found"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID based on segment_id
                await self.async_set_unique_id(user_input[CONF_SEGMENT_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SEGMENT_ID): str,
                vol.Required(CONF_BEARER_TOKEN): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SporetOptionsFlowHandler()


class SporetOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Sporet options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the new bearer token
            test_data = {
                CONF_SEGMENT_ID: self.config_entry.data[CONF_SEGMENT_ID],
                CONF_BEARER_TOKEN: user_input[CONF_BEARER_TOKEN],
            }

            try:
                await validate_input(self.hass, test_data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Update the config entry with the new bearer token
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **self.config_entry.data,
                        CONF_BEARER_TOKEN: user_input[CONF_BEARER_TOKEN],
                    },
                )
                return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_BEARER_TOKEN,
                    default=self.config_entry.data.get(CONF_BEARER_TOKEN, ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""


