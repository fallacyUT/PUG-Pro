# ELO Prefix System Guide

**PUG Pro Discord Bot**  
**Version:** 2.0  
**Developed by:** fallacy

---

## Overview

The **ELO Prefix System** allows you to group multiple game modes under a single ELO pool. This is perfect for game modes that are the same type but have different team sizes.

---

## Problem This Solves

**Without ELO Prefix:**
```
Modes:
- ctf2v2 (1v1 CTF) → ELO: 1500
- ctf3v3 (1.5v1.5 CTF) → ELO: 1000
- ctf5v5 (2.5v2.5 CTF) → ELO: 1000

Problem: Player is good at CTF but has different ELO for each team size!
```

**With ELO Prefix:**
```
All modes use prefix 'ctf':
- ctf2v2 → Uses 'ctf' ELO: 1500
- ctf3v3 → Uses 'ctf' ELO: 1500
- ctf5v5 → Uses 'ctf' ELO: 1500

Solution: Player has ONE CTF ELO across all team sizes!
```

---

## How It Works

### Step 1: Enable Per-Mode ELO for Modes
```
.permodeelo ctf2v2
.permodeelo ctf3v3
.permodeelo ctf5v5
```

### Step 2: Set ELO Prefix for Each Mode
```
.seteloprefix ctf2v2 ctf
.seteloprefix ctf3v3 ctf
.seteloprefix ctf5v5 ctf
```

### Step 3: Set Player ELO (Once!)
```
.setmodeelo ctf2v2 @Player 1500
```

This sets the player's **'ctf' ELO** to 1500.

### Result
```
Player joins ctf2v2 → Uses 'ctf' ELO: 1500
Player joins ctf3v3 → Uses 'ctf' ELO: 1500
Player joins ctf5v5 → Uses 'ctf' ELO: 1500

Player wins ctf3v3 → 'ctf' ELO: 1500 → 1515
Player joins ctf5v5 → Uses updated 'ctf' ELO: 1515
```

All CTF modes share ONE ELO!

---

## Commands

### Set ELO Prefix
```
.seteloprefix <mode> <prefix>
```

**Examples:**
```
.seteloprefix ctf2v2 ctf
.seteloprefix tam4v4 tam
.seteloprefix assault2v2 assault
```

### Remove ELO Prefix
```
.seteloprefix <mode> none
```

**Example:**
```
.seteloprefix ctf2v2 none
```
Now ctf2v2 uses its own ELO, not the 'ctf' prefix.

### Check Status
```
.permodeelostatus
```

Shows which modes have prefixes:
```
📊 Per-Mode ELO Status

Modes with Per-Mode ELO:
✅ ctf2v2 [prefix: ctf] - Per-mode ELO active
✅ ctf3v3 [prefix: ctf] - Per-mode ELO active
✅ ctf5v5 [prefix: ctf] - Per-mode ELO active
✅ tam4v4 [prefix: tam] - Per-mode ELO active
```

---

## Use Cases

### Use Case 1: CTF with Multiple Team Sizes

**Setup:**
```
Modes created:
- ctf1v1 (1v1)
- ctf2v2 (2v2)
- ctf3v3 (3v3)
- ctf5v5 (5v5)

Commands:
.permodeelo ctf1v1
.permodeelo ctf2v2
.permodeelo ctf3v3
.permodeelo ctf5v5

.seteloprefix ctf1v1 ctf
.seteloprefix ctf2v2 ctf
.seteloprefix ctf3v3 ctf
.seteloprefix ctf5v5 ctf

.setmodeelo ctf1v1 @Player 1600
```

**Result:**
- Player has 1600 CTF ELO
- Works for 1v1, 2v2, 3v3, 5v5
- One ELO across all CTF team sizes

### Use Case 2: TAM with Different Sizes

**Setup:**
```
Modes:
- tam2v2
- tam4v4
- tam6v6

Commands:
.permodeelo tam2v2
.permodeelo tam4v4
.permodeelo tam6v6

.seteloprefix tam2v2 tam
.seteloprefix tam4v4 tam
.seteloprefix tam6v6 tam
```

