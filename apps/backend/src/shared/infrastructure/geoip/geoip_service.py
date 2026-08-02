import os
from dataclasses import dataclass

from src.core.config.settings import config
from src.shared.infrastructure.logger import logger


@dataclass(frozen=True)
class GeoLocation:
    """
    Resolved geolocation for an IP address. Any field may be None when the
    underlying database has no value for it.
    """

    country_iso: str | None = None
    country_name: str | None = None
    city: str | None = None


class GeoIPService:
    """
    Thin wrapper around a MaxMind GeoLite2-City reader.

    The reader is opened once at application startup and reused for the process
    lifetime - lookups are in-memory (no network, no per-request I/O), so they
    are effectively free. The service always fails open: if the feature is
    disabled, the database is missing, or a lookup errors, it returns None
    instead of raising, so callers never have to guard geolocation.
    """

    def __init__(self):
        self._reader = None

    def load(self) -> None:
        """
        Open the GeoLite2 database. Called once during the app lifespan startup.
        No-ops (and logs) when disabled or the file is absent.
        """
        if not config.GEOIP_ENABLED or not config.GEOIP_DB_PATH:
            logger.info("GeoIP disabled or no database path configured; skipping load.")
            return

        if not os.path.exists(config.GEOIP_DB_PATH):
            logger.warning(
                "GeoIP database not found at %s; geolocation will be unavailable.",
                config.GEOIP_DB_PATH,
            )
            return

        try:
            import geoip2.database

            self._reader = geoip2.database.Reader(config.GEOIP_DB_PATH)
            logger.info("GeoIP database loaded from %s", config.GEOIP_DB_PATH)
        except Exception as e:  # pragma: no cover - defensive, never block startup
            self._reader = None
            logger.warning("Failed to load GeoIP database: %s", e)

    def close(self) -> None:
        """Close the reader during lifespan shutdown."""
        if self._reader is not None:
            self._reader.close()
            self._reader = None

    @property
    def is_available(self) -> bool:
        """Whether a reader is loaded and ready to serve lookups."""
        return self._reader is not None

    def lookup(self, ip_address: str | None) -> GeoLocation | None:
        """
        Resolve an IP address to a GeoLocation. Returns None when geolocation is
        unavailable, the IP is missing/unknown, or the address is not found
        (e.g. private/loopback ranges).

        Supports both GeoLite2-City and GeoLite2-Country databases: when the
        loaded database is country-only, city lookups fall back to country
        resolution and ``city`` stays None.
        """
        if self._reader is None or not ip_address or ip_address == "unknown":
            return None

        city = None
        country_iso = None
        country_name = None

        for method in ("city", "country"):
            try:
                response = getattr(self._reader, method)(ip_address)
            except ValueError:
                # Database type does not support this method
                # (e.g. calling city() on a country-only database).
                continue
            except Exception:
                # AddressNotFoundError (unknown/private IP), malformed input, etc.
                return None

            country_iso = response.country.iso_code
            country_name = response.country.name
            if method == "city":
                city = response.city.name
            break

        if country_iso is None and country_name is None:
            return None

        return GeoLocation(
            country_iso=country_iso,
            country_name=country_name,
            city=city,
        )


# Process-wide singleton. Loaded in the app lifespan and shared across requests.
geoip_service = GeoIPService()
