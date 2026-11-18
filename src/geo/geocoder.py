"""
Robust Geocoding Service.
Supports:
1. Google Maps Geocoding API (Primary, when GOOGLE_MAPS_API_KEY is configured).
2. OpenStreetMap / Nominatim via geopy (Fallback, with strict rate-limiting).
3. City-center spatial jitter fallback for unresolvable addresses with known cities.
All calls pass through persistent SQLite caching.
"""
import time
import requests
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from src.utils.paths import settings
from src.utils.logging import logger
from src.geo.cache import GeocodeCache
from src.geo.city_parser import parse_address_components

# Reference City Centroids (lat, lng) for Gulf & International hubs
CITY_CENTROIDS: Dict[str, Tuple[float, float]] = {
    'Riyadh': (24.7136, 46.6753),
    'Jeddah': (21.5433, 39.1728),
    'Mecca': (21.3891, 39.8579),
    'Medina': (24.5247, 39.5692),
    'Dammam': (26.4207, 50.0888),
    'Khobar': (26.2172, 50.1971),
    'Dhahran': (26.2361, 50.0393),
    'Taif': (21.4373, 40.5127),
    'Tabuk': (28.3835, 36.5662),
    'Abha': (18.2164, 42.5053),
    'Khamis Mushait': (18.3000, 42.7333),
    'Buraidah': (26.3592, 43.9818),
    'Al Jubail': (27.0112, 49.6583),
    'Yanbu': (24.0891, 38.0637),
    'Al Ahsa': (25.3833, 49.5833),
    'Kuwait': (29.3759, 47.9774),
    'Shuwaikh': (29.3500, 47.9500),
    'Dubai': (25.2048, 55.2708),
    'Abu Dhabi': (24.4539, 54.3773),
    'Doha': (25.2854, 51.5310),
    'Cardiff': (51.4816, -3.1791),
    'Birmingham': (52.4862, -1.8904),
    'London': (51.5074, -0.1278)
}

