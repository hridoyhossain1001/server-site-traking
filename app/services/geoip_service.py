import os
import logging
import httpx
import maxminddb

logger = logging.getLogger(__name__)

DB_URL = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"
DB_PATH = "GeoLite2-City.mmdb"

_reader = None

async def download_geoip_db_if_missing():
    """Download the GeoLite2 City database if it doesn't exist."""
    global _reader
    if not os.path.exists(DB_PATH):
        logger.info(f"Downloading GeoIP database from {DB_URL} (this may take a minute)...")
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(DB_URL, timeout=60.0)
                response.raise_for_status()
                with open(DB_PATH, "wb") as f:
                    f.write(response.content)
            logger.info("GeoIP database downloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to download GeoIP database: {e}")
            return
    
    # Initialize reader
    try:
        _reader = maxminddb.open_database(DB_PATH)
        logger.info("GeoIP database loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load GeoIP database: {e}")

def get_location_data(ip_address: str) -> dict:
    """
    Get city, state, country, and zip code from IP address.
    Returns a dict with 'ct', 'st', 'country', 'zp' keys.
    """
    if not _reader or not ip_address:
        return {}
    
    try:
        data = _reader.get(ip_address)
        if not data:
            return {}

        loc = {}
        
        # City
        if 'city' in data and 'names' in data['city'] and 'en' in data['city']['names']:
            loc['ct'] = data['city']['names']['en']
            
        # State/Region
        if 'subdivisions' in data and len(data['subdivisions']) > 0:
            sub = data['subdivisions'][0]
            if 'iso_code' in sub:
                loc['st'] = sub['iso_code']
            elif 'names' in sub and 'en' in sub['names']:
                loc['st'] = sub['names']['en']
                
        # Country
        if 'country' in data and 'iso_code' in data['country']:
            loc['country'] = data['country']['iso_code'].lower()
            
        # Zip Code
        if 'postal' in data and 'code' in data['postal']:
            loc['zp'] = data['postal']['code']
            
        return loc
    except Exception as e:
        logger.warning(f"GeoIP lookup failed for IP {ip_address}: {e}")
        return {}

def close_geoip_db():
    global _reader
    if _reader:
        _reader.close()
        _reader = None
