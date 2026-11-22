<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo_white.webp">
    <img src="assets/logo_color.webp" width="260" alt="Sanary-sur-Mer">
  </picture>
</p>

# Sanary-sur-Mer

[Home Assistant](https://www.home-assistant.io/) integration for the city of **Sanary-sur-Mer** (83110, Var, France), based on official data published on [sanarysurmer.com](https://www.sanarysurmer.com/).

## Disclaimer

This integration has been made with [Firefox](https://www.firefox.com/), [curl](https://curl.se/), [OpenCode](https://opencode.ai/desktop), [Scaleway](https://www.scaleway.com/en/generative-apis/) and [GLM 5.3](https://z.ai/blog/glm-5.3).

## Features

### Parking *(available)*

**Free spaces** for the municipal car parks, sourced from the city's official [parking map](https://www.sanarysurmer.com/parkings/):

| Device created                        | Source    |
| ------------------------------------- | --------- |
| Parking - Sanary - Esplanade          | counter 1 |
| Parking - Sanary - Picotières-Leclerc | counter 2 |
| Parking - Sanary - Arnaldi            | counter 4 |

Each car park is a separate **device** in Home Assistant with two sensors:

| Sensor    | Entity ID                                   | Source                                        |
| --------- | ------------------------------------------- | --------------------------------------------- |
| total     | `sensor.parking_sanary_esplanade_total`     | static capacity from the city's documentation |
| available | `sensor.parking_sanary_esplanade_available` | real-time counter from the city's parking map |

The `total` sensor uses the official capacities published in the city's [parking documentation](https://www.sanarysurmer.com/mes-services/mobilite-et-stationnement/):

- Esplanade 735
- Picotières-Leclerc 172
- Arnaldi 134

The `available` sensor attributes expose the counter status, the official message from the city hall, the age of the data and the GPS location of the car park (usable directly by the [Map card](https://www.home-assistant.io/dashboards/map/)).

The occupancy rate can be derived with a template: `available / total * 100`.

Devices are named after the city (`Parking - Sanary - <name>`, official parking names).

Sensors use `has_entity_name`, so the entity ID is naturally derived from the friendly name (ex: `sensor.parking_sanary_picotieres_leclerc_available`) and stays identical on every instance and language.

## Installation

### Via Marketplace (HACS)

1. In Home Assistant: **Settings → Marketplace**, ⋮ menu → **Custom repositories**
1. Add `https://github.com/rockyluke/ha-sanary` (category: integration)
1. Install **Sanary-sur-Mer**
1. Restart Home Assistant
1. **Settings → Devices & services → Add integration** → **Sanary-sur-Mer**

### Manually

Copy the `custom_components/sanary` folder into the `custom_components/` folder of your Home Assistant configuration, then follow steps 4 and 5 above.

## Configuration

| Option               | Description                                | Default |
| -------------------- | ------------------------------------------ | ------- |
| Polling interval (s) | How often the city hall website is queried | 300 s   |

The interval is set during installation and can be changed at any time in **Settings → Devices & services → Sanary-sur-Mer → Configure**, without a restart (60s minimum, 3600s maximum).

Since the city refreshes its counters every 30 seconds, data older than three times the configured interval is considered stale: the sensor then becomes `unavailable`.

## Compatibility

Tested with Home Assistant 2026.11. No external dependencies (uses `aiohttp`, bundled with Home Assistant).

The integration is localized in French (`translations/fr.json`) for the configuration dialog.
