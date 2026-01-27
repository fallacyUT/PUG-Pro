# Per-Mode ELO System - Updated Guide

**PUG Pro Bot**  
**A customizable version of the TAM Pro Bot**  
**Originally developed for the UT2004 Unreal Fight Club Discord Community**

**Developed by:** fallacy  
**Version:** 2.0 - Mode-Specific Per-Mode ELO  
**Any questions? Please message fallacy on Discord.**

---

## 🎯 What's New in Version 2.1

### Major Update: Mode-Specific Per-Mode ELO

**Old System (v1.0):**
- `.permodeelon` enabled per-mode ELO for ALL modes
- All-or-nothing approach

**New System (v2.0):**
- `.permodeelo <mode>` enables per-mode ELO for SPECIFIC modes
- Mix and match: Some modes use per-mode ELO, others use global
- More flexible and realistic

---

## How It Works Now

### Example Setup
```
Modes:
- TAM (competitive) → Per-mode ELO ENABLED
- CTF (competitive) → Per-mode ELO ENABLED
- Casual → Per-mode ELO DISABLED (uses global ELO)
- Training → Per-mode ELO DISABLED (uses global ELO)
```

### What This Means
```
Player stats:
- Global ELO: 1400 (used by Casual and Training)
- TAM ELO: 1700 (used only for TAM matches)
- CTF ELO: 1100 (used only for CTF matches)

When playing:
- TAM match → Uses 1700 ELO
- CTF match → Uses 1100 ELO
- Casual match → Uses 1400 global ELO
- Training match → Uses 1400 global ELO
```

---

## Commands

### Enable/Disable Per-Mode ELO for a Specific Mode
```
.permodeelo <mode>    Toggle per-mode ELO for that mode
```

**Examples:**
```
.permodeelo tam
✅ Per-Mode ELO Enabled for TAM

.permodeelo ctf
✅ Per-Mode ELO Enabled for CTF

.permodeelo casual
✅ Per-Mode ELO Disabled for casual
```

**How it works:**
- First time: Enables per-mode ELO for that mode
- Second time: Disables per-mode ELO for that mode
- Toggle on/off for each mode independently

### Check Status
```
.permodeelostatus      Show which modes have per-mode ELO
```

**Example output:**
```
📊 Per-Mode ELO Status

Modes with Per-Mode ELO:
✅ TAM - Per-mode ELO active
✅ CTF - Per-mode ELO active

Modes using Global ELO:
❌ casual - Uses global ELO
❌ training - Uses global ELO

Use .permodeelo <mode> to toggle
```

### Set Mode-Specific ELO
```
.setmodeelo <mode> <player> <elo>    Set player's ELO for a mode
```

**Requirements:**
- That mode must have per-mode ELO enabled first
- If not enabled, you'll get an error

**Examples:**
```
.setmodeelo tam @ProPlayer 1700
✅ TAM ELO set to 1700

.setmodeelo casual @ProPlayer 1500
❌ Per-mode ELO is not enabled for casual!
   Use .permodeelo casual to enable it first.
```

---

## Use Cases

### Scenario 1: Competitive vs Casual Split

**Problem:** Want separate ratings for competitive modes, but casual modes should share one rating

**Solution:**
```
.permodeelo tam           # Enable for competitive TAM
.permodeelo ctf           # Enable for competitive CTF
# Leave casual disabled

Result:
- TAM uses mode-specific ELO (e.g., 1700)
- CTF uses mode-specific ELO (e.g., 1100)
- Casual uses global ELO (e.g., 1400)
- Training uses global ELO (e.g., 1400)
```

### Scenario 2: One Mode Needs Separate Tracking

**Problem:** CTF plays very differently, needs separate ELO, but other modes are similar

**Solution:**
```
.permodeelo ctf           # Enable only for CTF

Result:
- CTF uses mode-specific ELO
- All other modes use global ELO
```

### Scenario 3: Testing Per-Mode ELO

**Problem:** Want to try per-mode ELO for one mode first

**Solution:**
```
.permodeelo experimental  # Enable for test mode
# Try it out...
.permodeelo experimental  # Disable if not working
```

---

## How ELO is Selected

### Decision Tree
```
Player joins TAM match:
1. Is TAM mode configured with per-mode ELO?
   └─ YES → Use player's TAM-specific ELO
   └─ NO  → Use player's global ELO

Player joins Casual match:
1. Is Casual mode configured with per-mode ELO?
   └─ YES → Use player's Casual-specific ELO
   └─ NO  → Use player's global ELO
```

### Code Logic
```python
def get_player_elo(discord_id, server_id, mode_name):
    if db_manager.is_per_mode_elo_enabled(mode_name):
        # Mode has per-mode ELO - use mode-specific rating
        return player_mode_elos.elo
    else:
        # Mode doesn't have per-mode ELO - use global rating
        return players.elo
```

---

## Benefits of Mode-Specific Per-Mode ELO

### ✅ Flexibility
- Enable only where needed
- Don't over-complicate simple modes
- Test on one mode before expanding

### ✅ Realistic
- Some modes need separate tracking
- Others don't - no need to force it

### ✅ Easier Management
- Less ELOs to manage for admins
- Players don't need to track 10 different ELOs

### ✅ Better UX
- Casual players see one ELO (global)
- Competitive players see relevant mode ELOs
- Not overwhelming

---

## Migration from v1.0

### If You Used Old Commands

