# Tiebreaker System Testing Guide

**PUG Pro Discord Bot**  
**Version:** 2.1  
**Developed by:** fallacy

---

## Overview

This guide explains how tiebreakers work and how to test that they're properly enabled/disabled.

---

## How Tiebreaker Selection Works

### Decision Tree

```
Match starts (4v4 = 8 players)
    ↓
Is tiebreaker enabled for this mode?
    ├─ NO → Skip tiebreaker (no map shown) ✅
    └─ YES → Continue
        ↓
    Are maps configured for this mode/prefix?
        ├─ NO → Skip tiebreaker (no maps) ✅
        └─ YES → Continue
            ↓
        Get maps not on cooldown
            ↓
        Select random map
            ↓
        Show tiebreaker in teams message ✅
```

---

## Three Scenarios

### Scenario 1: Tiebreaker Disabled
**Setup:**
```
Mode: duel (8 players total)
Tiebreaker: DISABLED
Maps: (doesn't matter)
```

**Expected Result:**
- ❌ NO tiebreaker shown in teams message
- Console: `[TIEBREAKER] Tiebreaker disabled for duel - skipped`

**Why:** Tiebreaker toggle is OFF

---

### Scenario 2: Tiebreaker Enabled, No Maps
**Setup:**
```
Mode: tam (8 players total)
Tiebreaker: ENABLED
Maps: NONE configured
```

**Expected Result:**
- ❌ NO tiebreaker shown in teams message
- Console: `[TIEBREAKER] No maps configured for tam (mode: tam) - tiebreaker skipped`

**Why:** Can't select a map when none exist

---

### Scenario 3: Tiebreaker Enabled, Maps Exist
**Setup:**
```
Mode: ctf2v2 (8 players total)
Tiebreaker: ENABLED
Maps: CTF-Face, CTF-LavaGiant, CTF-Orbital
```

**Expected Result:**
- ✅ Tiebreaker shown in teams message
- Example: "Tiebreaker: CTF-Face"
- Console: `[TIEBREAKER] Selected CTF-Face for ctf2v2 (mode: ctf)`

**Why:** All conditions met for tiebreaker selection

---

## Testing Commands

### Check Tiebreaker Status
```
.tiebreaker <mode>

Example:
.tiebreaker tam

Output (if enabled):
📊 Tiebreaker Status: TAM
Status: ✅ Enabled

Output (if disabled):
📊 Tiebreaker Status: TAM
Status: ❌ Disabled
```

### Enable/Disable Tiebreaker
```
.tiebreaker <mode> on        Enable
.tiebreaker <mode> off       Disable
```

### Check Maps
```
.maps <prefix>               Show maps for mode/prefix

Example:
.maps tam

Output (if maps exist):
🗺️ TAM Map Pool (5 maps)
DM-Rankin, DM-Deck17, ...

Output (if no maps):
📋 No maps configured for tam!
```

---

## Complete Test Scenarios

### Test 1: Disable Tiebreaker, Verify It's Not Shown

**Steps:**
```bash
# 1. Create mode
.addmode test 8

# 2. Add maps
.addmap test DM-Map1, DM-Map2, DM-Map3

# 3. Disable tiebreaker
.tiebreaker test off

# 4. Fill queue with 8 players
# [8 players join and ready up]

# 5. Check teams message
```

**Expected:**
- Teams shown
- ❌ NO "Tiebreaker" field in embed
- Console: `[TIEBREAKER] Tiebreaker disabled for test - skipped`

---

### Test 2: Enable Tiebreaker, No Maps, Verify It's Not Shown

**Steps:**
```bash
# 1. Create mode
.addmode test2 8

# 2. Enable tiebreaker (should be on by default)
.tiebreaker test2 on

# 3. DO NOT add any maps

# 4. Fill queue with 8 players
# [8 players join and ready up]

# 5. Check teams message
```

**Expected:**
- Teams shown
- ❌ NO "Tiebreaker" field in embed
- Console: `[TIEBREAKER] No maps configured for test2 (mode: test2) - tiebreaker skipped`

---

### Test 3: Enable Tiebreaker, Add Maps, Verify It IS Shown

**Steps:**
```bash
# 1. Create mode
.addmode test3 8

# 2. Enable tiebreaker
.tiebreaker test3 on

# 3. Add maps
.addmap test3 DM-Map1, DM-Map2, DM-Map3

# 4. Fill queue with 8 players
# [8 players join and ready up]

# 5. Check teams message
```

**Expected:**
- Teams shown
- ✅ "Tiebreaker" field showing random map
- Example: "Tiebreaker: DM-Map1"
- Console: `[TIEBREAKER] Selected DM-Map1 for test3 (mode: test3)`

