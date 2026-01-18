# Database Migration Guide

**PUG Pro Discord Bot**  
**Version:** 2.0  
**Developed by:** fallacy

---

## Overview

This guide explains how to migrate your existing PUG Pro Bot database to newer versions **without losing any data**.

---

## Important: Data Preservation

### ✅ Version 2.0+ Migrations Are Safe!

Starting with version 2.0, all database migrations are **non-destructive**:
- ✅ All player ELOs are preserved
- ✅ All player statistics are preserved
- ✅ All PUG history is preserved
- ✅ All admin permissions are preserved
- ✅ All game modes are preserved

**Old behavior (v1.0):** Migrations dropped tables and wiped data ❌  
**New behavior (v2.0+):** Migrations preserve all existing data ✅

---

## Migration Process

### Automatic Migration

When you upgrade to a new version:

1. **Backup your database** (recommended but not required)
2. **Extract new version**
3. **Replace bot files**
4. **Run the bot**
5. **Database auto-migrates** on startup

That's it! The bot handles everything automatically.

---

## Step-by-Step: Upgrading to v2.0

### Step 1: Backup Current Database (Recommended)

```bash
# Navigate to your bot directory
cd /path/to/your/bot

# Create backup
cp pug_data.db pug_data.db.backup_$(date +%Y%m%d)

# Example: Creates pug_data.db.backup_20260118
```

**Why backup?**
- Safety net in case of unexpected issues
- Allows rollback if needed
- Good practice for any database changes

### Step 2: Extract New Version

```bash
# Extract v2.0 package
tar -xzf PUGPro-Bot-Complete.tar.gz

# Navigate to extracted files
cd PUGPro-Bot-Release
```

### Step 3: Replace Bot Files

**Option A: In-place upgrade**
```bash
# Stop the bot first (Ctrl+C or Discord command)

# Backup old files
mv pug_bot.py pug_bot.py.old
mv database.py database.py.old

# Copy new files
cp /path/to/extracted/pug_bot.py .
cp /path/to/extracted/database.py .

# Keep your existing:
# - pug_data.db (your database)
# - Any custom configuration
```

**Option B: Fresh install with database copy**
```bash
# Copy your database to new installation
cp /path/to/old/bot/pug_data.db /path/to/new/bot/

# Configure new bot (BOT_TOKEN, etc.)
```

### Step 4: Run the Bot

```bash
python pug_bot.py
```

### Step 5: Watch Migration Messages

You'll see messages like:
```
⚠️  Migrating players table to add server_id...
   This migration PRESERVES all existing player data!
   Found 47 players to migrate...
   Migrating player data with server_id='default'...
✅ Players table migrated successfully!
   47 players migrated with server_id='default'
   All ELOs, stats, and player data PRESERVED!

⚠️  Migrating pug_admins table to add server_id...
   Found 3 admins to migrate...
   Migrating admins with server_id='default'...
✅ Database migration: Added 'server_id' to pug_admins table
   3 admins migrated with server_id='default'
   All admin permissions PRESERVED!

✅ Database migration: Added 'per_mode_elo_enabled' column to game_modes table
```

### Step 6: Verify Data

Check that your data migrated correctly:

**In Discord:**
```
.mystats              # Check your stats are intact
.topelo               # Check leaderboard has all players
.last                 # Check PUG history exists
```

**All your data should be there!**

---

## What Gets Migrated

### Players Table
**Before migration:**
```
discord_id | wins | losses | total_pugs | elo | ...
```

**After migration:**
```
discord_id | server_id | wins | losses | total_pugs | elo | ...
"123..."   | "default" | 45   | 30     | 75         | 1456| ...
```

**Result:** All player data preserved with `server_id='default'`

### PUG Admins Table
**Before migration:**
```
discord_id
"123..."
"456..."
```

**After migration:**
```
discord_id | server_id
"123..."   | "default"
"456..."   | "default"
```

**Result:** All admins preserved with `server_id='default'`

### Game Modes Table
**Before migration:**
```
mode_name | display_name | team_size | description
"tam"     | "TAM"        | 8         | null
```

**After migration:**
```
mode_name | display_name | team_size | description | per_mode_elo_enabled
"tam"     | "TAM"        | 8         | null        | 0
```

**Result:** All modes preserved, per-mode ELO disabled by default

### Other Tables
These tables get new columns added automatically:
- `pugs` - Gets `status` and `tiebreaker_map` columns
- `players` - Gets additional stat tracking columns
- `player_mode_elos` - New table created (empty initially)

**All existing data in these tables is preserved.**

---

## Understanding server_id='default'

### What is server_id?

`server_id` allows the bot to work across multiple Discord servers with separate databases per server.

### Why 'default'?

