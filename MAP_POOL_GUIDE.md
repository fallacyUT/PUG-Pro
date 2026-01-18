# Map Pool System Guide

**PUG Pro Discord Bot**  
**Version:** 2.0  
**Developed by:** fallacy

---

## Overview

The **Map Pool System** allows admins to configure different maps for different game modes. Maps are stored in the database, so they persist across bot updates and restarts.

---

## Key Features

✅ **Per-Mode Map Pools** - Different maps for CTF, TAM, Assault, etc.  
✅ **Database-Backed** - Maps survive bot updates/restarts  
✅ **Prefix-Based** - Shares maps across modes with same prefix  
✅ **Cooldown System** - Prevents recent maps from repeating  
✅ **Server-Specific** - Each Discord server has its own map pools

---

## How It Works

### Map Organization

Maps are organized by **mode prefix** (the same prefix used for ELO grouping):

```
Mode: ctf2v2 (elo_prefix: 'ctf')
Mode: ctf3v3 (elo_prefix: 'ctf')
Mode: ctf5v5 (elo_prefix: 'ctf')

Map Pool for 'ctf':
- CTF-Face
- CTF-FaceClassic
- CTF-LavaGiant
```

All CTF modes share the same map pool!

---

## Commands

### Add Map to Mode

```
.addmap <mode_prefix> <map_name>
```

**Examples:**
```
.addmap ctf CTF-Face
.addmap ctf CTF-LavaGiant
.addmap tam DM-Rankin
.addmap tam DM-Deck17
.addmap duel DM-1on1-Roughinery
```

**Important:** Use the mode's **elo_prefix** if it has one, otherwise use the mode name.

### Remove Map from Mode

```
.removemap <mode_prefix> <map_name>
```

**Examples:**
```
.removemap ctf CTF-Face
.removemap tam DM-Rankin
```

### List All Maps

```
.maps              Show all maps grouped by mode
.maps ctf          Show CTF maps with cooldown status
.maps tam          Show TAM maps with cooldown status
```

**Example Output:**
```
.maps

🗺️ All Map Pools

CTF (5 maps)
CTF-Face, CTF-FaceClassic, CTF-LavaGiant, CTF-Orbital, CTF-Grendelkeep

TAM (8 maps)
DM-Rankin, DM-Deck17, DM-Morpheus, DM-Compressed, ...

DUEL (3 maps)
DM-1on1-Roughinery, DM-1on1-Serpentine, DM-1on1-Spirit
```

---

## Setup Examples

### Example 1: CTF Modes

**Step 1: Set ELO Prefix (if not already done)**
```
.seteloprefix ctf2v2 ctf
.seteloprefix ctf3v3 ctf
.seteloprefix ctf5v5 ctf
```

**Step 2: Add CTF Maps**
```
.addmap ctf CTF-Face
.addmap ctf CTF-FaceClassic
.addmap ctf CTF-LavaGiant
.addmap ctf CTF-Orbital
.addmap ctf CTF-Grendelkeep
```

**Result:**
- All CTF modes use the same 5 maps
- Tiebreakers selected from these 5 maps

### Example 2: TAM Modes

**Step 1: Set ELO Prefix**
```
.seteloprefix tam2v2 tam
.seteloprefix tam4v4 tam
.seteloprefix tam6v6 tam
```

**Step 2: Add TAM Maps**
```
.addmap tam DM-Rankin
.addmap tam DM-Deck17
.addmap tam DM-Morpheus
.addmap tam DM-Compressed
.addmap tam DM-Curse4
```

**Result:**
- All TAM modes share the same 5 maps

### Example 3: Mode-Specific Maps (No Prefix)

For modes without an elo_prefix:

```
Mode: duel (no elo_prefix)

.addmap duel DM-1on1-Roughinery
.addmap duel DM-1on1-Serpentine
.addmap duel DM-1on1-Spirit
```

**Result:**
- Duel mode has its own unique 3 maps

---

## How Tiebreakers Work

### Selection Process