**Old Command:** `.permodeelon`  
**New Approach:**
```
# Enable for each mode you want
.permodeelo tam
.permodeelo ctf
.permodeelo competitive
```

**Old Command:** `.permodeeloff`  
**New Approach:**
```
# Disable for each mode
.permodeelo tam
.permodeelo ctf
```

**Old Command:** `.permodeelostatus`  
**Still works!** Now shows per-mode breakdown

---

## Database Changes

### game_modes Table
**New Column:** `per_mode_elo_enabled INTEGER DEFAULT 0`

```sql
CREATE TABLE game_modes (
    mode_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    team_size INTEGER NOT NULL,
    description TEXT,
    per_mode_elo_enabled INTEGER DEFAULT 0  -- NEW!
)
```

### Migration
Existing databases automatically get the new column with default value 0 (disabled).

---

## Common Workflows

### Setup: Competitive Scene with Casual Modes

```bash
# 1. Create modes
.addmode tam 8
.addmode ctf 8
.addmode casual 8
.addmode training 4

# 2. Enable per-mode ELO for competitive modes only
.permodeelo tam
.permodeelo ctf
# Leave casual and training using global ELO

# 3. Set starting ELOs for competitive modes
.setmodeelo tam @ProPlayer 1500
.setmodeelo ctf @ProPlayer 1500

# 4. Check configuration
.permodeelostatus
```

### Setup: All Modes Separate

```bash
# Enable per-mode ELO for every mode
.permodeelo tam
.permodeelo ctf
.permodeelo assault
.permodeelo casual

# Set ELOs for each
.setmodeelo tam @Player 1700
.setmodeelo ctf @Player 1100
.setmodeelo assault @Player 1400
.setmodeelo casual @Player 1300
```

### Setup: Test One Mode

```bash
# Just test CTF first
.permodeelo ctf

# Set some initial ELOs
.setmodeelo ctf @Player1 1600
.setmodeelo ctf @Player2 1400

# Try it out...
# If it works well, enable for other modes
# If not, disable
.permodeelo ctf
```

---

## FAQ

**Q: What happens to mode ELOs when I disable per-mode ELO for a mode?**  
A: They're preserved in the database but not used. If you re-enable, they come back.

**Q: Can I enable per-mode ELO for some modes and not others?**  
A: YES! That's the whole point of v2.0. Mix and match.

**Q: What's the default when I create a new mode?**  
A: Per-mode ELO is disabled. Mode uses global ELO until you enable it.

**Q: Do I have to set ELOs for every player in every mode?**  
A: No. Mode ELOs default to 1000 if not set. Or just don't enable per-mode ELO for that mode.

**Q: Can I switch a mode back and forth?**  
A: Yes. `.permodeelo <mode>` toggles it. ELOs are preserved.

**Q: How do I know which modes have per-mode ELO?**  
A: Use `.permodeelostatus` - shows complete breakdown.

**Q: What if I enable per-mode ELO but don't set any ELOs?**  
A: Players start at 1000 ELO for that mode.

---

## Comparison

### v1.0 (Global Enable/Disable)
```
.permodeelon
Result: ALL modes use per-mode ELO

.permodeeloff
Result: ALL modes use global ELO
```

### v2.0 (Per-Mode Control)
```
.permodeelo tam
Result: TAM uses per-mode ELO, others unchanged

.permodeelo ctf
Result: CTF uses per-mode ELO, others unchanged

.permodeelo casual
Result: Toggles casual (if it was on, turns off; if off, turns on)
```

---

## Best Practices

### Start Simple
1. Create all your modes
2. Enable per-mode ELO for 1-2 competitive modes only
3. Leave casual/fun modes using global ELO
4. Expand if needed

### For Competitive Communities
```
# Separate tracking for each competitive mode
.permodeelo competitive-5v5
.permodeelo competitive-3v3
.permodeelo competitive-1v1
# Leave casual modes global
```

### For Mixed Communities
```
# Separate for main modes only
.permodeelo ranked
.permodeelo competitive
# Everything else global
```

### For Simple Communities
```
# Don't enable per-mode ELO at all
# Just use global ELO for everything
# (This is fine!)
```

---

## Troubleshooting

### "Per-mode ELO not enabled for this mode"

**When setting mode ELO:**
```
.setmodeelo casual @Player 1500
❌ Per-mode ELO is not enabled for casual!
```

**Solution:**
```
.permodeelo casual
✅ Per-Mode ELO Enabled for casual

.setmodeelo casual @Player 1500
✅ Success!
```

### Check Current Configuration
```
.permodeelostatus

Shows exactly which modes have per-mode ELO
```

---

## Summary

**v2.0 Per-Mode ELO System:**
- ✅ Enable per-mode ELO per individual mode
- ✅ Mix modes with per-mode ELO and global ELO
- ✅ More flexible and realistic
- ✅ Easier to manage
- ✅ Better for most communities

**Commands:**
```
.permodeelo <mode>                    Toggle per-mode ELO for mode
.permodeelostatus                      Show which modes have it
.setmodeelo <mode> <player> <elo>     Set mode-specific ELO
```

**Philosophy:**
Not every mode needs separate ELO tracking. Enable it where it makes sense, leave others using global ELO.

---

**Questions?** Message **fallacy** on Discord!

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*A customizable version of the TAM Pro Bot*  
*Originally developed for the UT2004 Unreal Fight Club Discord Community*
