# Sporet - Home Assistant Integration

A Home Assistant custom component for monitoring cross-country ski trail conditions from [Sporet.no](https://sporet.no/).

## Features

- Monitor ski trail segment status in real-time
- Track trail preparation time
- View preparation symbols (trail condition indicators)
- Get warning messages for trail conditions
- Automatic updates every 10 minutes
- Support for updating bearer tokens without re-adding the integration

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/yourusername/home-assistant-sporet`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Sporet" in the HACS integration list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/sporet` folder from this repository
2. Copy the entire `sporet` folder to your Home Assistant `custom_components` directory:
   - Path: `<config_dir>/custom_components/sporet/`
3. Restart Home Assistant

## Configuration

### Prerequisites

Before setting up the integration, you need:

1. **Slope ID**: Find this at [sporet.no](https://sporet.no/)
   - Navigate to your desired ski trail
   - The slope ID is typically found in the URL or on the trail details page
   - Example: For "Heistadmoen 10 km", the slope ID is `10550`

2. **Bearer Token**: Obtain from your Sporet account
   - Log in to sporet.no
   - Navigate to your account settings or API access section
   - Generate or copy your bearer token
   - Keep this token secure

3. **Ski Trail Segment ID**: Find this by inspecting the API response or trail details
   - Example segment IDs: `117649`, `117651`, etc.
   - Each slope contains multiple segments representing different trail sections

### Setup Steps

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Sporet"
4. Enter your configuration:
   - **Slope ID**: The slope identifier from sporet.no
   - **Ski Trail Segment ID**: The specific segment you want to monitor
   - **Bearer Token**: Your API authentication token
5. Click **Submit**

The integration will validate your credentials and create sensors for the specified trail segment.

## Sensors

The integration creates three sensors for each configured trail segment:

### 1. Prepped Time
- **Entity ID**: `sensor.<slope_name>_<segment_id>_prepped_time`
- **Description**: Timestamp of when the trail was last prepared
- **Device Class**: Timestamp
- **Example**: `2025-12-01T09:06:12Z`

### 2. Prep Symbol
- **Entity ID**: `sensor.<slope_name>_<segment_id>_prep_symbol`
- **Description**: Numeric code indicating trail condition
- **Values**:
  - `40`: Good condition
  - `70`: Poor condition or not groomed
  - Other values as defined by Sporet
- **Example**: `40`

### 3. Warning Text
- **Entity ID**: `sensor.<slope_name>_<segment_id>_warning_text`
- **Description**: Warning message about trail conditions
- **Example**: `null` (no warnings) or text describing issues

### Additional Attributes

Each sensor includes additional attributes with detailed segment information:

- `slope_id`: The slope identifier
- `segment_id`: The trail segment identifier
- `slope_name`: Name of the ski trail
- `hasClassic`: Boolean - Classic skiing available
- `hasSkating`: Boolean - Skating skiing available
- `hasFloodlight`: Boolean - Floodlight available
- `statusId`: Current status (e.g., "active")
- `segmentLength`: Length of the segment in meters
- `destinationId`: Associated destination ID
- `isScooterTrail`: Boolean - Scooter trail
- `trailTypeSymbol`: Trail type numeric code

## Updating Bearer Token

If your bearer token expires or needs to be updated:

1. Go to **Settings** → **Devices & Services**
2. Find the "Sporet" integration
3. Click **Configure**
4. Enter your new bearer token
5. Click **Submit**

The integration will reload with the new token without losing your configuration.

## Example Automation

### Notify when trail is freshly groomed

```yaml
automation:
  - alias: "Notify when trail is groomed"
    trigger:
      - platform: state
        entity_id: sensor.heistadmoen_10_km_117649_prepped_time
    condition:
      - condition: template
        value_template: >
          {{ (now() - states.sensor.heistadmoen_10_km_117649_prepped_time.state | as_datetime).total_seconds() < 3600 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Trail Groomed!"
          message: "Heistadmoen trail segment 117649 was just groomed."
```

### Display trail condition in Lovelace

```yaml
type: entities
title: Ski Trail Status
entities:
  - entity: sensor.heistadmoen_10_km_117649_prepped_time
    name: Last Groomed
  - entity: sensor.heistadmoen_10_km_117649_prep_symbol
    name: Condition
  - entity: sensor.heistadmoen_10_km_117649_warning_text
    name: Warnings
```

## API Details

The integration uses the Sporet public API:

- **Endpoint**: `https://api.sporet.no/loypeapi/public/skiroutes/{slope_id}/details`
- **Authentication**: Bearer token in Authorization header
- **Update Interval**: 600 seconds (10 minutes)
- **Method**: GET

## Troubleshooting

### Cannot Connect Error

- Verify your internet connection
- Check if sporet.no is accessible
- Ensure the API endpoint is not blocked by your firewall

### Invalid Auth Error

- Verify your bearer token is correct
- Check if the token has expired
- Regenerate a new token from sporet.no

### Segment Not Found Error

- Verify the segment ID exists in the specified slope
- Check the slope ID is correct
- Make a manual API call to verify the segment exists

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.sporet: debug
```

## Development

This integration includes a development container for easy testing:

1. Open the project in VS Code
2. Install the "Remote - Containers" extension
3. Click "Reopen in Container" when prompted
4. The development Home Assistant instance will start automatically
5. Access at `http://localhost:9123`

## Support

For issues, feature requests, or contributions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/home-assistant-sporet/issues)
- Discussions: [Join the discussion](https://github.com/yourusername/home-assistant-sporet/discussions)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Data provided by [Sporet.no](https://sporet.no/)
- Integration developed for Home Assistant