class GeocoderService:
    """Manages address geocoding with caching, retries, and API fallbacks."""
    
    def __init__(self, cache: Optional[GeocodeCache] = None):
        self.cache = cache or GeocodeCache()
        self.api_key = settings.get_google_maps_key()
        self.nominatim = Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)
        
    def geocode_address(self, place: str, address: str, use_network_fallback: bool = False) -> Dict[str, Any]:
        """Geocodes a single (place, address) entity with hierarchical fallback."""
        parsed = parse_address_components(address)
        city = parsed['city']
        
        # Cache key combines place + address
        cache_key = f"{place.strip()} || {address.strip()}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
            
        result = None
        # 1. Primary: Google Maps Geocoding API if key configured
        if self.api_key:
            result = self._geocode_google(place, address, city)
            
        # 2. Fallback: Nominatim / OpenStreetMap (only if explicitly allowed to prevent rate limit blocking)
        if use_network_fallback and (not result or result.get('latitude') is None):
            result = self._geocode_nominatim(address, city)
            
        # 3. Third-level Fallback: Instant high-precision city centroid with spatial jitter
        if not result or result.get('latitude') is None:
            result = self._geocode_centroid_fallback(city, parsed)
            
        result['city'] = city
        self.cache.set(cache_key, result)
        return result

    def _geocode_google(self, place: str, address: str, city: str) -> Optional[Dict[str, Any]]:
        """Queries Google Geocoding API."""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            query = f"{place}, {address}" if place != "Unknown Business" else address
            params = {"address": query, "key": self.api_key}
            
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == 'OK' and len(data.get('results', [])) > 0:
                    top = data['results'][0]
                    loc = top['geometry']['location']
                    return {
                        'latitude': float(loc['lat']),
                        'longitude': float(loc['lng']),
                        'formatted_address': top.get('formatted_address', address),
                        'place_id': top.get('place_id'),
                        'geocode_status': 'GOOGLE_OK',
                        'geocode_confidence': 0.95,
                        'source': 'google_geocoding'
                    }
        except Exception as e:
            logger.warning(f"Google Geocoding error for '{address}': {e}")
        return None

    def _geocode_nominatim(self, address: str, city: str) -> Optional[Dict[str, Any]]:
        """Queries OpenStreetMap Nominatim with rate-limiting."""
        time.sleep(settings.NOMINATIM_RATE_LIMIT_SEC)
        try:
            # Query with city context
            query = address if city == 'Unknown' else f"{city}, Saudi Arabia"
            loc = self.nominatim.geocode(query, timeout=4)
            if loc:
                return {
                    'latitude': float(loc.latitude),
                    'longitude': float(loc.longitude),
                    'formatted_address': loc.address,
                    'place_id': str(loc.raw.get('place_id', '')),
                    'geocode_status': 'NOMINATIM_OK',
                    'geocode_confidence': 0.75,
                    'source': 'nominatim'
                }
        except Exception as e:
            logger.debug(f"Nominatim lookup failed: {e}")
        return None

    def _geocode_centroid_fallback(self, city: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Provides spatial jitter around verified city centroids for unresolvable streets."""
        if city in CITY_CENTROIDS:
            base_lat, base_lng = CITY_CENTROIDS[city]
            # Add subtle jitter (+/- ~2km) so markers do not stack exactly on a single pixel
            jitter_lat = base_lat + np.random.uniform(-0.015, 0.015)
            jitter_lng = base_lng + np.random.uniform(-0.015, 0.015)
            return {
                'latitude': float(jitter_lat),
                'longitude': float(jitter_lng),
                'formatted_address': f"{city}, {parsed.get('country', 'Saudi Arabia')}",
                'place_id': f"centroid_{city.lower()}",
                'geocode_status': 'CITY_CENTROID_ESTIMATE',
                'geocode_confidence': 0.60,
                'source': 'centroid_fallback'
            }
        else:
            # Default to Riyadh central coordinates
            base_lat, base_lng = CITY_CENTROIDS['Riyadh']
            return {
                'latitude': float(base_lat + np.random.uniform(-0.02, 0.02)),
                'longitude': float(base_lng + np.random.uniform(-0.02, 0.02)),
                'formatted_address': 'Saudi Arabia',
                'place_id': 'default_country',
                'geocode_status': 'DEFAULT_FALLBACK',
                'geocode_confidence': 0.30,
                'source': 'default_fallback'
            }

    def geocode_businesses_dataframe(self, biz_df: pd.DataFrame, max_records: Optional[int] = None) -> pd.DataFrame:
        """Batch geocodes unique businesses in a DataFrame and appends geo columns."""
        logger.info(f"Geocoding {len(biz_df)} businesses (max_records={max_records})...")
        df = biz_df.copy()
        
        target_df = df if max_records is None else df.head(max_records)
        
        lats, lngs, cities, statuses, confidences, sources = [], [], [], [], [], []
        
        total = len(target_df)
        for i, row in target_df.iterrows():
            geo = self.geocode_address(row['place'], row['address'])
            lats.append(geo.get('latitude'))
            lngs.append(geo.get('longitude'))
            cities.append(geo.get('city', 'Unknown'))
            statuses.append(geo.get('geocode_status', 'UNKNOWN'))
            confidences.append(geo.get('geocode_confidence', 0.0))
            sources.append(geo.get('source', 'none'))
            
            if (len(lats) % 250 == 0) or (len(lats) == total):
                logger.info(f"Geocoded {len(lats)}/{total} businesses...")
                
        df.loc[target_df.index, 'latitude'] = lats
        df.loc[target_df.index, 'longitude'] = lngs
        df.loc[target_df.index, 'city'] = cities
        df.loc[target_df.index, 'geocode_status'] = statuses
        df.loc[target_df.index, 'geocode_confidence'] = confidences
        df.loc[target_df.index, 'geocode_source'] = sources
        
        return df
