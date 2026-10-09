# COMPRESSOR WATTAGE CALCULATION GUIDE
## How to Determine Required Wattage for 150 L/hr Cooling Capacity

---

## 1. THE BASIC PHYSICS

### Cooling Capacity Formula (Heat Transfer)

**Q = m × Cp × ΔT**

Where:
- **Q** = Cooling Capacity (kW) - Heat removed from water
- **m** = Mass flow rate (kg/s) - Water flow rate
- **Cp** = Specific heat capacity of water (4.187 kJ/kg·K)
- **ΔT** = Temperature difference (°C) - Water temperature drop

---

## 2. CALCULATION FOR 150 L/hr WATER COOLER

### Step 1: Water Flow Rate

**Given:**
- Cooling Capacity Rating: 150 L/hr
- Convert to kg/s: 150 L/hr ÷ 3600 sec/hr = 0.0417 L/s
- Since water density ≈ 1 kg/L: **m = 0.0417 kg/s**

### Step 2: Temperature Difference (IS 1475 Test Conditions)

**From IS 1475 Clause 5.2:**
- Ambient temperature: 35°C
- Inlet water temperature: 30°C
- Maximum outlet water temperature: 13.5°C

**ΔT = 30°C - 13.5°C = 16.5°C**

### Step 3: Calculate Cooling Capacity (Heat Load)

**Q = m × Cp × ΔT**
**Q = 0.0417 kg/s × 4.187 kJ/kg·K × 16.5 K**
**Q = 2.89 kW**

**This is the heat that must be removed from water to cool 150 L/hr from 30°C to 13.5°C**

---

## 3. COMPRESSOR POWER CALCULATION

### The COP Relationship

**COP (Coefficient of Performance) = Cooling Capacity / Power Input**

**Power Input = Cooling Capacity / COP**

### Typical COP Values for Water Coolers

| Compressor Type | Typical COP | Typical EER |
|----------------|-------------|-------------|
| Reciprocating (Piston) | 1.5 - 3.5 | 5.1 - 12.0 |
| Scroll | 2.5 - 4.5 | 8.5 - 15.4 |
| Rotary | 2.0 - 3.5 | 6.8 - 12.0 |

### Power Input Calculation

**Using COP = 3.0 (typical for water cooler compressor):**

**Power Input = 2.89 kW / 3.0 = 0.963 kW = 963W**

**Using COP = 2.5 (conservative estimate):**

**Power Input = 2.89 kW / 2.5 = 1.156 kW = 1,156W**

**Using COP = 3.5 (high efficiency):**

**Power Input = 2.89 kW / 3.5 = 0.826 kW = 826W**

---

## 4. THEORETICAL MINIMUM vs IS 1475 SPECIFICATION

### Theoretical Minimum

| COP | Required Power Input |
|-----|---------------------|
| 2.0 | 1,445W |
| 2.5 | 1,156W |
| 3.0 | 963W |
| 3.5 | 826W |
| 4.0 | 723W |

**THEORETICALLY: A compressor with 800-1,200W could deliver 150 L/hr cooling capacity**

### IS 1475 Specification

**IS 1475 Clause 5.6.3:**
> "The rate of energy consumption for drinking water coolers... shall **not be more than** the values given below..."

| Size | Cooling Capacity Rating | Maximum Energy Consumption |
|------|------------------------|---------------------------|
| 8 | 150 L/hr | **1,550W** |

**IS 1475 SPECIFIES 1,550W AS THE MAXIMUM ALLOWED!**

---

## 5. WHY IS 1,550W SPECIFIED (NOT THEORETICAL MINIMUM)?

### Reason 1: Safety Margin
- Test conditions are ideal (35°C ambient, 30°C inlet)
- Real-world conditions vary (higher ambient, higher inlet temps)
- 1,550W provides buffer for adverse conditions

### Reason 2: Maximum Operating Conditions
**From IS 1475 Clause 5.3:**
- Ambient temperature: 43°C (not 35°C)
- Inlet water temperature: 35°C (not 30°C)
- Must still deliver 90% of rated capacity

### Reason 3: Energy Efficiency Standard
- 1,550W is MAXIMUM, not minimum
- Lower wattage = BETTER energy efficiency
- But must still DELIVER 150 L/hr

### Reason 4: Component Sizing
- Compressor must handle peak loads
- Condenser must reject heat efficiently
- Evaporator must maintain cooling capacity

---

## 6. THE GODREJ GE153H ANALYSIS

### GE153H Specifications

| Parameter | Value | Application |
|-----------|-------|-------------|
| Power Consumption | ~200W | Refrigerator |
| Refrigerant | R134A | Refrigerator |
| Application | Single door fridge (180-210L) | NOT water cooler |
| Type | LBP (Low Back Pressure) | Refrigerator |

### Can 200W Deliver 150 L/hr?