1. **Queue fills** (4v4 = 8 players)
2. **Bot checks** for maps configured for this mode
3. **Gets cooldown list** (last 3 used maps)
4. **Selects random map** from available (not on cooldown)
5. **Shows tiebreaker** in team announcement
6. **Adds to cooldown** when match completes

### Cooldown System

Maps are on cooldown for **3 completed matches** to prevent repeats.

**Example:**
```
Map Pool: Face, LavaGiant, Orbital, Grendelkeep (4 maps)

Match 1: Face selected → Face on cooldown
Match 2: LavaGiant selected → Face, LavaGiant on cooldown
Match 3: Orbital selected → Face, LavaGiant, Orbital on cooldown
Match 4: Grendelkeep selected → LavaGiant, Orbital, Grendelkeep on cooldown
Match 5: Face available again! → Face, Orbital, Grendelkeep on cooldown
```

### Check Cooldown Status

```
.maps ctf

Output:
✅ Available (2)
CTF-Face, CTF-Grendelkeep

⏳ On Cooldown (3)
~~CTF-LavaGiant~~ (1 PUG ago)
~~CTF-Orbital~~ (2 PUGs ago)
~~CTF-FaceClassic~~ (3 PUGs ago)
```

---

## Database Storage

### Maps Table
```sql
CREATE TABLE maps (
    id INTEGER PRIMARY KEY,
    server_id TEXT,
    mode_prefix TEXT,
    map_name TEXT,
    added_at TIMESTAMP,
    UNIQUE(server_id, mode_prefix, map_name)
)
```

**Example Data:**
```
server_id | mode_prefix | map_name
12345...  | ctf         | CTF-Face
12345...  | ctf         | CTF-LavaGiant
12345...  | tam         | DM-Rankin
12345...  | tam         | DM-Deck17
```

### Map Cooldowns Table
```sql
CREATE TABLE map_cooldowns (
    id INTEGER PRIMARY KEY,
    server_id TEXT,
    mode_prefix TEXT,
    map_name TEXT,
    used_at TIMESTAMP
)
```

**How Cooldowns Work:**
- When match completes → Map added to cooldowns
- Cooldown query → Get last 3 maps ordered by `used_at`
- Old cooldowns cleaned → Keep last 10 for history

---

## Prefix vs Mode Name

### When to Use Prefix

If your modes have an **elo_prefix** set, use that prefix for maps:

```
Modes with elo_prefix='ctf':
- ctf2v2
- ctf3v3
- ctf5v5

Add maps:
.addmap ctf CTF-Face    ← Use prefix 'ctf'
```

### When to Use Mode Name

If your mode has NO elo_prefix, use the mode name:

```
Mode: duel (no elo_prefix)

Add maps:
.addmap duel DM-1on1-Roughinery    ← Use mode name 'duel'
```

### Check Your Prefixes

```
.permodeelostatus

Shows:
✅ ctf2v2 [prefix: ctf]
✅ ctf3v3 [prefix: ctf]
✅ duel - Per-mode ELO active (no prefix shown)
```

Use the **prefix** if shown, otherwise use **mode name**.

---

## Common Workflows

### Workflow 1: New Server Setup

```bash
# 1. Create modes
.addmode ctf2v2 4
.addmode ctf3v3 6

# 2. Set ELO prefix
.seteloprefix ctf2v2 ctf
.seteloprefix ctf3v3 ctf

# 3. Enable per-mode ELO
.permodeelo ctf2v2
.permodeelo ctf3v3

# 4. Add maps
.addmap ctf CTF-Face
.addmap ctf CTF-LavaGiant
.addmap ctf CTF-Orbital

# 5. Verify
.maps ctf
```

### Workflow 2: Add New Map

```bash
.addmap ctf CTF-Grendelkeep
.maps ctf    # Verify it was added
```

### Workflow 3: Remove Unpopular Map

```bash
.maps ctf    # Check current maps
.removemap ctf CTF-Unpopular
.maps ctf    # Verify removed
```

### Workflow 4: Change Map Pool Entirely

