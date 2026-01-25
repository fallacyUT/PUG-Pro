# PUG Pro Bot - Complete Feature Summary

**Version:** 2.1  
**Developed by:** fallacy  
**Date:** January 2026

---

## 🎯 Overview

PUG Pro is a comprehensive Discord bot for managing competitive gaming pickup games (PUGs). Originally developed for Unreal Tournament 2004, it's fully customizable for any competitive game.

---

## 📦 Package Contents

### Core Files
- `pug_bot.py` - Main bot code (7,800+ lines)
- `database.py` - SQLite database manager (1,700+ lines)
- `scraper.py` - Game server scraper
- `requirements.txt` - Python dependencies

### Documentation (20 Files)
- README.md
- QUICKSTART.md
- CHANGELOG.md
- COMMANDS.md
- ADMIN_GUIDE.md
- PLAYER_GUIDE.md
- MAP_POOL_GUIDE.md
- ELO_PREFIX_GUIDE.md
- PER_MODE_ELO_V2_GUIDE.md
- DATABASE_MIGRATION_GUIDE.md
- TIEBREAKER_TESTING.md
- QUEUE_TIMEOUT_FIX.md
- COMPLETE_FEATURE_SUMMARY.md (this file)
- Plus 7 more specialized guides

---

## 🚀 Major Features

### 1. Queue Management System
**Multiple concurrent queues** for different game modes
- Join/leave queues with simple commands
- Waiting list system when queue is full
- Auto-expire timers to auto-remove inactive players
- Queue status display with ELO rankings
- Ready check system with timeout handling
- Promotion from waiting list when slots open

**Commands:**
```
.j <mode>          Join queue
++ <mode>          Quick join
.l <mode>          Leave queue
.list              Show all queues
.list <mode>       Show specific queue
.expire <time>     Auto-leave after time
.expire cancel     Cancel timer
```

---

### 2. Team Selection System

#### Autopick Mode (Recommended)
- Automatically balances teams using ELO
- Considers win probability and variance
- Multiple optimization criteria for fair matches
- Mode-aware ELO (uses correct ELO per mode)

#### Manual Captain Mode
- Players volunteer as captains
- Auto-captain selection after timeout
- Snake draft picking
- Admin can pick for captains

**Commands:**
```
.autopick <mode>       Enable autopick
.autopickoff <mode>    Disable autopick
.captain               Volunteer as captain
.pick <player>         Captain picks player
```

---

### 3. ELO System (Three-Tier)

#### Global ELO (Traditional)
- Single ELO rating for all modes
- Default: 1000 starting ELO
- Standard ELO calculation (K=32)

#### Per-Mode ELO (v2.0)
- Separate ELO for each mode
- Enable per mode, not all-or-nothing
- Mix competitive and casual modes

#### ELO Prefix System (v2.0)
- Group modes under one ELO pool
- Perfect for different team sizes
- Example: ctf2v2, ctf3v3, ctf5v5 all use "ctf" ELO

**Commands:**
```
# Per-Mode ELO
.permodeelo <mode>                Toggle per-mode ELO
.permodeelostatus                 Show which modes enabled
.setmodeelo <mode> @player <elo>  Set mode-specific ELO

# ELO Prefix System
.seteloprefix <mode> <prefix>     Group modes under prefix
.seteloprefix <mode> none         Remove prefix
```

**Example Setup:**
```
.addmode ctf2v2 4
.addmode ctf3v3 6
.addmode ctf5v5 10

.seteloprefix ctf2v2 ctf
.seteloprefix ctf3v3 ctf
.seteloprefix ctf5v5 ctf

.permodeelo ctf2v2
.permodeelo ctf3v3
.permodeelo ctf5v5

Result: All CTF modes share one "ctf" ELO
```

---

### 4. Database-Backed Map Pool System (v2.1)

#### Features
- Maps stored in database (persist across updates)
- Per-mode/prefix map pools
- Map cooldown system (prevents repeats)
- Bulk map adding
- Case-insensitive operations

