"""Constants for the Sanary-sur-Mer integration."""

from homeassistant.const import Platform

# Integration for the city of Sanary-sur-Mer (Var, France).
# For now, only parking data is handled; other city services
# (beaches, markets, waste collection...) can be added here later.
DOMAIN = "sanary"
PLATFORMS = [Platform.SENSOR]

# Official data source from the city hall (parking map).
ENDPOINT = "https://www.sanarysurmer.com/parkings/mapstates.json"
CONFIGURATION_URL = "https://www.sanarysurmer.com/parkings/"

# Official counters: 1 = Esplanade, 2 = Leclerc, 4 = Arnaldi
# (counter 3 is out of service on the city side).
# "total" is the static capacity, from the city's official parking
# documentation (the real-time API only exposes free spaces):
# https://www.sanarysurmer.com/mes-services/mobilite-et-stationnement/
PARKINGS: dict[str, dict[str, str | float | int]] = {
    "1": {"name": "Esplanade", "total": 735, "latitude": 43.1156397, "longitude": 5.7906263},
    "2": {"name": "Picotières-Leclerc", "total": 172, "latitude": 43.1185749, "longitude": 5.7987220},
    "4": {"name": "Arnaldi", "total": 134, "latitude": 43.1196128, "longitude": 5.8017488},
}

# Polling interval (seconds).
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300
MIN_SCAN_INTERVAL = 60
MAX_SCAN_INTERVAL = 3600

# Data older than 3 x the polling interval is considered stale,
# matching the behaviour of the city's official parking map.
STALE_FACTOR = 3