```bash
# Remove old maps
.removemap ctf CTF-Old1
.removemap ctf CTF-Old2

# Add new maps
.addmap ctf CTF-New1
.addmap ctf CTF-New2

# Verify
.maps ctf
```

---

## Benefits

### ✅ Persistence
Maps stored in database, not in code:
- Survive bot restarts
- Survive bot updates
- Never lose map configurations

### ✅ Per-Mode Configuration
Different modes use different maps:
- CTF maps for CTF modes
- TAM maps for TAM modes
- Duel maps for duel mode

### ✅ Prefix Sharing
Modes with same prefix share maps:
- ctf2v2, ctf3v3, ctf5v5 → All use 'ctf' maps
- Fewer map pools to manage

### ✅ Cooldown Prevention
Maps don't repeat immediately:
- Last 3 maps on cooldown
- Ensures variety

### ✅ Server-Specific
Each Discord server independent:
- Server A has their maps
- Server B has their maps
- No conflicts

---

## Troubleshooting

### "No maps configured"

**Problem:** Tiebreaker not showing

**Solution:**
```bash
# Check if maps exist
.maps ctf

# If empty, add maps
.addmap ctf CTF-Face
.addmap ctf CTF-LavaGiant
```

### "Map already exists"

**Problem:** Trying to add duplicate

**Solution:**
```bash
# Map is already in pool
# Check with:
.maps ctf
```

### "Wrong prefix used"

**Problem:** `.addmap ctf2v2 CTF-Face` doesn't work

**Solution:**
```bash
# Use PREFIX not mode name
.addmap ctf CTF-Face    ← Correct (use prefix)
```

### "All maps on cooldown"

**Problem:** Only 3 maps, all on cooldown

**Solution:**
- Bot auto-resets cooldown if all maps unavailable
- Add more maps to pool:
```bash
.addmap ctf CTF-NewMap1
.addmap ctf CTF-NewMap2
```

---

## FAQ

**Q: Do maps survive bot updates?**  
A: YES! Maps are in the database, not the code.

**Q: Can different modes have different maps?**  
A: YES! Each mode_prefix has its own map pool.

**Q: What if I update bot versions?**  
A: Maps are preserved. Database migrations keep all data.

**Q: How many maps should I have?**  
A: Minimum 4 (more than cooldown count). Recommended 6-10.

**Q: Can I have mode-specific maps without prefixes?**  
A: YES! Use the mode name instead of prefix.

**Q: What happens if no maps configured?**  
A: No tiebreaker shown. PUG works fine, just no map.

**Q: Can I change maps mid-season?**  
A: YES! Add/remove anytime with .addmap/.removemap.

**Q: Do cooldowns reset between sessions?**  
A: NO! Cooldowns persist in database.

---

## Migration from Old System

### Old System (Code-Based)
```python
MAP_POOL = ['DM-Rankin', 'DM-Deck17', ...]
```

**Problems:**
- Lost on bot update
- Same maps for all modes
- Reset on restart

### New System (Database-Based)
```sql
maps table:
ctf | CTF-Face
ctf | CTF-LavaGiant
tam | DM-Rankin
tam | DM-Deck17
```

**Benefits:**
- Persists across updates
- Different maps per mode
- Never lost

### How to Migrate

If you had maps in old system:

```bash
# Add them to database
.addmap ctf CTF-Face
.addmap ctf CTF-LavaGiant
.addmap tam DM-Rankin
.addmap tam DM-Deck17
```

Old MAP_POOL variable is now unused.

---

## Summary

**Map Pool System:**
- ✅ Database-backed (survives updates)
- ✅ Per-mode configuration
- ✅ Prefix-based sharing
- ✅ Cooldown prevention
- ✅ Server-specific

**Commands:**
```
.addmap <prefix> <map>      Add map
.removemap <prefix> <map>   Remove map
.maps                       List all
.maps <prefix>              List for mode
```

**Best Practice:**
- Set elo_prefix first
- Add 6-10 maps per mode
- Use prefix for addmap
- Check with .maps regularly

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*Maps that persist, modes that matter*

**Questions?** Message **fallacy** on Discord!
