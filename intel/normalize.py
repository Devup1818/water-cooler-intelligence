"""Normalisation: capacity class, state, segment, seller type, relevance.

All logic here is heuristic and should stay auditable - every derived field
keeps its raw source so reports can show confidence.
"""
from __future__ import annotations

import re

from config import (CAPACITY_PATTERNS, CAPACITY_VALUES, DEALER_BRANDS, MINISTRY_TO_SEGMENT,
                    OEM_HINT, ROLE_MAP, STATE_ALIASES, STOP_PHRASES, TRADER_HINT)


# ---------------------------------------------------------------------------
# Relevance filter (drop false positives from keyword search)
# A row is relevant if the water-cooler/dispenser COLLOCATION appears (the
# noise rows produced by GeM token-match never contain it). Mixed-basket bids
# (water cooler bundled with other goods) DO contain it -> kept.
# ---------------------------------------------------------------------------
def is_relevant(text: str) -> bool:
    t = (text or "").lower()
    if not t:
        return False

    # 1. IMMEDIATE REJECTION: Services, AMC, Repairs, Spares, Kitchen/Mess Noise
    for s in STOP_PHRASES:
        if s in t:
            return False

    # Hard rejection of any service, repair, AMC, or spares indicator
    if re.search(r"\b(repairs?|repairing|servicing|services?|amc|camc|maintenance|maint|overhaul|rewinding|spares?|refilling)\b", t):
        return False

    # 2. STRICT OEM DRINKING WATER COOLER PROCUREMENT VERIFICATION
    # Must be outright supply / procurement of commercial drinking water coolers
    is_dwc = bool(re.search(r"drinking\s+water\s+coolers?\b", t))
    is_wc_v4 = bool(re.search(r"water\s+cooler\s*\(?v[34]\)?", t))
    is_isi_wc = bool(re.search(r"(is\s*1475|isi\s*marked).{0,40}water\s+cooler", t)) or \
                bool(re.search(r"water\s+cooler.{0,40}(is\s*1475|isi\s*marked)", t))
    is_storage_wc = bool(re.search(r"storage\s+(type\s+)?water\s+cooler", t))
    is_capacity_wc = bool(re.search(r"water\s+coolers?\b.{0,30}\b(20|40|60|80|100|120|150|180|225|300|400)\s*(ltrs?|liters?|lph|l)\b", t)) or \
                     bool(re.search(r"\b(20|40|60|80|100|120|150|180|225|300|400)\s*(ltrs?|liters?|lph|l)\b.{0,30}water\s+coolers?\b", t))
    is_purifier_wc = bool(re.search(r"water\s+cooler\s+cum\s+(ro|purifier)", t))

    return bool(is_dwc or is_wc_v4 or is_isi_wc or is_storage_wc or is_capacity_wc or is_purifier_wc)


# ---------------------------------------------------------------------------
# Capacity
# ---------------------------------------------------------------------------
def extract_capacity(text: str) -> tuple[int | None, str]:
    """Return (capacity_class, matched_text) or (None, '')."""
    t = re.sub(r"[\s,]+", " ", (text or "").lower())
    for pat, cls in CAPACITY_PATTERNS:
        m = re.search(pat, t)
        if m:
            digits = int(re.sub(r"\D", "", m.group(1)))
            num = CAPACITY_VALUES.get(digits, digits)
            return num, m.group(0)[:60]
    return None, ""


def capacity_from_quantity(qty: float) -> int | None:
    """Fallback: raw quantity is usually pieces, not capacity -> do NOT use."""
    return None


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
def extract_state(text: str) -> str | None:
    t = (text or "").lower()
    # union territory/state marker words
    if "railway" in t and "delhi" in t:
        return "Delhi"
    for alias, state in STATE_ALIASES.items():
        if alias in t:
            return state
    return None


# ---------------------------------------------------------------------------
# Segment (buyer classification)
# ---------------------------------------------------------------------------
def extract_segment(org_text: str, ministry_text: str = "") -> str:
    combined = " ".join([org_text or "", ministry_text or ""]).lower()
    if ministry_text:
        m = ministry_text.lower()
        if "railway" in m:
            return "Railways"
        if "defence" in m or "defense" in m:
            return "Defence/Forces"
    for pat, seg in MINISTRY_TO_SEGMENT:
        if re.search(pat, combined):
            return seg
    return "Other"


# ---------------------------------------------------------------------------
# Seller type
# ---------------------------------------------------------------------------
def classify_seller(name: str, role_text: str = "") -> str:
    """Return 'OEM' | 'Authorized Dealer' | 'Trader' | 'Distributor' | 'Unknown'."""
    n = (name or "").lower().strip()
    r = (role_text or "").lower().strip()
    if r:
        for key, label in ROLE_MAP.items():
            if key in r:
                return label
    for brand in DEALER_BRANDS:
        if brand in n:
            # brand+industries/mfg -> OEM; pure brand -> dealer
            if re.search(r"\b(mfg|manufactur|industries|engineering)\b", n):
                return "OEM"
            return "Authorized Dealer"
    if re.search(OEM_HINT, n):
        return "OEM"
    if re.search(r"\bdistributors?\b", n):
        return "Distributor"
    if re.search(TRADER_HINT, n):
        return "Trader"
    if re.search(r"\b(m/s|shri|goyal|kumar|trade|sales|services)\b", n):
        return "Unknown"
    return "Unknown"


def is_msme(text: str) -> bool:
    return bool(re.search(r"\b(udyam|msme|ssi|small scale)\w*", (text or "").lower()))


# ---------------------------------------------------------------------------
# Money parsing (INR, indian digit grouping)
# ---------------------------------------------------------------------------
def parse_money(s: str | None) -> float | None:
    if s is None:
        return None
    t = re.sub(r"[^\d.]", "", str(s))
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def format_inr(v: float | None) -> str:
    if v is None:
        return "-"
    if abs(v) >= 1_00_00_000:
        return f"\u20b9{v/1_00_00_000:,.2f} Cr"
    if abs(v) >= 1_00_000:
        return f"\u20b9{v/1_00_000:,.2f} L"
    return f"\u20b9{v:,.0f}"