#### Map Pool Management
```
# Add Maps
.addmap ctf CTF-Face                              Single map
.addmap ctf CTF-Face, CTF-Lava, CTF-Orbital      Multiple maps

# Remove Maps
.removemap ctf CTF-Face                          One map
.removeallmaps ctf                               All maps

# List Maps
.maps                                            All maps grouped by mode
.maps ctf                                        CTF maps with cooldowns

# Cleanup Accidental Prefixes
.listmapprefixes                                 Show all prefixes
.deletemapprefix <prefix>                        Delete invalid prefix
.confirmdeletemapprefix <prefix>                 Confirm deletion
```

#### Map Cooldown System
- Last 3 used maps on cooldown
- Automatic rotation
- Database-backed persistence
- Per-mode cooldown tracking

---

### 5. Tiebreaker System (v2.1)

#### Features
- Random map selection for 4v4 matches
- Per-mode enable/disable
- Uses map pool system
- Respects cooldowns
- Only shows if enabled AND maps configured

**Commands:**
```
.tiebreaker <mode> on      Enable tiebreaker
.tiebreaker <mode> off     Disable tiebreaker
.tiebreaker <mode>         Check status
```

**Requirements for Tiebreaker:**
1. Match is 4v4 (8 players)
2. Tiebreaker enabled for mode
3. Maps configured for mode/prefix

---

### 6. Match Results System

#### Winner Declaration
- Vote-based system (2 votes required)
- Admin can force winner
- Undo capability
- Split wins for incomplete BO3

**Commands:**
```
.winner red                Vote red team won
.winner blue               Vote blue team won
.splitwin                  Declare 1-1 split
.setwinner <pug#> red      Admin force winner
.undowinner <pug#>         Undo winner
```

#### Dead PUG System
```
.deadpug                   Vote to cancel
.forcedeadpug <pug#>       Admin cancel
.undodeadpug <pug#>        Restore cancelled PUG
```

---

### 7. Statistics System

#### Player Stats
- Wins/Losses
- Win rate
- ELO (global and per-mode)
- Peak ELO
- Total PUGs played
- Streaks (current, best win, best loss)

**Commands:**
```
.mystats                   Your stats
.stats @player             Another player's stats
.top10                     Top 10 most active
.topelo                    Top 10 by ELO
.topratio                  Top 10 by win rate
```

#### Leaderboard
- Auto-updating channel
- Sortable by ELO, wins, win rate
- Configurable refresh

---

### 8. Game Mode System

#### Mode Management
```
.addmode <name> <size>         Create mode (e.g., .addmode tam 8)
.removemode <name>             Delete mode
.modes                         List all modes
.addalias <mode> <alias>       Add mode alias
.removealias <alias>           Remove alias
```

#### Mode Features
- Customizable team sizes
- Display names
- Descriptions
- Aliases for easy access
- Per-mode autopick toggle
- Per-mode ELO toggle
- Per-mode tiebreaker toggle

---

### 9. Admin Tools

#### Player Management
```
.setelo @player <elo>              Set global ELO
.setmodeelo <mode> @player <elo>   Set mode-specific ELO
.setpugs @player <count>           Set total PUGs
.deleteplayer @player              Delete player
.undoplayerpugs @player            Reset win/loss to match total
```

#### Queue Management
```
.reset <mode>                  Reset specific queue
.resetall                      Reset all queues
.add @player <mode>            Add player to queue
.remove @player <mode>         Remove player from queue
```

#### Data Management
```
.exportstats                   Export all player data to CSV
.importelos                    Import ELO updates from CSV
.updateplayerpugs              Bulk update PUG counts
.undoupdateplayerpugs          Undo last bulk update
.examplepugcsv                 Generate template CSV
.reseteloall                   Reset all ELOs to 700
.resetplayerpugs               Reset all wins/losses to 0
```

#### Bot Control
```
.tamproon / .pugproon          Enable bot
.tamprooff / .pugprooff        Disable bot
.leaderboard                   Update leaderboard
.cleartopelo                   Clear ELO cache
```

---

### 10. Advanced Features

#### UT2004 Integration (Optional)
- Server scraping
- Player name linking
- Live server status
- Stats integration

