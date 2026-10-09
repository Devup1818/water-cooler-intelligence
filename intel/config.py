"""Domain configuration for the Water Cooler Govt Tender Intelligence pipeline.

All India, water coolers (storage / bulk / drinking), capacities 40-300 L.
Tuned for Fresco Casa (Cool Home India) market intelligence.
"""

# ---------------------------------------------------------------------------
# 1. SEARCH KEYWORDS (GeM bidplus full-text + CPPP title search)
#    Add regional / category synonyms over time.
# ---------------------------------------------------------------------------
GEM_KEYWORDS = [
    # High-precision category queries for IS 1475:2001 Drinking Water Coolers only
    "Drinking Water Coolers",
    "Drinking Water Coolers V4",
    "Water Cooler V4",
    "Water Cooler V3",
    "Coolers ISI Marked",
    "Water Cooler cum Purifier",
]

# Keys actually used in a normal run.
def default_gem_keywords() -> list[str]:
    return [k for k in GEM_KEYWORDS if k != "water cooler"]
DEFAULT_GEM_KEYWORDS = default_gem_keywords()

# STRICT STOP PHRASES:
# Instantly drop non-OEM procurement, repair/AMC services, engine parts, and unrelated appliances.
STOP_PHRASES = [
    # Services / AMC / Repair / Maintenance (Cool Home is an OEM manufacturer, NOT an appliance repair vendor)
    "repair",
    "repairs",
    "repairing",
    "servicing",
    "service of",
    "services for",
    "annual maintenance",
    "maintenance of",
    "amc",
    "camc",
    "overhaul",
    "rewinding",
    "restoration of",
    "gas charging",
    "custom bid for services",
    "spare parts",
    "spares",

    # Kitchen & Army Mess Appliances (eliminates mixed mess repair tenders)
    "chapati",
    "hamam",
    "generator",
    "dg set",
    "bush cutter",
    "kneading machine",
    "microwave",
    "washing machine",
    "led tv",
    "lcd",
    "television",
    "gas stove",
    "bhatti",
    "weighing machine",
    "deep freezer",
    "food warmer",

    # Automotive & Engine Coolers
    "engine oil cooler",
    "lube oil cooler",
    "jacket water cooler",
    "waste water cooler",
    "engine cooling water",
    "water cooled condenser",
    "water cooled chiller",
    "o ring eng oil cooler",
    "head lamp",
    "bearing tapered",
    "gasket cylinder",

    # Non-IS 1475 Coolers
    "desert cooler",
    "air cooler",
    "room cooler",
    "water camper",
    "water cooler box",
    "cooler box",
    "cooler bag",
]

# ---------------------------------------------------------------------------
# 2. CAPACITY EXTRACTION
#    Water cooler sizes in THIS industry are named by number (40/60/80/120/
#    150/180/225/300) which usually means *cooling capacity* in LPH or
#    *storage capacity* in litres. We normalise to a nominal "L class"
#    so market analysis can bucket them.
# ---------------------------------------------------------------------------
CAPACITY_CLASSES = [300, 225, 180, 150, 120, 100, 80, 60, 45, 40, 30, 20, 10, 5]

