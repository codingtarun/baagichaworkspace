# 09 — Global DSS Research Summary

> **Why are we building this? What makes us different?**
> 
> Context for developers to understand the competitive landscape and design decisions.

---

## The Problem We're Solving

**Current state for Himalayan apple farmers:**
- No India-specific apple disease prediction system exists
- Farmers spray on calendar schedule (every 15 days) = wasteful + often too late
- Generic weather apps don't understand apple diseases
- KVKs have research data but no digital delivery mechanism
- Western DSS tools (RIMpro, WSU DAS, NEWA) don't work for India

**Result:** 25-40% post-harvest losses, ₹50,000-2,00,000/year losses per farmer from mistimed sprays.

---

## Global Competitor Analysis

### RIMpro (Netherlands) — The Scientific Gold Standard
| Aspect | Detail |
|--------|--------|
| Developer | Marc Trapman, RIMpro B.V. |
| Models | Apple scab, powdery mildew, codling moth, fruit rot |
| Approach | **Biological simulation** — models pseudothecia development, ascospore maturation |
| Output | "RIM value" = % ascospores likely to cause infection |
| Weather | YR (Norwegian Met) or Meteoblue forecasts |
| Key Feature | Fungicide depletion simulation |
| Pricing | Subscription per grower |
| **Limitations** | Complex UI, requires training, Euro-centric, **not available in India** |
| **What we learn** | Benchmark for model sophistication. We simplify RIMpro concepts for low-literacy farmers. |

### WSU Decision Aid System (DAS) — USA
| Aspect | Detail |
|--------|--------|
| Developer | Washington State University |
| Models | 10+ pests/diseases |
| Approach | Degree-day + weather threshold models |
| Weather | AgWeatherNet stations (paid) |
| Limitations | PNW-only, English-only, desktop-first |

### NEWA (Cornell) — USA Northeast
| Aspect | Detail |
|--------|--------|
| Developer | Cornell University |
| Models | 31 tools |
| Weather | 1,000+ public/private stations |
| Key Feature | **Free** for partner states |
| Limitations | Northeast USA only, requires weather station purchase |

### ADEM (UK)
| Aspect | Detail |
|--------|--------|
| Developer | NIAB EMR |
| Models | Apple scab, powdery mildew, fire blight |
| Approach | Dynamic infection efficiency model |
| Key Feature | **More accurate than Mills Table** for early detection |
| Limitations | PC-based, UK-focused, high input burden |

### The Indian Vacuum
- **NO India-specific apple DSS exists**
- Dr. YS Parmar University (Solan, HP) has:
  - Department of Plant Pathology with scab research
  - Regional stations: Sharbo, Kotkhai, Seobagh, Katrain, Bajaura
  - KVKs: Chamba, Rohru, Kinnaur, Kandaghat, Tabo
  - Apple Scab Monitoring Lab at Kotkhai

**Key research findings (Sharma & Bhandari, 1993-2015):**
- Scab highest when: rainfall >225mm + >30 rainy days + temp 15-25°C during Mar-May
- Climate change: Apple cultivation shifting from 1200-1500m → 1500-2500m → >3500m
- Warmer temps increasing pest/disease pressure

---

## Our Competitive Advantage

| Feature | Calendar Spraying | Generic Weather | RIMpro/NEWA | **Baagvaani** |
|---------|-------------------|-----------------|-------------|---------------|
| **Cost** | Free (wasteful) | Free | $$$ subscription | Free / Freemium |
| **Language** | N/A | English | English | **Hindi + English** |
| **Altitude-aware** | ❌ | ❌ | ❌ | **✅ Core feature** |
| **Block-level** | ❌ | ❌ | Some | **✅ Planned** |
| **Offline** | N/A | ❌ | ❌ | **✅ Critical** |
| **Actionable** | Vague | No | Complex graphs | **✅ Simple instructions** |
| **Made for HP** | ❌ | ❌ | ❌ | **✅ Native** |
| **Learns** | ❌ | ❌ | Static | **✅ Feedback loop** |

---

## Model Selection Rationale

### Why Revised Mills (not RIMpro)?
| Factor | RIMpro | Revised Mills |
|--------|--------|---------------|
| Data needs | Hourly rain, RH, light sensors | Temperature + estimated wetness |
| Complexity | Very high | Medium |
| Accuracy | ~90% | ~75-80% |
| Farmer hardware | Weather station required | Just a smartphone |
| Upgrade path | Never (too complex) | Yes → dynamic IE model later |

**Decision:** Start with Mills. It's proven, explainable, and works with forecast data. Upgrade after validation.

### Why Simplified Maryblyt (not CougarBlight)?
- Maryblyt developed in humid Maryland climate (similar to HP)
- CougarBlight is PNW-specific (dry, continental)
- Maryblyt is more universally applicable

### Why DMC for Powdery Mildew?
- Powdery mildew is easier to predict than scab (no rain needed)
- DMC needs only temp + RH — data we already have
- Can implement in < 1 week

---

## Validation Strategy

### Season 0: Shadow Mode (No Farmer Alerts)
- Run predictions internally
- Compare with KVK expert recommendations weekly
- Measure: false positive rate, false negative rate, timing accuracy
- **Target:** < 20% false positives, < 5% false negatives

### Season 1: Soft Launch (Beta Labels)
- Farmers see predictions labeled "BETA"
- Heavy feedback collection via app
- Weekly model tuning based on feedback
- Track: accuracy, farmer satisfaction, spray savings

### Season 2: Full Launch
- Predictions become primary recommendations
- Farmer feedback loop active
- Begin ML retraining monthly
- KVK joint publication for credibility

---

## Key Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mills/Maryblyt not validated for HP climate | HIGH | Partner with KVK, run shadow mode for 1 season |
| Weather forecast inaccurate in Himalayan valleys | MEDIUM | Use Open-Meteo + OpenWeatherMap, add farmer feedback adjustments |
| No leaf wetness sensors | MEDIUM | Estimate from RH + rain + dew point, label "estimated" |
| Farmer literacy gap | MEDIUM | Hindi UI, emoji-based severity, audio explanations |
| Government releases free app | LOW | Be first, build trust, offer superior UX + block-level precision |

---

## Sources

1. [RIMpro Cloud — Apple Scab Model](https://rimpro.cloud/wp-content/uploads/2021/09/2007-Apple-scab-a-simulation-model-for-estimating-risk-of-Venturia-Italy.pdf)
2. [WSU Decision Aid System](https://treefruit.wsu.edu/tools-resources/wsu-das/)
3. [NEWA Crop & Pest Management](https://newa.cornell.edu/crop-and-pest-management)
4. [Mills Table Revision (MacHardy & Gadoury, 1989)](https://www.apsnet.org/publications/phytopathology/backissues/Documents/1989Articles/Phyto79n03_304.pdf)
5. [ADEM / NIAB Apple Scab Forecasting](https://www.niab.com/forecasting-apple-scab-infection-apple-scab)
6. [Apple Scab in HP — Sharma & Bhandari](https://journal.agrimetassociation.org/index.php/jam/article/download/557/460)
7. [Climate Change & Apple Diseases in HP](https://pubs.thesciencein.org/journal/index.php/jist/article/download/a795/525/2947)
8. [Codling Moth DD Models — WSU](https://treefruit.wsu.edu/crop-protection/opm/dd-models/)

---

*This research underpins every design decision in the prediction engine. When in doubt, refer back to these sources.*