#### Multi-Server Support
- Each Discord server has separate database
- Independent settings per server
- Server-specific map pools
- Server-specific modes

#### Database Migrations
- Automatic schema updates
- **Data preservation** (no data loss on updates)
- Safe upgrades from v1.0 → v2.0 → v2.1
- Migration logging

---

## 📋 Complete Command Reference

### Player Commands

#### Queue Commands
```
.register                       Register for PUG tracking
.j <mode>                       Join mode queue
++ <mode>                       Quick join mode
.l <mode>                       Leave mode queue
.list                          Show all queue statuses
.list <mode>                   Show specific queue status
.expire <time>                 Auto-leave after time (e.g., 20m, 1h)
.expire cancel                 Cancel expire timer
```

#### Match Commands
```
.ready                         Ready up for match
.captain                       Volunteer as captain
.pick <player>                 Pick player (captain only)
.winner red/blue               Vote for winner
.splitwin                      Declare 1-1 split
.deadpug                       Vote to cancel PUG
```

#### Statistics Commands
```
.mystats                       View your statistics
.stats @player                 View player statistics
.top10                         Top 10 most active players
.topelo                        Top 10 by ELO rating
.topratio                      Top 10 by win percentage
.modes                         List available game modes
```

---

### Admin Commands

#### Player Management
```
.setelo @player <elo>                Set player's global ELO
.setmodeelo <mode> @player <elo>     Set player's mode ELO
.setpugs @player <count>             Set player's total PUG count
.deleteplayer @player                Delete player from database
.undoplayerpugs @player              Reset player's wins/losses
```

#### Per-Mode ELO Management
```
.permodeelo <mode>                   Toggle per-mode ELO for mode
.permodeelostatus                    Show which modes have per-mode ELO
.setmodeelo <mode> @player <elo>     Set player's ELO for mode
.seteloprefix <mode> <prefix>        Set ELO prefix to group modes
.seteloprefix <mode> none            Remove ELO prefix
```

#### Match Management
```
.setwinner <pug#> red/blue          Override PUG winner
.undowinner                         Undo most recent winner
.undowinner <pug#>                  Undo specific PUG
.forcedeadpug <pug#>                Force cancel PUG
.undodeadpug <pug#>                 Undo cancelled PUG
```

#### Queue Management
```
.reset <mode>                       Reset specific queue
.resetall                           Reset all queues
.add @player <mode>                 Add player to queue
.remove @player <mode>              Remove player from queue
```

#### Game Mode Management
```
.addmode <name> <size>              Create new game mode
.removemode <name>                  Delete game mode
.addalias <mode> <alias>            Add alias for mode
.removealias <alias>                Remove mode alias
.autopick <mode>                    Enable auto team picking
.autopickoff <mode>                 Disable auto team picking
```

#### Map Pool Management
```
.addmap <prefix> <maps>             Add map(s) (comma-separated)
.removemap <prefix> <map>           Remove map from pool
.removeallmaps <prefix>             Remove ALL maps from pool
.deletemapprefix <prefix>           Delete accidental prefix
.confirmdeletemapprefix <prefix>    Confirm prefix deletion
.listmapprefixes                    List all map prefixes
.maps                               Show all maps grouped by mode
.maps <prefix>                      Show maps with cooldowns
```

#### Tiebreaker Management
```
.tiebreaker <mode> on               Enable tiebreaker for mode
.tiebreaker <mode> off              Disable tiebreaker for mode
.tiebreaker <mode>                  Check tiebreaker status
```

#### Data Management
```
.exportstats                        Export all player data to CSV
.importelos                         Import ELO updates from CSV
.updateplayerpugs                   Bulk update PUG counts from CSV
.undoupdateplayerpugs               Undo last bulk update
.examplepugcsv                      Generate template CSV
.reseteloall                        Reset all ELOs to 700
.resetplayerpugs                    Reset all wins/losses to 0
```

#### Bot Control
```
.tamproon / .pugproon               Enable bot
.tamprooff / .pugprooff             Disable bot
.leaderboard                        Update leaderboard
.cleartopelo                        Clear top ELO cache
```

