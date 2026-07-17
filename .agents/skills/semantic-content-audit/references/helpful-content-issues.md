# Helpful Content Issues & Fixes

## Issue 11: Missing First-Hand Experience

**Problem**: Content lacks evidence of actual use/testing.

**Detection**:
```
"The iPhone 15 Pro Max has excellent battery life and camera quality." ✗
```

**Fix**:
```
"After using the iPhone 15 Pro Max for 45 days, I recorded average screen-on time of 8.2 hours. The camera produced sharp images in low light at 10 lux, though I noticed 2-second shutter lag in Night mode." ✓
```

**Severity**: Critical

---

## Issue 12: Generic "Best" Claims

**Problem**: Recommending something as "best" without first-hand support.

**Detection**:
```
"The Sony WH-1000XM5 is the best noise-cancelling headphone." ✗
```

**Fix**:
```
"After testing the Sony WH-1000XM5, Bose QC45, and Apple AirPods Max in identical conditions—a 65dB office environment and 85dB aircraft cabin—the Sony reduced ambient noise by 28dB compared to 24dB (Bose) and 26dB (Apple). For office use, this makes the Sony my top recommendation." ✓
```

**Severity**: Critical

---

## Issue 13: Missing Author Information

**Problem**: No byline or author credentials.

**Detection**: Check for author name, credentials, and author page link.

**Fix**: Add author byline with relevant credentials and link to author page:
```
"By [Author Name], [Relevant Credential] with [X years] experience in [field]."
+ Link to author page with full bio
```

**Severity**: High

---

## Issue 14: Spec Recitation Without Observation

**Problem**: Content repeats manufacturer specs without personal insight.

**Detection**:
```
"The laptop weighs 1.4kg and has 16GB RAM, 512GB SSD." ✗
```

**Fix**:
```
"At 1.4kg, the laptop felt comfortable in my backpack during daily commutes over 3 weeks. The 16GB RAM handled my typical workload—15 Chrome tabs, Slack, and VS Code—without slowdown, though I noticed occasional lag when adding Figma." ✓
```

**Severity**: High

---

## Issue 15: Missing Drawbacks in Reviews

**Problem**: Review only mentions positives.

**Detection**: Search for negative observations, "however", "drawback", "issue", "problem".

**Fix**: Add honest drawbacks section based on actual use experience:
```
"Drawbacks I Discovered:
1. The oleophobic coating wore off around screen edges after 2 weeks
2. Fast charging generated noticeable heat (warm to touch)
3. Speaker distorted at volumes above 80%"
```

**Severity**: High

---

## Issue 16: Single-Source Recommendation

**Problem**: Only one purchase option provided (affiliate motivation suspected).

**Detection**: Check for multiple seller links.

**Fix**: Add links to multiple sellers/platforms:
```
"Where to Buy:
- [Amazon] - Currently [price]
- [Official Store] - Includes warranty extension
- [Lazada] - Often has bundle deals
- [Shopee] - Check for vouchers"
```

**Severity**: Medium

---

## Issue 17: Third-Party Experience Claims

**Problem**: Using "users report" or "reviews indicate" instead of first-hand experience.

**Detection**:
```
"Users report that the battery lasts all day." ✗
"According to reviews, the camera is excellent." ✗
```

**Fix**:
```
"In my 30-day test, the battery consistently lasted 9+ hours of mixed use including video calls, browsing, and document editing." ✓
```

**Severity**: High

---

## Issue 18: Missing Testing Methodology

**Problem**: Claims test results without explaining how tests were conducted.

**Detection**:
```
"Battery tested at 10 hours." ✗ (How? Under what conditions?)
```

**Fix**:
```
"Battery test methodology: Continuous video playback at 50% brightness, WiFi enabled, ambient temperature 25°C. Result: 10 hours 23 minutes." ✓
```

**Severity**: Medium

---

## Issue 19: Hypothetical Language for Factual Content

**Problem**: Using "could", "might", "may" for things that were actually tested.

**Detection**:
```
"The camera might produce good low-light photos." ✗
```

**Fix**:
```
"The camera produced usable photos at 5 lux with noise visible but details preserved. At 1 lux, noise reduction smeared fine details." ✓
```

**Severity**: Medium

---

## Issue 20: No Timeframe for Experience

**Problem**: Claims experience without specifying duration.

**Detection**:
```
"I've been using this product and it's great." ✗
```

**Fix**:
```
"After 6 weeks of daily use (averaging 4 hours per day), the build quality has held up with no visible wear on the high-touch surfaces." ✓
```

**Severity**: Medium
