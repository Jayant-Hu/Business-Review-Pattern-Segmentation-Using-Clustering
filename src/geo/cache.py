"""
Persistent SQLite Geocoding Cache.
Stores resolved coordinates, geocode status, and formatted addresses to prevent duplicate API calls.
"""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from src.utils.paths import settings
from src.utils.logging import logger

class GeocodeCache:
    """Manages persistent SQLite caching of geocoded addresses."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (settings.GEO_CACHE_DIR / "geocode_cache.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))
        
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS geocache (
                    address_key TEXT PRIMARY KEY,
                    latitude REAL,
                    longitude REAL,
                    city TEXT,
                    formatted_address TEXT,
                    place_id TEXT,
                    geocode_status TEXT,
                    geocode_confidence REAL,
                    source TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get(self, address_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached geocode entry if present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT latitude, longitude, city, formatted_address, place_id, geocode_status, geocode_confidence, source FROM geocache WHERE address_key = ?",
                (address_key,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'latitude': row[0],
                    'longitude': row[1],
                    'city': row[2],
                    'formatted_address': row[3],
                    'place_id': row[4],
                    'geocode_status': row[5],
                    'geocode_confidence': row[6],
                    'source': row[7]
                }
        return None

    def set(self, address_key: str, data: Dict[str, Any]):
        """Persists geocode entry into cache."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO geocache 
                (address_key, latitude, longitude, city, formatted_address, place_id, geocode_status, geocode_confidence, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                address_key,
                data.get('latitude'),
                data.get('longitude'),
                data.get('city'),
                data.get('formatted_address'),
                data.get('place_id'),
                data.get('geocode_status', 'OK'),
                data.get('geocode_confidence', 1.0),
                data.get('source', 'unknown')
            ))
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Returns total entries and counts of successful vs failed coordinates."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*), count(latitude) FROM geocache")
            total, resolved = cursor.fetchone()
            return {'total_cached': total, 'resolved': resolved}
