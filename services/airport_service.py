"""Airport and city lookup service with comprehensive worldwide airport coverage."""

from typing import Dict, List, Optional
import re


# Database of major airports worldwide with focus on India, Asia, Middle East, Europe, and Americas
AIRPORTS_DB: List[Dict[str, str]] = [
    # India - South
    {"iata": "COK", "name": "Cochin International Airport", "city": "Kochi", "state": "Kerala", "country": "India"},
    {"iata": "TRV", "name": "Trivandrum International Airport", "city": "Thiruvananthapuram", "state": "Kerala", "country": "India"},
    {"iata": "CCJ", "name": "Calicut International Airport", "city": "Kozhikode", "state": "Kerala", "country": "India"},
    {"iata": "CNN", "name": "Kannur International Airport", "city": "Kannur", "state": "Kerala", "country": "India"},
    {"iata": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore", "state": "Karnataka", "country": "India"},
    {"iata": "MAA", "name": "Chennai International Airport", "city": "Chennai", "state": "Tamil Nadu", "country": "India"},
    {"iata": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "state": "Telangana", "country": "India"},
    {"iata": "CJB", "name": "Coimbatore International Airport", "city": "Coimbatore", "state": "Tamil Nadu", "country": "India"},
    {"iata": "TRZ", "name": "Tiruchirappalli International Airport", "city": "Tiruchirappalli", "state": "Tamil Nadu", "country": "India"},
    {"iata": "IXE", "name": "Mangaluru International Airport", "city": "Mangalore", "state": "Karnataka", "country": "India"},
    {"iata": "IXM", "name": "Madurai Airport", "city": "Madurai", "state": "Tamil Nadu", "country": "India"},
    {"iata": "VGA", "name": "Vijayawada Airport", "city": "Vijayawada", "state": "Andhra Pradesh", "country": "India"},
    {"iata": "VTZ", "name": "Visakhapatnam Airport", "city": "Visakhapatnam", "state": "Andhra Pradesh", "country": "India"},

    # India - North & Central
    {"iata": "DEL", "name": "Indira Gandhi International Airport", "city": "Delhi", "state": "Delhi", "country": "India"},
    {"iata": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "state": "Maharashtra", "country": "India"},
    {"iata": "CCU", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata", "state": "West Bengal", "country": "India"},
    {"iata": "AMD", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "state": "Gujarat", "country": "India"},
    {"iata": "PNQ", "name": "Pune International Airport", "city": "Pune", "state": "Maharashtra", "country": "India"},
    {"iata": "GOI", "name": "Dabolim Airport", "city": "Goa", "state": "Goa", "country": "India"},
    {"iata": "GOX", "name": "Manohar International Airport (Mopa)", "city": "Goa", "state": "Goa", "country": "India"},
    {"iata": "JAI", "name": "Jaipur International Airport", "city": "Jaipur", "state": "Rajasthan", "country": "India"},
    {"iata": "LKO", "name": "Chaudhary Charan Singh International Airport", "city": "Lucknow", "state": "Uttar Pradesh", "country": "India"},
    {"iata": "PAT", "name": "Jay Prakash Narayan Airport", "city": "Patna", "state": "Bihar", "country": "India"},
    {"iata": "GAU", "name": "Lokpriya Gopinath Bordoloi International Airport", "city": "Guwahati", "state": "Assam", "country": "India"},
    {"iata": "SXR", "name": "Sheikh ul-Alam International Airport", "city": "Srinagar", "state": "Jammu and Kashmir", "country": "India"},
    {"iata": "IXC", "name": "Shaheed Bhagat Singh International Airport", "city": "Chandigarh", "state": "Punjab", "country": "India"},
    {"iata": "ATQ", "name": "Sri Guru Ram Dass Jee International Airport", "city": "Amritsar", "state": "Punjab", "country": "India"},
    {"iata": "BBI", "name": "Biju Patnaik Airport", "city": "Bhubaneswar", "state": "Odisha", "country": "India"},
    {"iata": "IDR", "name": "Devi Ahilya Bai Holkar Airport", "city": "Indore", "state": "Madhya Pradesh", "country": "India"},
    {"iata": "BHO", "name": "Raja Bhoj Airport", "city": "Bhopal", "state": "Madhya Pradesh", "country": "India"},
    {"iata": "NAG", "name": "Dr. Babasaheb Ambedkar International Airport", "city": "Nagpur", "state": "Maharashtra", "country": "India"},
    {"iata": "VNS", "name": "Lal Bahadur Shastri Airport", "city": "Varanasi", "state": "Uttar Pradesh", "country": "India"},
    {"iata": "IXB", "name": "Bagdogra Airport", "city": "Siliguri", "state": "West Bengal", "country": "India"},

    # Middle East
    {"iata": "DXB", "name": "Dubai International Airport", "city": "Dubai", "state": "", "country": "United Arab Emirates"},
    {"iata": "AUH", "name": "Zayed International Airport", "city": "Abu Dhabi", "state": "", "country": "United Arab Emirates"},
    {"iata": "SHJ", "name": "Sharjah International Airport", "city": "Sharjah", "state": "", "country": "United Arab Emirates"},
    {"iata": "DOH", "name": "Hamad International Airport", "city": "Doha", "state": "", "country": "Qatar"},
    {"iata": "BAH", "name": "Bahrain International Airport", "city": "Manama", "state": "", "country": "Bahrain"},
    {"iata": "MCT", "name": "Muscat International Airport", "city": "Muscat", "state": "", "country": "Oman"},
    {"iata": "KWI", "name": "Kuwait International Airport", "city": "Kuwait City", "state": "", "country": "Kuwait"},
    {"iata": "RUH", "name": "King Khalid International Airport", "city": "Riyadh", "state": "", "country": "Saudi Arabia"},
    {"iata": "JED", "name": "King Abdulaziz International Airport", "city": "Jeddah", "state": "", "country": "Saudi Arabia"},

    # Southeast Asia & East Asia
    {"iata": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "state": "", "country": "Singapore"},
    {"iata": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "state": "", "country": "Malaysia"},
    {"iata": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "state": "", "country": "Thailand"},
    {"iata": "DMK", "name": "Don Mueang International Airport", "city": "Bangkok", "state": "", "country": "Thailand"},
    {"iata": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "state": "", "country": "Hong Kong"},
    {"iata": "NRT", "name": "Narita International Airport", "city": "Tokyo", "state": "", "country": "Japan"},
    {"iata": "HND", "name": "Haneda Airport", "city": "Tokyo", "state": "", "country": "Japan"},
    {"iata": "ICN", "name": "Incheon International Airport", "city": "Seoul", "state": "", "country": "South Korea"},
    {"iata": "CGK", "name": "Soekarno-Hatta International Airport", "city": "Jakarta", "state": "", "country": "Indonesia"},
    {"iata": "DPS", "name": "Ngurah Rai International Airport", "city": "Bali", "state": "", "country": "Indonesia"},
    {"iata": "MLE", "name": "Velana International Airport", "city": "Male", "state": "", "country": "Maldives"},
    {"iata": "CMB", "name": "Bandaranaike International Airport", "city": "Colombo", "state": "", "country": "Sri Lanka"},

    # Europe
    {"iata": "LHR", "name": "Heathrow Airport", "city": "London", "state": "", "country": "United Kingdom"},
    {"iata": "LGW", "name": "Gatwick Airport", "city": "London", "state": "", "country": "United Kingdom"},
    {"iata": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "state": "", "country": "France"},
    {"iata": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "state": "", "country": "Germany"},
    {"iata": "MUC", "name": "Munich Airport", "city": "Munich", "state": "", "country": "Germany"},
    {"iata": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "state": "", "country": "Netherlands"},
    {"iata": "IST", "name": "Istanbul Airport", "city": "Istanbul", "state": "", "country": "Turkey"},
    {"iata": "FCO", "name": "Leonardo da Vinci–Fiumicino Airport", "city": "Rome", "state": "", "country": "Italy"},
    {"iata": "MAD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "state": "", "country": "Spain"},
    {"iata": "BCN", "name": "Josep Tarradellas Barcelona-El Prat Airport", "city": "Barcelona", "state": "", "country": "Spain"},
    {"iata": "ZRH", "name": "Zurich Airport", "city": "Zurich", "state": "", "country": "Switzerland"},

    # North America
    {"iata": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "state": "New York", "country": "United States"},
    {"iata": "EWR", "name": "Newark Liberty International Airport", "city": "New York", "state": "New Jersey", "country": "United States"},
    {"iata": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "state": "California", "country": "United States"},
    {"iata": "SFO", "name": "San Francisco International Airport", "city": "San Francisco", "state": "California", "country": "United States"},
    {"iata": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "state": "Illinois", "country": "United States"},
    {"iata": "DFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "state": "Texas", "country": "United States"},
    {"iata": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "state": "Georgia", "country": "United States"},
    {"iata": "SEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "state": "Washington", "country": "United States"},
    {"iata": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "state": "Ontario", "country": "Canada"},
    {"iata": "YVR", "name": "Vancouver International Airport", "city": "Vancouver", "state": "British Columbia", "country": "Canada"},

    # Australia & Oceania
    {"iata": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "state": "New South Wales", "country": "Australia"},
    {"iata": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "state": "Victoria", "country": "Australia"},
]

# Fast lookup map by IATA code
IATA_MAP: Dict[str, Dict[str, str]] = {item["iata"].upper(): item for item in AIRPORTS_DB}

# Synonyms and alternative spellings
CITY_SYNONYMS: Dict[str, str] = {
    "cochin": "COK",
    "kochi": "COK",
    "nedumbassery": "COK",
    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",
    "calicut": "CCJ",
    "kozhikode": "CCJ",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "bombay": "BOM",
    "chennai": "MAA",
    "madras": "MAA",
    "calcutta": "CCU",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "goa": "GOI",
    "ahmedabad": "AMD",
    "pune": "PNQ",
    "dubai": "DXB",
    "london": "LHR",
    "new york": "JFK",
    "nyc": "JFK",
    "singapore": "SIN",
    "paris": "CDG",
    "tokyo": "HND",
    "bangkok": "BKK",
    "san francisco": "SFO",
    "los angeles": "LAX",
    "sydney": "SYD",
    "toronto": "YYZ"
}


def lookup_iata(query: str) -> Optional[str]:
    """
    Resolve a city name, airport name, or airport code to a 3-letter IATA code.
    Returns uppercase 3-letter IATA code or None.
    """
    if not query:
        return None

    cleaned = query.strip()

    # Exact 3-letter code match
    if len(cleaned) == 3 and cleaned.upper() in IATA_MAP:
        return cleaned.upper()

    # If already a valid 3-letter code format
    if re.match(r"^[A-Za-z]{3}$", cleaned) and cleaned.upper() in IATA_MAP:
        return cleaned.upper()

    normalized = cleaned.lower()

    # Direct synonym match
    if normalized in CITY_SYNONYMS:
        return CITY_SYNONYMS[normalized]

    # Partial city or name search
    for item in AIRPORTS_DB:
        if normalized == item["city"].lower():
            return item["iata"]

    for item in AIRPORTS_DB:
        if normalized in item["city"].lower() or normalized in item["name"].lower():
            return item["iata"]

    # If it is a 3-letter uppercase code not in our DB, return it anyway as valid IATA candidate
    if re.match(r"^[A-Za-z]{3}$", cleaned):
        return cleaned.upper()

    return None


def get_airport_info(iata: str) -> Optional[Dict[str, str]]:
    """Retrieve detailed airport info by IATA code."""
    if not iata:
        return None
    code = iata.strip().upper()
    if code in IATA_MAP:
        return IATA_MAP[code]
    return {
        "iata": code,
        "name": f"Airport ({code})",
        "city": code,
        "state": "",
        "country": "International"
    }


def search_airports(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """Search airports by keyword (IATA code, city name, or airport name)."""
    if not query:
        return AIRPORTS_DB[:limit]

    q = query.strip().lower()
    matches = []

    # Priority 1: Exact IATA match
    for item in AIRPORTS_DB:
        if item["iata"].lower() == q:
            matches.append(item)

    # Priority 2: City starts with query
    for item in AIRPORTS_DB:
        if item not in matches and item["city"].lower().startswith(q):
            matches.append(item)

    # Priority 3: City or Name contains query
    for item in AIRPORTS_DB:
        if item not in matches and (q in item["city"].lower() or q in item["name"].lower() or q in item["country"].lower()):
            matches.append(item)

    return matches[:limit]