When migrating from v1.0 (which didn't have server_id), all existing data is assigned `server_id='default'`.

### Does this affect anything?

**If you run on ONE Discord server:** No impact at all. Everything works normally.

**If you run on MULTIPLE Discord servers:** Each server will have its own data going forward, but migrated data uses 'default'.

### Can I change server_id?

Yes, but it's advanced. Generally not needed unless you're managing multiple servers.

---

## Migration Scenarios

### Scenario 1: Single Server Bot (Most Common)

**Before:**
- Bot running on one Discord server
- 50 players, 200 PUGs, 5 admins

**Migration:**
```
✅ All 50 players migrated → server_id='default'
✅ All 200 PUGs preserved
✅ All 5 admins migrated → server_id='default'
✅ All game modes preserved
```

**Result:** Everything works exactly as before. No data loss.

### Scenario 2: Multi-Server Bot

**Before:**
- Bot running on 3 Discord servers
- All data mixed in one database (v1.0 didn't separate)

**Migration:**
```
✅ All players migrated → server_id='default'
✅ All PUGs preserved
✅ All admins migrated → server_id='default'
```

**Going forward:**
- New players on each server get that server's ID
- Migrated 'default' data is accessible from all servers
- Can manually update server_ids if needed for separation

### Scenario 3: Fresh v2.0 Install

**Before:**
- No existing database

**Migration:**
```
✅ New database created
✅ No migration needed
✅ All data uses actual server_id from start
```

**Result:** Clean start, no 'default' server_id used.

---

## Rollback Procedure

If you need to roll back to v1.0 after upgrading:

### Step 1: Stop the Bot
```bash
# Stop v2.0 bot
```

### Step 2: Restore Backup
```bash
# Remove migrated database
rm pug_data.db

# Restore backup
cp pug_data.db.backup_20260118 pug_data.db
```

### Step 3: Restore Old Bot Files
```bash
# Restore old bot version
mv pug_bot.py.old pug_bot.py
mv database.py.old database.py
```

### Step 4: Run Old Version
```bash
python pug_bot.py
```

**Result:** Back to v1.0 with original data intact.

---

## Troubleshooting

### "Old player data cleared"

**Problem:** You see this message from an old version.

**Solution:** You're using old migration code. Re-download v2.0 which has safe migrations.

### "Previous PUG admins were cleared"

**Problem:** You see this message from an old version.

**Solution:** You're using old migration code. Re-download v2.0 which preserves admins.

### Migration seems stuck

**Problem:** Bot doesn't proceed after migration messages.

**Solution:** 
1. Check for errors in console
2. Verify database file isn't corrupted
3. Check file permissions

### Data looks wrong after migration

**Problem:** Stats or ELOs don't match expected values.

**Solution:**
1. Stop the bot
2. Restore from backup: `cp pug_data.db.backup pug_data.db`
3. Try migration again
4. If still issues, contact support

### Want to start fresh instead of migrate

**Option 1: Rename old database**
```bash
mv pug_data.db pug_data.db.old
# Bot will create new empty database
```

**Option 2: Delete old database**
```bash
rm pug_data.db
# Bot will create new empty database
```

**Warning:** This loses ALL data. Only do if you're sure!

---

## Best Practices

### Always Backup
```bash
# Before any upgrade
cp pug_data.db pug_data.db.backup_$(date +%Y%m%d)
```

### Test First
If you're nervous about migration:
1. Copy database to test environment
2. Run migration on copy first
3. Verify data looks good
4. Then do real migration

### Keep Backups
```bash
# Keep dated backups
pug_data.db.backup_20260115
pug_data.db.backup_20260118
pug_data.db.backup_20260125
```

### Document Your Setup
Keep notes on:
- What version you're running
- When you last upgraded
- Any custom modifications
- Server configurations

---

## FAQ

**Q: Will my ELOs be preserved?**  
A: YES! v2.0+ migrations preserve all ELOs.

**Q: Will my PUG history be preserved?**  
A: YES! All PUG records are preserved.

**Q: Will my admin permissions be preserved?**  
A: YES! All admins are migrated.

**Q: What if I have multiple servers?**  
A: Migrated data gets server_id='default'. New data uses actual server_id.

**Q: Can I roll back if something goes wrong?**  
A: YES! Restore from backup and use old bot files.

**Q: Do I need to do anything manually?**  
A: NO! Migrations are automatic. Just backup and run.

**Q: What if migration fails?**  
A: Restore from backup and try again, or contact support.

**Q: Will this work for future versions?**  
A: YES! All future versions will use safe migrations.

**Q: Is there downtime?**  
A: Brief - just the time to stop old bot and start new one (usually <1 minute).

**Q: What about custom modifications?**  
A: Migrations preserve data. Custom code may need updating separately.

---

## Migration Checklist

### Pre-Migration
- [ ] Backup database: `cp pug_data.db pug_data.db.backup`
- [ ] Note current version
- [ ] Document current player count, ELOs, etc.
- [ ] Stop the bot

### During Migration
- [ ] Extract new version
- [ ] Copy/replace bot files
- [ ] Keep existing database file
- [ ] Start bot
- [ ] Watch console for migration messages

### Post-Migration
- [ ] Verify player data: `.mystats`, `.topelo`
- [ ] Verify PUG history: `.last`
- [ ] Verify admins: Check who can run admin commands
- [ ] Test basic functionality: Join queue, check stats
- [ ] Confirm everything works

### If Issues
- [ ] Stop bot
- [ ] Restore backup
- [ ] Try again or contact support

---

## Support

**Issues with migration?**
1. Check console output for error messages
2. Verify backup exists
3. Read troubleshooting section above
4. Contact: **fallacy** on Discord

**Common Questions:**
- "Will my data be safe?" → YES, if using v2.0+
- "Do I need to backup?" → Recommended but not required
- "Is migration automatic?" → YES
- "Can I roll back?" → YES, from backup

---

## Summary

### v2.0+ Migration is Safe! ✅

**What's preserved:**
- ✅ All player ELOs
- ✅ All player statistics
- ✅ All PUG history
- ✅ All admin permissions
- ✅ All game modes
- ✅ All settings

**What changes:**
- ✅ New columns added to existing tables
- ✅ New tables created for new features
- ✅ server_id='default' assigned to migrated data

**Best practice:**
```bash
# 1. Backup
cp pug_data.db pug_data.db.backup

# 2. Upgrade files
# 3. Run bot
# 4. Verify data

Done! ✅
```

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*Safe database migrations since v2.0*

**Questions?** Message **fallacy** on Discord!