#### Team Management (Captain Mode)
```
.pickforred @player                 Admin pick for red captain
.pickforblue @player                Admin pick for blue captain
.undopickforred                     Undo last red pick
.undopickforblue                    Undo last blue pick
```

---

## 🗄️ Database Schema

### Tables
1. **players** - Player profiles, global ELO, stats
2. **pugs** - Match history
3. **game_modes** - Mode configurations
4. **mode_aliases** - Mode name aliases
5. **pug_admins** - Admin permissions
6. **player_mode_elos** - Per-mode ELO ratings
7. **maps** - Map pools per mode/prefix
8. **map_cooldowns** - Recently used maps
9. **bot_settings** - Bot configuration

### Data Preservation
- All migrations preserve existing data
- No data loss on version updates
- Safe rollback capability
- Automatic backups recommended

---

## 🎮 Common Workflows

### Setting Up a New Mode
```bash
# 1. Create mode
.addmode ctf5v5 10

# 2. Enable per-mode ELO
.permodeelo ctf5v5

# 3. Set ELO prefix (optional, for grouping)
.seteloprefix ctf5v5 ctf

# 4. Enable autopick
.autopick ctf5v5

# 5. Add maps
.addmap ctf CTF-Face, CTF-LavaGiant, CTF-Orbital

# 6. Enable tiebreaker
.tiebreaker ctf5v5 on

# Done! Mode is ready
```

### Managing Map Pools
```bash
# Add multiple maps at once
.addmap tam DM-Rankin, DM-Deck17, DM-Morpheus

# Check maps and cooldowns
.maps tam

# Remove one map
.removemap tam DM-Rankin

# Clear all maps
.removeallmaps tam

# List all prefixes (find accidental ones)
.listmapprefixes

# Delete accidental prefix
.deletemapprefix invalid-prefix
.confirmdeletemapprefix invalid-prefix
```

### Running a Match
```bash
# Players join
Player1: .j tam
Player2: .j tam
... (8 players total)

# Queue fills → Ready check starts
Everyone clicks ✅

# Autopick balances teams → Match starts
Bot shows: Teams, ELO prediction, Tiebreaker

# Match completes
Player1: .winner red
Player2: .winner red

# Winner declared, ELOs updated
```

---

## 🔧 Troubleshooting

### Queue Issues
**Problem:** Players stuck in queue  
**Solution:** `.reset <mode>`

**Problem:** Ready check timeout not working  
**Solution:** v2.1 fixed this - upgrade

**Problem:** Waiting list not promoting  
**Solution:** v2.1 fixed this - upgrade

### ELO Issues
**Problem:** Wrong ELO shown in .list  
**Solution:** v2.1 fixed this - uses mode-aware ELO

**Problem:** Want different ELO for different team sizes  
**Solution:** Use ELO prefix system

### Map Issues
**Problem:** Accidental prefix created  
**Solution:** Use `.deletemapprefix` + `.confirmdeletemapprefix`

**Problem:** Tiebreaker not showing  
**Solution:** Check `.tiebreaker <mode>`, ensure maps configured

**Problem:** Wrong maps showing  
**Solution:** Check `.permodeelostatus` to see correct prefix

### Migration Issues
**Problem:** Lost data after upgrade  
**Solution:** v2.1 has safe migrations - future upgrades preserve data

**Problem:** Missing column error  
**Solution:** v2.1 auto-migrates all columns

---

## 📊 Version History

### v2.1 (January 2026) - Current
**Major Features:**
- Bulk map adding (comma-separated)
- Per-mode tiebreaker toggle
- Map prefix cleanup commands
- Case-insensitive map operations
- `.listmapprefixes` command

**Fixes:**
- Ready check + waitlist promotion bug
- Autopick mode-aware ELO
- Map removal case sensitivity
- Database migration data preservation
- Missing `tiebreaker_enabled` column

### v2.0 (January 2026)
**Major Features:**
- Mode-specific per-mode ELO
- ELO prefix system
- Database-backed map pools
- Queue timeout fix

