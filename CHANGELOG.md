# Changelog

A customizable version of the TAM Pro Bot
Originally developed for the UT2004 Unreal Fight Club Discord Community


**PUG Pro Discord Bot**  
**Version:** 2.0  
**Developed by:** fallacy

---

## Version 2.0 (January 2026)

### Major Features

**Mode-Specific Per-Mode ELO:**
- Per-mode ELO can now be enabled for individual modes instead of all-or-nothing
- Enables mixed competitive/casual setups (e.g., TAM has per-mode ELO, casual uses global)
- More flexible and realistic for diverse gaming communities

**Queue Timeout Fix:**
- Queue timeout now resets every time a player joins (not just first player)
- Ensures fair treatment of recent joiners
- Queue only clears after true 4-hour inactivity

### New Commands
- `.permodeelo <mode>` - Toggle per-mode ELO for specific mode
- `.permodelostatus` - Show which modes have per-mode ELO enabled
- `.setmodeelo <mode> <player> <elo>` - Set mode-specific ELO
- `.pugproon` - Alias for `.tamproon` (enable bot)
- `.pugprooff` - Alias for `.tamprooff` (disable bot)

### Removed Commands
- `.permodeelon` - Replaced by `.permodeelo <mode>`
- `.permodeeloff` - Replaced by `.permodeelo <mode>`

### Database Changes
- Added `per_mode_elo_enabled` column to `game_modes` table
- Automatic migration for existing databases

### Bug Fixes
- Fixed queue timeout to reset on every player join
- Queue now only clears after 4 hours of no new joins

### Documentation
- Added PER_MODE_ELO_V2_GUIDE.md - Complete guide to mode-specific per-mode ELO
- Added QUEUE_TIMEOUT_FIX.md - Explanation of queue timeout behavior
- Updated COMMANDS.md with v2.0 commands
- Updated all documentation to version 2.0

---

## Version 1.0 (January 2026)

### Initial Release

**Core Features:**
- Queue management with ready checks
- Captain picking and autopick team balancing
- ELO rating system with automatic updates
- Complete statistics tracking
- Multiple game mode support
- Voting system for match results
- Real-time leaderboard updates

**Player Commands:**
- `.register` - Player registration
- `.j` / `++` - Queue joining
- `.l` - Queue leaving
- `.winner` - Match result voting
- `.splitwin` - BO3 split results
- `.deadpug` - Cancel match voting
- Stats commands (`.mystats`, `.topelo`, etc.)

**Admin Commands:**
- ELO management (`.setelo`, `.importelos`)
- PUG control (`.setwinner`, `.undowinner`, `.forcedeadpug`)
- Queue management (`.reset`, `.add`, `.remove`)
- Mode management (`.addmode`, `.autopick`)
- Data export/import

**Key Features:**
- Auto-updating leaderboard on bot startup
- 10-minute ready status persistence
- Automatic team balancing by ELO
- CSV import/export for bulk operations
- Win percentage calculation fix
- Split win support for incomplete BO3s
- Map cooldown system
- 4-hour queue inactivity timeout
- Waiting list with auto-promotion

**Bug Fixes:**
- Fixed ready check not restarting after timeout
- Fixed "already in queue" detection
- Fixed double ELO application on admin override
- Fixed leaderboard not updating
- Fixed win % calculation to use wins+losses

---

## Future Improvements

Potential features for future versions:
- Web dashboard
- Advanced statistics and analytics
- Tournament bracket system
- Custom ELO formulas per mode
- Player achievements/badges
- Match replay system
- Discord voice channel integration

---

**Questions or suggestions?** Message **fallacy** on Discord.

---

*Bot made for Competitive Gaming Communities to use for Pick Up Games (PUGs)*
