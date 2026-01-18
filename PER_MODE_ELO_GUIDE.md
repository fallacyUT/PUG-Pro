# Per-Mode ELO System Guide

**PUG Pro Bot**  
**A customizable version of the TAM Pro Bot**  
**Originally developed for the UT2004 Unreal Fight Club Discord Community**

**Developed by:** fallacy  
**Any questions? Please message fallacy on Discord.**

---

## Overview

The Per-Mode ELO system allows players to have **separate ELO ratings for each game mode**. This means a player who excels at one mode (e.g., competitive 5v5) can have a different rating than in another mode (e.g., casual 2v2).

**This feature is optional and disabled by default.**

---

## When to Use Per-Mode ELO

### ✅ Use Per-Mode ELO If:
- Your community plays multiple game modes with different skill requirements
- Players have varying skill levels across modes
- You want accurate matchmaking per mode
- Example: Good at Team Deathmatch but not Capture the Flag

### ❌ Don't Use Per-Mode ELO If:
- You only have one game mode
- All modes require similar skills
- You prefer a single overall skill rating
- You're just starting out (keep it simple)

---

## How It Works

### Global ELO (Default)
```
Player has ONE ELO rating: 1500

competitive match: 1500 ELO
casual match: 1500 ELO
ranked match: 1500 ELO
```

All modes share the same rating.

### Per-Mode ELO (Optional)
```
Player has SEPARATE ELO per mode:

competitive: 1650 ELO
casual: 1200 ELO  
ranked: 1450 ELO
```

Each mode tracks independently.

---

## Enabling Per-Mode ELO

### Command
```
Admin: .permodeelon
```

**What happens:**
- ✅ Each mode now tracks separate ELOs
- ✅ Existing global ELOs are preserved
- ✅ New mode-specific ELOs start at 1000
- ✅ Stats tracked separately per mode

**Example Output:**
```
✅ Per-Mode ELO Enabled
Each game mode will now track separate ELO ratings for players.

What This Means:
• Players have different ELO for each mode
• Stats are tracked separately per mode
• Use .setmodeelo to set mode-specific ELOs
• Use .mystats to see all mode ELOs

Note: Existing global ELOs are preserved
```

---

## Disabling Per-Mode ELO

### Command
```
Admin: .permodeeloff
```

**What happens:**
- ✅ Switches back to global ELO
- ✅ Mode-specific ELOs preserved (not used)
- ✅ Global ELO from players table used

---

## Checking Status

### Command
```
Admin: .permodelostatus
```

**Example Output:**
```
📊 Per-Mode ELO Status
Status: ✅ Enabled

Current Mode: Each game mode tracks separate ELO ratings
```

---

## Setting Per-Mode ELOs

### Command
```
Admin: .setmodeelo <mode> <player> <elo>
```

**Examples:**
```
.setmodeelo competitive @ProGamer 1650
.setmodeelo casual PlayerName 1200
.setmodeelo ranked @TopPlayer 1800
```

**Requirements:**
- Per-mode ELO must be enabled first
- Mode must exist (use `.modes` to check)
- ELO must be between 0-3000

**Example Output:**
```
⚙️ Mode ELO Updated: competitive
Updated competitive ELO for @ProGamer

Mode: competitive
Old ELO: 1000 (B)
New ELO: 1650 (S)
Change: +650
```

---

## How ELO Calculation Works

### Same Formula, Different Tracking

The ELO calculation formula **remains identical** for all modes:
```
Expected Score = 1 / (1 + 10^((Opponent ELO - Your ELO) / 400))
ELO Change = K-Factor × (Actual Result - Expected Score)
K-Factor = 32
```

**What changes:**
- With global ELO: Uses one rating for all modes
- With per-mode ELO: Uses mode-specific rating

### Example

**Global ELO System:**
```
Player starts: 1500 ELO (all modes)

Plays competitive match:
- Wins → 1515 ELO (all modes)

Plays casual match:
- Loses → 1500 ELO (all modes)
```

**Per-Mode ELO System:**
```
Player starts:
- competitive: 1500 ELO
- casual: 1500 ELO

Plays competitive match:
- Wins → competitive: 1515 ELO
- casual: still 1500 ELO (unchanged)

Plays casual match:
- Loses → casual: 1485 ELO
- competitive: still 1515 ELO (unchanged)
```

---

## Stats Tracking

### Global Stats (Always Tracked)
These are ALWAYS tracked regardless of mode:
- Total wins
- Total losses
- Total PUGs
- Overall win %

### Per-Mode Stats (When Enabled)
When per-mode ELO is enabled, ALSO tracked per mode:
- Mode-specific ELO
- Mode-specific wins
- Mode-specific losses
- Mode-specific peak ELO
- Mode-specific streaks

### Viewing Stats

**Global stats:**
```
Player: .mystats

Bot shows:
- Overall ELO
- Total wins/losses
- Total PUGs
```

**Per-mode stats (when enabled):**
```
Player: .mystats

Bot shows:
- Overall stats PLUS
- Breakdown per mode:
  competitive: 1650 ELO (45W-30L)
  casual: 1200 ELO (20W-25L)
  ranked: 1450 ELO (30W-28L)
```

---

## Common Scenarios

### Scenario 1: New Player Registration

**Global ELO:**
```
Admin: .setelo @NewPlayer 1000
Result: Player has 1000 ELO for all modes
```