**Database Changes:**
- Added `per_mode_elo_enabled` column
- Added `elo_prefix` column
- Added `maps` table
- Added `map_cooldowns` table
- Added `tiebreaker_enabled` column

### v1.0 (Original)
- Basic queue system
- Global ELO
- Manual team selection
- In-memory map pool

---

## 🚀 Getting Started

### Quick Start (5 Minutes)
1. Extract package
2. Install: `pip install -r requirements.txt`
3. Configure bot token in `pug_bot.py`
4. Run: `python pug_bot.py`
5. In Discord: `.addmode tam 8`
6. In Discord: `.autopick tam`
7. Players can now: `.j tam`

### Recommended Setup
1. Create multiple modes (tam, ctf, casual)
2. Enable per-mode ELO for competitive modes
3. Set ELO prefixes to group modes
4. Add map pools per mode
5. Enable tiebreakers for 4v4 modes
6. Configure autopick for all modes
7. Add admin permissions
8. Test with a few players

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Overview and quick start |
| QUICKSTART.md | 5-minute setup guide |
| CHANGELOG.md | Version history |
| COMMANDS.md | Complete command reference |
| ADMIN_GUIDE.md | Admin setup and management |
| PLAYER_GUIDE.md | Player usage guide |
| MAP_POOL_GUIDE.md | Map system guide |
| ELO_PREFIX_GUIDE.md | ELO prefix system guide |
| PER_MODE_ELO_V2_GUIDE.md | Per-mode ELO guide |
| DATABASE_MIGRATION_GUIDE.md | Safe upgrade guide |
| TIEBREAKER_TESTING.md | Tiebreaker testing guide |
| QUEUE_TIMEOUT_FIX.md | Queue timeout explanation |

---

## 💡 Tips & Best Practices

### ELO Management
- Start all players at 1000 ELO
- Use per-mode ELO for competitive modes
- Use ELO prefixes to group similar modes
- Set mode-specific ELOs when needed

### Map Management
- Add 6-10 maps per mode minimum
- Use descriptive mode prefixes
- Check `.listmapprefixes` periodically
- Clean up accidental prefixes promptly

### Queue Management
- Enable autopick for faster matches
- Set reasonable timeout values
- Use waiting list for popular modes
- Reset queues if they get stuck

### Database Management
- Backup database regularly
- Test migrations on copy first
- Read migration guide before upgrading
- Export stats before major changes

---

## 🔒 Safety Features

### Data Protection
- Automatic migration preserves data
- Undo commands for most operations
- Export/backup capabilities
- Confirmation required for destructive actions

### Validation
- Mode name validation
- Player existence checks
- ELO range limits
- Permission verification

### Error Handling
- Graceful error messages
- State recovery mechanisms
- Transaction rollback support
- Debug logging

---

## 🎯 Common Use Cases

### Competitive Community
- Multiple game modes (TAM, CTF, Duel)
- Per-mode ELO for each type
- Tiebreaker maps for competitive modes
- Autopick for fair teams

### Casual Community
- Single mode or few modes
- Global ELO only
- Manual team selection
- No tiebreakers

### Mixed Community
- Competitive modes with per-mode ELO
- Casual modes with global ELO
- Flexible map pools
- Mix of autopick and manual

---

## 📞 Support

**Questions?** Message **fallacy** on Discord

**Bug Reports:** Include:
- Bot version
- Command used
- Error message
- Console output

**Feature Requests:** Describe:
- Use case
- Expected behavior
- Why it's needed

---

## 🎉 Summary

**PUG Pro v2.1** is a full-featured competitive gaming bot with:
- ✅ 100+ commands
- ✅ 3-tier ELO system
- ✅ Database-backed persistence
- ✅ Map pool management
- ✅ Tiebreaker system
- ✅ Queue management
- ✅ Team balancing
- ✅ Statistics tracking
- ✅ Multi-server support
- ✅ Safe migrations
- ✅ 20+ documentation files

**Everything you need for competitive PUGs!**

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
**Version:** 2.1  
**Date:** January 2026

**Questions? Message fallacy on Discord!**