# Regexes run against the full (title + category + description) text, in order.
# First match wins. `key` is a friendly bucket used in reports.
CAPACITY_PATTERNS = [
    (r"\b(3\d\d)\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour|liter\s*/?\s*hour|cooling\s*capacity)\b", "300"),
    (r"\b30\d\s*l\b", "300"),
    (r"\b(2\d\d)\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "225"),
    (r"\b(1[89]\d)\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour|cooling)\b", "180"),
    (r"\b1[45]\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour|cooling|cape)\b", "150"),
    (r"\b1[23]\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "120"),
    (r"\b100\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "100"),
    (r"\b8\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "80"),
    (r"\b6\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "60"),
    (r"\b4\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "40"),
    (r"\b3\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "30"),
    (r"\b2\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "20"),
    (r"\b1\d\s*(?:lph|l/h|l/hr|litres?\s*per\s*hour)\b", "15"),
]

# Capacity value, in litres (assumed LPH) used for unit economics.
CAPACITY_VALUES = {5: 5, 10: 10, 15: 15, 20: 20, 30: 30, 40: 40, 45: 45, 60: 60,
                   80: 80, 100: 100, 120: 120, 150: 150, 180: 180, 225: 225, 300: 300}

# ---------------------------------------------------------------------------
# 3. GEO / STATE CLASSIFICATION
#    From buyer organisation name, department, ministry, consignee city.
# ---------------------------------------------------------------------------
STATE_ALIASES = {
    "delhi": "Delhi", "new delhi": "Delhi", "nct of delhi": "Delhi",
    "maharashtra": "Maharashtra", "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "karnataka": "Karnataka", "bengaluru": "Karnataka", "bangalore": "Karnataka",
    "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "chennai": "Tamil Nadu",
    "telangana": "Telangana", "hyderabad": "Telangana",
    "andhra pradesh": "Andhra Pradesh", "visakhapatnam": "Andhra Pradesh",
    "uttar pradesh": "Uttar Pradesh", "up ": "Uttar Pradesh", "lucknow": "Uttar Pradesh",
    "rajasthan": "Rajasthan", "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "ajmer": "Rajasthan", "bikaner": "Rajasthan",
    "haryana": "Haryana", "gurugram": "Haryana", "gurgaon": "Haryana",
    "punjab": "Punjab", "chandigarh": "Chandigarh", "ludhiana": "Punjab", "amritsar": "Punjab",
    "gujarat": "Gujarat", "ahmedabad": "Gujarat", "surat": "Gujarat",
    "madhya pradesh": "Madhya Pradesh", "bhopal": "Madhya Pradesh", "indore": "Madhya Pradesh",
    "west bengal": "West Bengal", "kolkata": "West Bengal",
    "bihar": "Bihar", "patna": "Bihar",
    "odisha": "Odisha", "orissa": "Odisha", "bhubaneswar": "Odisha",
    "assam": "Assam", "guwahati": "Assam",
    "jharkhand": "Jharkhand", "ranchi": "Jharkhand",
    "chhattisgarh": "Chhattisgarh", "raipur": "Chhattisgarh",
    "kerala": "Kerala", "kochi": "Kerala", "trivandrum": "Kerala",
    "jammu": "Jammu & Kashmir", "kashmir": "Jammu & Kashmir", "srinagar": "Jammu & Kashmir",
    "himachal pradesh": "Himachal Pradesh", "shimla": "Himachal Pradesh",
    "uttarakhand": "Uttarakhand", "dehradun": "Uttarakhand",
    "goa": "Goa", "panaji": "Goa",
    "manipur": "Manipur", "meghalaya": "Meghalaya", "mizoram": "Mizoram",
    "nagaland": "Nagaland", "tripura": "Tripura", "sikkim": "Sikkim",
    "andaman": "Andaman & Nicobar", "puducherry": "Puducherry", "ladakh": "Ladakh",
}

# ---------------------------------------------------------------------------
# 4. MINISTRY can be read directly from GeM (`ba_official_details_minName`).
#    These patterns are used only as a fallback when it is missing AND to
#    build the buyer "segment" column.
# ---------------------------------------------------------------------------
MINISTRY_TO_SEGMENT = [
    (r"railway", "Railways"),
    (r"defence|defense|army|navy|air force|ordinance|DRDO|BSF|CRPF|ITBP|paramilitary", "Defence/Forces"),
    (r"power|electricity|generation|transmission|distribution", "Power"),
    (r"health|medical|hospital|ayush|pharma|hosp", "Health"),
    (r"education|university|school|iit|nit|college|ignou", "Education"),
    (r"home|police|prison|fire", "Home/Police"),
    (r"rural|panchayat|municipal|corporation|urban|development authority", "Urban/Rural Development"),
    (r"water|irrigation|jal|sewage|drainage", "Water/WSB"),
    (r"transport|road|nhai|airport|metro|rail", "Transport"),
    (r"agriculture|horticulture|fisher|dairy|animal", "Agriculture"),
    (r"petroleum|oil|gas|refinery|ongc", "Petroleum"),
    (r"steel|mines|coal|mineral", "Mines/Steel/Coal"),
    (r"telecom|doT|broadband|nic|electronics|it\b", "IT/Telecom"),
    (r"finance|bank|insurance|revenue|custom|gst|income", "Finance"),
    (r"food|civil supply|fci", "Food/Civil Supplies"),
    (r"rail|metro", "Transport"),
]

# ---------------------------------------------------------------------------
# 5. OEM vs DEALER vs TRADER classification
#    Applied against winner / seller names in the award log.
#    Heuristic only - override in the awards CSV column "winner_type" if known.
# ---------------------------------------------------------------------------
OEM_HINT = r"\b(mfg|manufactur|industries|enterprises? |engineering|fabricat|produc|auto.?clave|electrics?|refrigerat)\b"
TRADER_HINT = r"\b(traders?|trading|suppliers?|supply|agency|agencies|distribut|stockist|enterprise)\b"
DEALER_BRANDS = ["voltas", "blue star", "hitachi", "lloyd", "daikin", "kent", "eureka forbes",
                 "aquaguard", "fresco casa", "cool home", "cool care", "icecool", "snowman",
                 "water king", "aqua fresh", "life cool", "cold point", "supreme", "amaze"]

# GeM seller-role hint: documents say "Selling As: OEM / Authorized Dealer / Trader"
ROLE_MAP = {"oem": "OEM", "manufacturer": "OEM", "authorized dealer": "Authorized Dealer",
            "authorised dealer": "Authorized Dealer", "dealer": "Authorized Dealer",
            "trader": "Trader", "distributor": "Distributor", "reseller": "Trader"}

# ---------------------------------------------------------------------------
# 6. RATE ANOMALY GUARD (rupees per unit sanity band by capacity class)
#    Used to flag implausible unit prices in the award log.
# ---------------------------------------------------------------------------
RATE_BANDS = {
    40: (15000, 60000), 60: (18000, 75000), 80: (22000, 90000),
    100: (25000, 105000), 120: (28000, 120000), 150: (32000, 140000),
    180: (38000, 160000), 225: (45000, 200000), 300: (55000, 260000),
}

# ---------------------------------------------------------------------------
# 7b. PORTAL REGISTRY (Full India sweep)
#     Every government tender source we monitor. `engine` selects the scraper
#     adaptor in the `portals/` package; `verified`=True only after a live run
#     has produced rows on THIS machine (corporate proxy may differ).
#
#     engine families:
#       drupal     - e-procure Drupal fork (CPPP + most states). Form search is
#                    CAPTCHA-gated; falls back to public listing pages.
#       nprocure   - Gujarat nprocure.com (IIS/ASP.NET engine).
#       generic    - any portal with a public tenders listing we can page
#                    through; rows keyword-filtered locally.
#       health     - medical supplies corporations / hospital bodies (mostly
#                    own sites or GeM; some publish on nprocure/drupal).
# ---------------------------------------------------------------------------
PORTAL_ENGINES = ("drupal", "nprocure", "generic", "health", "bihar", "telangana")

PORTALS = [
    # -- central -----------------------------------------------------------
    {"code": "cppp", "name": "CPPP (Central Public Procurement)", "state": "ALL",
     "engine": "drupal", "type": "central", "base": "https://eprocure.gov.in",
     "search": "https://eprocure.gov.in/cppp/tendersearch", "captcha": True, "verified": True},
    {"code": "gem", "name": "GeM (Government e-Marketplace)", "state": "ALL",
     "engine": "gem", "type": "central", "base": "https://bidplus.gem.gov.in",
     "captcha": False, "verified": True},

    # -- state e-procure (mostly Drupal eprocure forks) ---------------------
    {"code": "up", "name": "UP eTenders", "state": "Uttar Pradesh", "engine": "drupal",
     "type": "state", "base": "https://etender.up.nic.in", "captcha": True, "verified": True},
    {"code": "mh", "name": "Maharashtra e-Procurement (MahaTenders)", "state": "Maharashtra",
     "engine": "drupal", "type": "state", "base": "https://mahatenders.gov.in", "captcha": True, "verified": True},
    {"code": "rj", "name": "Rajasthan eProc", "state": "Rajasthan", "engine": "drupal",
     "type": "state", "base": "https://eproc.rajasthan.gov.in", "captcha": True, "verified": True},
    {"code": "mp", "name": "MP Tenders (MPTenders)", "state": "Madhya Pradesh", "engine": "drupal",
     "type": "state", "base": "https://mptenders.gov.in", "captcha": True, "verified": True},
    {"code": "ka", "name": "Karnataka KPPP", "state": "Karnataka", "engine": "drupal",
     "type": "state", "base": "https://kppp.karnataka.gov.in", "captcha": True, "verified": False},
    {"code": "tn", "name": "TN Tenders (TNTENDERS)", "state": "Tamil Nadu", "engine": "drupal",
     "type": "state", "base": "https://tntenders.gov.in", "captcha": True, "verified": True},
    {"code": "wb", "name": "West Bengal Tenders (WBENDERS)", "state": "West Bengal", "engine": "drupal",
     "type": "state", "base": "https://wbtenders.gov.in", "captcha": True, "verified": True},
    {"code": "kl", "name": "Kerala eTenders", "state": "Kerala", "engine": "drupal",
     "type": "state", "base": "https://etenders.kerala.gov.in", "captcha": True, "verified": True},
    {"code": "od", "name": "Odisha Tenders", "state": "Odisha", "engine": "drupal",
     "type": "state", "base": "https://tendersodisha.gov.in", "captcha": True, "verified": True},
    {"code": "br", "name": "Bihar eProcurement (eproc2)", "state": "Bihar", "engine": "bihar",
     "type": "state", "base": "https://eproc2.bihar.gov.in", "captcha": True, "verified": True},
    {"code": "jh", "name": "Jharkhand Tenders", "state": "Jharkhand", "engine": "drupal",
     "type": "state", "base": "https://jharkhandtenders.gov.in", "captcha": True, "verified": True},
    {"code": "cg", "name": "Chhattisgarh eTenders", "state": "Chhattisgarh", "engine": "drupal",
     "type": "state", "base": "https://etenders.cgstate.gov.in", "captcha": True, "verified": False},
    {"code": "ts", "name": "Telangana eProcurement", "state": "Telangana", "engine": "telangana",
     "type": "state", "base": "https://tender.telangana.gov.in", "captcha": True, "verified": True},
    {"code": "ap", "name": "Andhra Pradesh eProcurement", "state": "Andhra Pradesh", "engine": "drupal",
     "type": "state", "base": "https://etenders.ap.gov.in", "captcha": True, "verified": False},
    {"code": "hr", "name": "Haryana eTenders", "state": "Haryana", "engine": "drupal",
     "type": "state", "base": "https://etenders.hry.nic.in", "captcha": True, "verified": True},
    {"code": "pb", "name": "Punjab eProcurement", "state": "Punjab", "engine": "drupal",
     "type": "state", "base": "https://eproc.punjab.gov.in", "captcha": True, "verified": True},
    {"code": "assam", "name": "Assam eProcurement", "state": "Assam", "engine": "drupal",
     "type": "state", "base": "https://assamtenders.gov.in", "captcha": True, "verified": True},
    {"code": "hp", "name": "Himachal Pradesh eTenders", "state": "Himachal Pradesh", "engine": "generic",
     "type": "state", "base": "https://hptenders.gov.in", "captcha": True, "verified": True},
    {"code": "uk", "name": "Uttarakhand Tenders", "state": "Uttarakhand", "engine": "generic",
     "type": "state", "base": "https://uktenders.gov.in", "captcha": True, "verified": True},
    {"code": "jk", "name": "J&K eProcurement", "state": "Jammu & Kashmir", "engine": "generic",
     "type": "state", "base": "https://jktenders.gov.in", "captcha": True, "verified": True},
    {"code": "dl", "name": "Delhi eTenders (NCT)", "state": "Delhi", "engine": "drupal",
     "type": "state", "base": "https://govtprocurement.delhi.gov.in", "captcha": True, "verified": True},
    {"code": "ga", "name": "Goa Tenders", "state": "Goa", "engine": "generic",
     "type": "state", "base": "https://goatenders.gov.in", "captcha": True, "verified": False},
    {"code": "gjm", "name": "Gujarat nprocure", "state": "Gujarat", "engine": "nprocure",
     "type": "state", "base": "https://tender.nprocure.com", "captcha": False, "verified": False},

    # -- health / medical supplies corps -------------------------------------
    {"code": "tnmsc", "name": "TNMSC (Tamil Nadu Medical Services Corp)", "state": "Tamil Nadu",
     "engine": "health", "type": "health", "base": "https://www.tnmsc.com", "captcha": False, "verified": False},
    {"code": "kms", "name": "Karnataka Medical Supplies Corps", "state": "Karnataka",
     "engine": "health", "type": "health", "base": "https://kms.karnataka.gov.in", "captcha": False, "verified": False},
    {"code": "hmscl", "name": "Haryana Medical Services Corps", "state": "Haryana",
     "engine": "health", "type": "health", "base": "https://hmscl.org.in", "captcha": False, "verified": False},
    {"code": "mpmscl", "name": "MP Medical Supplies (MPMSME)", "state": "Madhya Pradesh",
     "engine": "health", "type": "health", "base": "https://mprmsc.mp.gov.in", "captcha": False, "verified": False},
    {"code": "esic", "name": "ESIC (employee health) procurement", "state": "ALL",
     "engine": "generic", "type": "health", "base": "https://www.esic.gov.in", "captcha": True, "verified": False},
]

# Short human label for the report's portal column.
def portal_label(code: str) -> str:
    for p in PORTALS:
        if p["code"] == code:
            return p["name"]
    return code

# Keywords sent to third-party portals. State e-procure titles are plainer
# than GeM category names, so use simple case-insensitive terms; local
# `base_filter` keeps it tight, and is_relevant() re-filters anyway.
PORTAL_KEYWORDS = ["Water Cooler", "Water Coolers", "Drinking Water Cooler",
                   "Drinking Water Coolers", "Water Dispenser", "Water Dispensers",
                   "Water Cooler cum Purifier", "Bulk Water Dispenser"]

# Default engine buckets for `run.py scrape-portal --all`
def portals_for(type_: str | None = None, engine: str | None = None) -> list[dict]:
    ps = PORTALS
    if type_:
        ps = [p for p in ps if p.get("type") == type_]
    if engine:
        ps = [p for p in ps if p.get("engine") == engine]
    return ps

def portals_of_state(state: str | None = None) -> list[dict]:
    if not state or state == "ALL":
        return [p for p in PORTALS if p.get("type") != "state"]
    return [p for p in PORTALS if p.get("state") == state and p.get("type") == "state"]

# ---------------------------------------------------------------------------
# 8. PIPES
# ---------------------------------------------------------------------------
DB_PATH = "data/intel.db"
AUTHORIZED_THROUGHPUT = 0.8  # max HTTP hits per second per source (be nice)
REQUEST_TIMEOUT = 40
HTTP_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                   "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}