**Result:**
- All TAM modes share one ELO
- Player's TAM skill translates across team sizes

### Use Case 3: Mixed Setup

**Setup:**
```
Modes:
- ctf2v2, ctf5v5 → Use 'ctf' prefix
- tam4v4, tam6v6 → Use 'tam' prefix
- casual → No prefix, own ELO
- duel → No prefix, own ELO

Commands:
.permodeelo ctf2v2
.permodeelo ctf5v5
.seteloprefix ctf2v2 ctf
.seteloprefix ctf5v5 ctf

.permodeelo tam4v4
.permodeelo tam6v6
.seteloprefix tam4v4 tam
.seteloprefix tam6v6 tam

.permodeelo casual
.permodeelo duel
```

**Result:**
```
Player ELOs:
- ctf: 1700 (shared by ctf2v2 and ctf5v5)
- tam: 1500 (shared by tam4v4 and tam6v6)
- casual: 1400 (only for casual)
- duel: 1600 (only for duel)
```

---

## How ELO is Determined

### Decision Flow

When a player joins a queue or match completes:

1. **Check if mode has per-mode ELO enabled**
   - NO → Use global ELO
   - YES → Continue to step 2

2. **Check if mode has elo_prefix set**
   - NO → Use mode name for ELO lookup
   - YES → Use prefix for ELO lookup

**Examples:**

```
Mode: ctf2v2
Per-mode ELO: Enabled
ELO Prefix: 'ctf'
→ Uses 'ctf' ELO

Mode: ctf5v5
Per-mode ELO: Enabled
ELO Prefix: 'ctf'
→ Uses 'ctf' ELO (SAME as ctf2v2)

Mode: casual
Per-mode ELO: Enabled
ELO Prefix: None
→ Uses 'casual' ELO

Mode: training
Per-mode ELO: Disabled
→ Uses global ELO
```

---

## Database Structure

### game_modes Table
```sql
CREATE TABLE game_modes (
    mode_name TEXT PRIMARY KEY,
    display_name TEXT,
    team_size INTEGER,
    description TEXT,
    per_mode_elo_enabled INTEGER,
    elo_prefix TEXT           -- NEW!
)
```

**Example Data:**
```
mode_name | per_mode_elo_enabled | elo_prefix
ctf2v2    | 1                    | ctf
ctf3v3    | 1                    | ctf
ctf5v5    | 1                    | ctf
tam4v4    | 1                    | tam
tam6v6    | 1                    | tam
casual    | 1                    | NULL
```

### player_mode_elos Table
```sql
CREATE TABLE player_mode_elos (
    discord_id TEXT,
    server_id TEXT,
    mode_name TEXT,      -- Stores the PREFIX if set!
    elo REAL,
    wins INTEGER,
    losses INTEGER,
    ...
    PRIMARY KEY (discord_id, server_id, mode_name)
)
```

**Example Data:**
```
discord_id | server_id | mode_name | elo
123...     | default   | ctf       | 1700  ← Shared by ctf2v2, ctf3v3, ctf5v5
123...     | default   | tam       | 1500  ← Shared by tam4v4, tam6v6
123...     | default   | casual    | 1400  ← Only casual
```

---

## Technical Details

### get_effective_mode_for_elo()

This function determines which mode name to use for ELO:

```python
def get_effective_mode_for_elo(mode_name):
    """
    Returns the effective mode name for ELO purposes.
    If mode has elo_prefix, returns prefix.
    Otherwise returns mode_name.
    """
    elo_prefix = get_mode_elo_prefix(mode_name)
    return elo_prefix if elo_prefix else mode_name
```

**Examples:**
```python
get_effective_mode_for_elo('ctf2v2')  # Has prefix 'ctf'
→ Returns: 'ctf'

get_effective_mode_for_elo('ctf5v5')  # Has prefix 'ctf'
→ Returns: 'ctf'

get_effective_mode_for_elo('casual')  # No prefix
→ Returns: 'casual'
```

