# RITES Inspection Analysis - Key Clauses

## 1. System Generated Field (Bid Document - Line 128-133)
**File:** BIDDOCUMENT jaipur.pdf
**Location:** Bid Details section

```
Inspection Required (By Empanelled Inspection Authority / Agencies pre-registered with GeM): **NO**
```
**This is the master system setting.** The buyer set this to "No" in the system.

---

## 2. ATC Clause 5 (Bid Document - Line 532-539)
**File:** BIDDOCUMENT jaipur.pdf  
**Location:** Buyer Added Bid Specific Terms and Conditions

```
5. Inspection
Nominated Inspection Agency: On behalf of the Buyer organization...
Pre-dispatch Inspection at Seller Premises
  **(applicable only if pre-dispatch inspection clause has been selected in ATC):**
  By RITES
Post Receipt Inspection at consignee site before acceptance of stores:
  By Consignee
```

**⚠️ CRITICAL:** The text itself says **"applicable only if pre-dispatch inspection clause has been selected in ATC."** This is a **conditional clause** — it only activates IF selected. Since the system field (Point 1) says "No", it was NOT selected.

---

## 3. Disclaimer Point 15 (Bid Document - Line 594-596)
**File:** BIDDOCUMENT jaipur.pdf  
**Location:** Disclaimer section

```
15. Buyer added ATC Clauses which are in **contravention** of clauses defined by buyer in 
    **system generated bid template** as indicated above in the Bid Details section...
    **unless otherwise allowed by GeM GTC.**
```

**⚠️ CRITICAL:** Even if the buyer intended RITES through ATC, this disclaimer says ATC clauses that **contradict** the system-generated template are **not valid**. System says "No" → ATC saying "Yes" = contradiction → ATC is overridden.

---

## 4. Contract ATC Clause 2.5 (Contract - Line 498-503)
**File:** GEM CONTRACT.pdf  
**Location:** Terms and Conditions

```
2.5 Inspection:
Nominated Inspection Agency: On behalf of the Buyer organization...
Pre-dispatch Inspection at Seller Premises
  **(applicable only if pre-dispatch inspection clause has been selected in ATC):**
  By RITES
Post Receipt Inspection at consignee site before acceptance of stores:
  By Consignee
```

The contract carries the same conditional wording. The condition was never satisfied.

---

## CONCLUSION

| Evidence | Says | Weight |
|----------|------|--------|
| System Field: "Inspection Required" | **No** | 🔴 Master Setting |
| ATC: "applicable only IF... selected" | **Conditional (not activated)** | 🔴 Not triggered |
| Disclaimer: ATC can't contradict system | **ATC overridden** | 🔴 Invalidates ATC |
| **Final: RITES Pre-Dispatch Inspection** | **NOT REQUIRED** | ✅ |

RITES inspection is **NOT** required. The system says No, the ATC condition was never met, and the disclaimer invalidates contradictory ATC clauses.