**Per-Mode ELO:**
```
Admin: .setmodeelo competitive @NewPlayer 1000
Admin: .setmodeelo casual @NewPlayer 800
Admin: .setmodeelo ranked @NewPlayer 1100

Result: Player has different ELO per mode
```

### Scenario 2: Switching Systems

**Enable per-mode after having players:**
```
Admin: .permodeelon

Result:
- Old global ELOs preserved
- New mode ELOs start at 1000
- Admin can set mode-specific ELOs
```

**Disable per-mode:**
```
Admin: .permodeeloff

Result:
- Returns to global ELO system
- Uses old global ELOs from players table
- Mode-specific ELOs saved but not used
```

### Scenario 3: Player Plays Multiple Modes

**Per-mode ELO enabled:**
```
1. Player joins competitive queue
   - System uses competitive ELO (1650)
   - Match made with competitive ELOs
   
2. Player wins competitive match
   - competitive ELO: 1650 → 1665
   - Other mode ELOs unchanged
   
3. Player joins casual queue
   - System uses casual ELO (1200)
   - Match made with casual ELOs
   
4. Player loses casual match
   - casual ELO: 1200 → 1185
   - competitive ELO still 1665
```

---

## Best Practices

### For Admins

**1. Start Simple**
- Begin with global ELO
- Enable per-mode later if needed

**2. Set Initial Mode ELOs**
- When enabling per-mode, set starting ELOs
- Base on player's known skill per mode
- Don't just use global ELO for all modes

**3. Communicate Changes**
- Announce when enabling per-mode ELO
- Explain what it means to players
- Show how to check their mode-specific stats

**4. Be Consistent**
- Don't frequently switch between systems
- Pick one and stick with it

### For Players

**1. Understand Your Ratings**
- Check `.mystats` to see all your ELOs
- Know which modes you're strong/weak in

**2. Play Your Skill Level**
- Per-mode ELO means fair matches per mode
- You'll face appropriate opponents per mode

**3. Improve Per Mode**
- Focus on improving in specific modes
- Your bad mode won't affect your good mode

---

## Commands Reference

### Admin Commands
```
.permodeelon                           - Enable per-mode ELO
.permodeeloff                          - Disable per-mode ELO  
.permodelostatus                       - Check if enabled
.setmodeelo <mode> <player> <elo>      - Set mode-specific ELO
```

### Player Commands
```
.mystats                               - View your stats (shows all modes if enabled)
.modes                                 - List available game modes
```

### Existing Commands (Work With Both Systems)
```
.j <mode>                              - Join queue (uses appropriate ELO)
.winner red/blue                       - Report result (updates appropriate ELO)
.topelo                                - Top 10 players (uses global or primary mode)
```

---

## Database Details

### Tables

**players** (global stats)
- discord_id, server_id
- elo (global ELO)
- wins, losses, total_pugs
- peak_elo, streaks

**player_mode_elos** (per-mode stats)
- discord_id, server_id, mode_name
- elo (mode-specific)
- wins, losses (mode-specific)
- peak_elo, streaks (mode-specific)

### Settings

**bot_settings table:**
```sql
'per_mode_elo_enabled' = 'false'  (default)
'per_mode_elo_enabled' = 'true'   (when enabled)
```

---

## Troubleshooting

### Per-Mode ELO Not Working

**Issue:** Commands say "per-mode ELO not enabled"

**Solution:**
```
Admin: .permodeelon
```

### Can't Set Mode ELO

**Issue:** ".setmodeelo mode doesn't exist"

**Solution:**
```
Admin: .modes                    # Check available modes
Admin: .addmode <mode> <size>    # Create mode if needed
Admin: .setmodeelo <mode> @player <elo>
```

### Stats Show Wrong ELO

**Issue:** Player shows different ELO in match vs stats

**Check:**
1. Is per-mode ELO enabled? (`.permodelostatus`)
2. Which mode are they playing?
3. Check mode-specific ELO (`.mystats`)

### Want to Reset Per-Mode ELOs

**Solution:**
```sql
-- In database, clear player_mode_elos table
DELETE FROM player_mode_elos;
```

Then use `.setmodeelo` to set new starting ELOs.

---

## FAQ

**Q: Can I use both global and per-mode ELO?**  
A: No, it's one or the other. Choose based on your needs.

**Q: What happens to old ELOs when I enable per-mode?**  
A: Global ELOs are preserved. Mode ELOs start at 1000 or what admin sets.

**Q: Can players see their mode-specific ELOs?**  
A: Yes, `.mystats` shows all mode ELOs when enabled.

**Q: Does this affect leaderboard?**  
A: Leaderboard shows global ELO. Per-mode leaderboards are future feature.

**Q: What if I switch back to global ELO?**  
A: System uses old global ELOs. Mode ELOs are saved but not used.

**Q: Do I need to set ELO for every mode?**  
A: No, modes default to 1000 ELO if not set.

---

## Summary

**Per-Mode ELO:**
- ✅ Separate ratings per mode
- ✅ Fair matchmaking per mode
- ✅ Independent tracking
- ✅ Optional feature

**Commands:**
- `.permodeelon` - Enable
- `.permodeeloff` - Disable
- `.setmodeelo` - Set mode ELO
- `.permodelostatus` - Check status

**When to Use:**
- Multiple modes with different skills
- Want accurate per-mode ratings

**When Not to Use:**
- One game mode
- Keep it simple
- Just starting out

---

**Questions?** Message **fallacy** on Discord!

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*A customizable version of the TAM Pro Bot*  
*Originally developed for the UT2004 Unreal Fight Club Discord Community*