**Theoretical Calculation:**
- If COP = 3.0: 200W × 3.0 = 600W cooling capacity
- Required: 2,890W cooling capacity (for 150 L/hr)
- **Gap: 2,890W - 600W = 2,290W SHORT!**

**Physics Reality:**
- 200W compressor can deliver ~600W cooling (at COP 3.0)
- 150 L/hr requires ~2,890W cooling
- **200W is 4.8x UNDERPOWERED for 150 L/hr**

---

## 7. COMPRESSOR WATTAGE VERIFICATION METHOD

### Method 1: Check Manufacturer Data Sheet

**Required Data:**
1. Cooling capacity at standard conditions (W or BTU/hr)
2. Power input at standard conditions (W)
3. COP or EER rating
4. Application type (refrigerator vs water cooler)

**Example from Market Data:**

| Compressor Model | Power (W) | Cooling Capacity (W) | COP | Application |
|------------------|-----------|---------------------|-----|-------------|
| Godrej GE153H | 200 | ~600 | 3.0 | Refrigerator |
| Typical 150 L/hr | 1,100-1,550 | 2,890 | 2.5-3.5 | Water Cooler |

### Method 2: Calculate from Specifications

**If you have:**
- Cooling capacity rating (L/hr)
- Temperature drop (°C)
- COP rating

**Calculate Required Power:**

**Step 1:** Calculate heat load
```
Q = (Flow Rate in L/hr ÷ 3600) × 4.187 × ΔT
Q = (150 ÷ 3600) × 4.187 × 16.5
Q = 2.89 kW
```

**Step 2:** Calculate power input
```
Power Input = Q / COP
Power Input = 2.89 / 3.0
Power Input = 0.963 kW = 963W
```

### Method 3: Check IS 1475 Table

**From IS 1475 Clause 5.6.3:**

| Cooling Capacity (L/hr) | Maximum Power (W) |
|------------------------|-------------------|
| 5 | 175 |
| 10 | 270 |
| 15 | 300 |
| 30 | 400 |
| 40 | 575 |
| 60 | 775 |
| 80 | 950 |
| 120 | 1,300 |
| **150** | **1,550** |
| 225 | 2,200 |

**For 150 L/hr: Maximum allowed = 1,550W**

---

## 8. KEY INSIGHT: WATTAGE vs APPLICATION

### The Real Issue

**It's NOT just about wattage, but APPLICATION:**

| Factor | Godrej GE153H | Required for Water Cooler |
|--------|---------------|---------------------------|
| Power | 200W | 800-1,550W |
| Application | Refrigerator | Water Cooler |
| Design | LBP (Low Back Pressure) | HBP (High Back Pressure) |
| Duty Cycle | Intermittent | Continuous |
| Cooling Load | 200-300L fridge | 150 L/hr continuous |

### Why Application Matters

1. **Duty Cycle:** Refrigerators cycle on/off; water coolers run continuously
2. **Heat Load:** Water cooler has higher heat load (continuous flow)
3. **Condenser Design:** Water cooler needs larger condenser
4. **Evaporator Design:** Water cooler needs different evaporator

---

## 9. PRACTICAL VERIFICATION STEPS

### Step 1: Request Data Sheet from OEM

**Ask for:**
1. Compressor model and specifications
2. Cooling capacity at standard conditions
3. Power input at standard conditions
4. COP/EER rating
5. Application type (refrigerator vs water cooler)

### Step 2: Verify Cooling Capacity Test

**Request test report showing:**
1. Test conditions (ambient, inlet, outlet temps)
2. Measured cooling capacity (L/hr)
3. Measured power input (W)
4. Calculated COP

### Step 3: Check ISI Mark Validity

**Verify:**
1. BIS license number
2. Product covered under license
3. Validity period

### Step 4: Compare with IS 1475

**Check if:**
1. Cooling capacity meets 150 L/hr
2. Power input ≤ 1,550W
3. Test conditions per IS 1475 Clause 5.2

---

## 10. SUMMARY

### Theoretical Minimum for 150 L/hr

| COP | Minimum Power Required |
|-----|----------------------|
| 2.5 | 1,156W |
| 3.0 | 963W |
| 3.5 | 826W |

### IS 1475 Maximum Allowed

**1,550W for 150 L/hr**

### Godrej GE153H Reality

**200W = 4.8x UNDERPOWERED for 150 L/hr**

### Key Takeaway

**The issue is NOT that 200W < 1,550W (which is actually BETTER)**
**The issue is that 200W CANNOT DELIVER 150 L/hr cooling capacity**

---

## 11. QUESTIONS FOR OEM

1. **What is the cooling capacity of GE153H at standard conditions?**
2. **Has the product been tested for 150 L/hr cooling capacity?**
3. **Is there a test report from a certified lab?**
4. **What is the COP rating of the compressor?**
5. **Is the compressor designed for water cooler applications?**

---

*This document explains how to verify compressor wattage requirements*
*July 2026*
