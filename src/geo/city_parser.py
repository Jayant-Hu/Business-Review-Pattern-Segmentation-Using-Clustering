"""
Address parsing utility to extract city, region, and postal codes.
Handles Gulf (Saudi Arabia, Kuwait, UAE, Qatar) and international formats.
"""
import re
from typing import Dict, Optional, Tuple

# Known major cities in Saudi Arabia & GCC
KNOWN_CITIES = [
    'Riyadh', 'Jeddah', 'Mecca', 'Makkah', 'Medina', 'Madinah',
    'Dammam', 'Khobar', 'Al Khobar', 'Dhahran', 'Tabuk', 'Taif',
    'Abha', 'Khamis Mushait', 'Buraidah', 'Hail', 'Najran', 'Jizan',
    'Al Jubail', 'Yanbu', 'Al Ahsa', 'Hofuf', 'Kuwait', 'Shuwaikh',
    'Dubai', 'Abu Dhabi', 'Sharjah', 'Doha', 'Manama', 'Muscat',
    'London', 'Cardiff', 'Birmingham', 'Manchester', 'Edinburgh',
    'الرياض', 'جدة', 'مكة', 'المدينة المنورة', 'الدمام', 'الخبر'
]

# Mapping Arabic city names to English
ARABIC_CITY_MAP = {
    'الرياض': 'Riyadh',
    'جدة': 'Jeddah',
    'مكة': 'Mecca',
    'المدينة المنورة': 'Medina',
    'الدمام': 'Dammam',
    'الخبر': 'Khobar'
}

def parse_address_components(address: str) -> Dict[str, Optional[str]]:
    """
    Parses unstructured address string into normalized city, region, postal_code, and country.
    """
    if not address or not isinstance(address, str) or address.strip() in ['0', 'nan', 'Unknown Address']:
        return {'city': 'Unknown', 'region': 'Unknown', 'postal_code': None, 'country': 'Unknown'}
        
    addr_clean = address.strip()
    
    # 1. Postal code extraction (e.g., 5-digit Saudi code '13322', or UK postcodes 'CF10 2BH')
    postal_code = None
    postal_match = re.search(r'\b\d{5}\b', addr_clean)
    if postal_match:
        postal_code = postal_match.group(0)
    else:
        uk_match = re.search(r'\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b', addr_clean, re.IGNORECASE)
        if uk_match:
            postal_code = uk_match.group(0).upper()

    # 2. Country extraction
    country = 'Unknown'
    if 'Saudi Arabia' in addr_clean or 'المملكة العربية السعودية' in addr_clean:
        country = 'Saudi Arabia'
    elif 'Kuwait' in addr_clean or 'الكويت' in addr_clean:
        country = 'Kuwait'
    elif 'United Kingdom' in addr_clean or 'UK' in addr_clean:
        country = 'United Kingdom'
    elif 'United Arab Emirates' in addr_clean or 'UAE' in addr_clean or 'الإمارات' in addr_clean:
        country = 'United Arab Emirates'
    elif 'Qatar' in addr_clean or 'قطر' in addr_clean:
        country = 'Qatar'

    # 3. City extraction
    city = 'Unknown'
    # Check known cities
    for kc in KNOWN_CITIES:
        pattern = r'(?i)\b' + re.escape(kc) + r'\b'
        if re.search(pattern, addr_clean):
            city = ARABIC_CITY_MAP.get(kc, kc)
            if city in ['Al Khobar']:
                city = 'Khobar'
            elif city in ['Makkah']:
                city = 'Mecca'
            elif city in ['Madinah']:
                city = 'Medina'
            break
            
    # Fallback: check comma-separated segments
    if city == 'Unknown':
        parts = [p.strip() for p in addr_clean.split(',') if p.strip()]
        if len(parts) >= 2:
            # Often city is the second to last part before country
            candidate = parts[-2]
            # Strip postal codes from candidate
            candidate_clean = re.sub(r'\b\d{5}\b', '', candidate).strip()
            if candidate_clean and len(candidate_clean) < 30:
                city = candidate_clean
                
    # 4. Region / District
    region = 'Unknown'
    parts = [p.strip() for p in addr_clean.split(',') if p.strip()]
    if len(parts) >= 3:
        region = parts[1]
    elif len(parts) == 2:
        region = parts[0]
        
    return {
        'city': city if city else 'Unknown',
        'region': region if region else 'Unknown',
        'postal_code': postal_code,
        'country': country
    }