### Match Processing

When a match completes:

```python
mode_name = 'ctf3v3'
effective_mode = get_effective_mode_for_elo('ctf3v3')  # Returns 'ctf'

# Update ELO using 'ctf' as the mode name
update_player_mode_elo(player_id, server_id, 'ctf', new_elo)
```

---

## Benefits

### ✅ Realistic Skill Tracking
- Player's CTF skill is the same regardless of team size
- No artificial ELO differences between 2v2 and 5v5

### ✅ Easier Management
- Set ELO once per game type, not per team size
- Less modes to manage in `.permodeelostatus`

### ✅ Better Matchmaking
- Players matched by actual game type skill
- No ELO reset when playing different team size

### ✅ Flexible
- Can group some modes, leave others separate
- Mix and match as needed

---

## Common Questions

**Q: Do I have to use prefixes?**  
A: No! Prefixes are optional. Modes without prefixes work normally.

**Q: Can different modes share the same prefix?**  
A: Yes! That's the whole point. ctf2v2 and ctf5v5 both use 'ctf'.

**Q: What if I set different prefixes for similar modes?**  
A: They won't share ELO. ctf2v2 with prefix 'ctf2' and ctf5v5 with prefix 'ctf5' have separate ELOs.

**Q: Can I change a prefix later?**  
A: Yes, use `.seteloprefix <mode> <new_prefix>`. Existing ELO data is preserved.

**Q: What happens to stats when using prefixes?**  
A: Wins/losses are tracked under the prefix name. Example: All CTF wins/losses count toward 'ctf' stats.

**Q: Can I remove a prefix?**  
A: Yes, use `.seteloprefix <mode> none`

**Q: Do I need per-mode ELO enabled to use prefixes?**  
A: Yes! The mode must have per-mode ELO enabled first.

---

## Migration Example

### Before: Separate ELOs per Team Size

```
Player stats:
- ctf2v2: 1500 ELO
- ctf3v3: 1000 ELO (just started)
- ctf5v5: 1000 ELO (just started)

Problem: Player is good at CTF but stats don't reflect it!
```

### After: Shared CTF ELO

```
Admin setup:
.seteloprefix ctf2v2 ctf
.seteloprefix ctf3v3 ctf
.seteloprefix ctf5v5 ctf

Player stats (automatically merged):
- ctf: 1500 ELO (from ctf2v2)
- Wins/losses combined

Result: Player's true CTF skill is shown!
```

---

## Best Practices

### 1. Group Similar Game Types
```
Good grouping:
- All CTF modes → 'ctf' prefix
- All TAM modes → 'tam' prefix
- All Assault modes → 'assault' prefix

Bad grouping:
- CTF and TAM → Don't group different game types!
```

### 2. Use Descriptive Prefixes
```
Good: 'ctf', 'tam', 'duel', 'assault'
Bad: 'mode1', 'a', 'x'
```

### 3. Be Consistent
```
If ctf2v2 uses 'ctf', then:
- ctf3v3 should use 'ctf'
- ctf5v5 should use 'ctf'
Don't mix and match!
```

### 4. Document Your Setup
Keep notes on which modes share prefixes so you remember later.

---

## Summary

**ELO Prefix System:**
- Group modes by game type instead of team size
- Set once with `.seteloprefix <mode> <prefix>`
- All modes with same prefix share one ELO pool
- Optional feature - use only if needed

**Commands:**
```
.seteloprefix ctf2v2 ctf        Set prefix
.seteloprefix ctf2v2 none       Remove prefix
.permodeelostatus                See all prefixes
```

**Perfect for:**
- CTF with multiple team sizes
- TAM with 2v2, 4v4, 6v6
- Any game type with different team sizes

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*A customizable version of the PUG Pro Bot*  
*Originally developed for the UT2004 Unreal Fight Club Discord Community*

**Questions?** Message **fallacy** on Discord!