---

### Test 4: Toggle Tiebreaker During Testing

**Steps:**
```bash
# 1. Setup
.addmode test4 8
.addmap test4 CTF-Face, CTF-Lava
.tiebreaker test4 on

# 2. First match - should show tiebreaker
# [8 players join, ready, teams pick]
# Expected: Tiebreaker shown ✅

# 3. Disable tiebreaker
.tiebreaker test4 off

# 4. Second match - should NOT show tiebreaker
# [8 players join, ready, teams pick]
# Expected: No tiebreaker shown ❌

# 5. Re-enable tiebreaker
.tiebreaker test4 on

# 6. Third match - should show tiebreaker again
# [8 players join, ready, teams pick]
# Expected: Tiebreaker shown ✅
```

---

## Console Debug Messages

### When Tiebreaker Is Shown
```
[TIEBREAKER] Selected CTF-Face for ctf2v2 (mode: ctf)
```
- Map was selected
- Will be shown to players
- Will be added to cooldown

### When Disabled
```
[TIEBREAKER] Tiebreaker disabled for duel - skipped
```
- Admin disabled tiebreaker for this mode
- No map selected
- No cooldown added

### When No Maps
```
[TIEBREAKER] No maps configured for tam (mode: tam) - tiebreaker skipped
```
- Tiebreaker enabled but no maps exist
- No map selected
- No cooldown added

---

## Code Flow Verification

### show_teams() Function
```python
# Line 1123-1125: Check if 4v4
if self.team_size == 8:
    tiebreaker_enabled = db_manager.is_tiebreaker_enabled(self.game_mode_name)
    
    # Line 1127: Only continue if enabled
    if tiebreaker_enabled:
        # Get maps...
        # Select tiebreaker...
        # Show in embed
    else:
        # Skip entirely (no tiebreaker shown)
```

### Database Default
```python
# is_tiebreaker_enabled() returns:
# - True (1) if explicitly enabled
# - True if column is NULL (backwards compatibility)
# - False (0) if explicitly disabled
```

---

## Common Questions

**Q: Does tiebreaker show for all match sizes?**  
A: No, only for 4v4 (8 players total). Hard-coded at line 1123.

**Q: What if I create a mode and don't set tiebreaker?**  
A: Defaults to ENABLED (backwards compatibility).

**Q: If I disable tiebreaker, does it delete maps?**  
A: No! Maps remain in database. Just won't be shown.

**Q: Can I disable tiebreaker but keep maps for reference?**  
A: Yes! Use `.tiebreaker <mode> off` and `.maps <prefix>` still shows them.

**Q: If no maps configured, does it error?**  
A: No, silently skips tiebreaker. Check console for debug message.

**Q: Do cooldowns work if tiebreaker disabled?**  
A: No, cooldowns only apply when tiebreaker is shown.

**Q: What if I add maps after disabling tiebreaker?**  
A: Maps are added to database but won't be shown until you `.tiebreaker <mode> on`.

---

## Troubleshooting

### Issue: Tiebreaker Shows When It Shouldn't

**Check:**
```
.tiebreaker <mode>
```

**If shows "Enabled":**
```
.tiebreaker <mode> off
```

---

### Issue: Tiebreaker Doesn't Show When It Should

**Check 1:** Is tiebreaker enabled?
```
.tiebreaker <mode>
```

**If "Disabled":**
```
.tiebreaker <mode> on
```

**Check 2:** Are maps configured?
```
.maps <prefix>
```

**If no maps:**
```
.addmap <prefix> Map1, Map2, Map3
```

**Check 3:** Is it 4v4?
- Tiebreaker only shows for 8-player matches
- Other sizes don't get tiebreakers

---

### Issue: Wrong Maps Being Used

**Check prefix:**
```
.permodeelostatus
```

This shows which prefix each mode uses.

**Example:**
```
✅ ctf2v2 [prefix: ctf]
✅ ctf3v3 [prefix: ctf]
```

Both use 'ctf' prefix, so both use 'ctf' maps.

**Solution:**
```
.maps ctf                    # Check maps
.addmap ctf NewMap           # Add correct maps
```

---

## Summary

**Three Requirements for Tiebreaker:**
1. ✅ Match is 4v4 (8 players)
2. ✅ Tiebreaker enabled: `.tiebreaker <mode> on`
3. ✅ Maps configured: `.addmap <prefix> <maps>`

**If ANY requirement fails:**
- ❌ No tiebreaker shown
- Console shows reason

**Debug:**
- Check console messages: `[TIEBREAKER]`
- Use `.tiebreaker <mode>` to check status
- Use `.maps <prefix>` to check maps

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*Tiebreakers when you need them, skipped when you don't*
