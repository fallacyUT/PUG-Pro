# What's New in This Release

A customizable version of the TAM Pro Bot
Originally developed for the UT2004 Unreal Fight Club Discord Community


**PUG Pro Discord Bot - Generic Version**
**Developed by:** fallacy
**For:** Competitive Gaming Communities

---

## Major Changes

### ✅ Removed Game-Specific Content

**Before:**
- Hardcoded UT2004 maps
- competitive mode references everywhere
- Default 4v4 mode auto-created

**After:**
- Empty map pool (admins configure)
- Generic mode references
- No default modes (admins create)
- Works with ANY competitive game!

---

## What Was Removed

### 1. Hardcoded Map Pool
**Before:**
```python
MAP_POOL = [
    "Ages", "Elucidation", "Entropic", "Invictus",
    "OSR-Cheops", "PeerToPeer", "Pending", ...
]
```

**After:**
```python
MAP_POOL = []  # Empty - configure for your game
```

### 2. Default Game Mode
**Before:**
- Auto-created "competitive" 4v4 mode
- Hardcoded in database initialization

**After:**
- No default modes
- Admins create modes with `.addmode`
- Fully customizable

### 3. Game-Specific References
**Before:**
- "Use `.j competitive` to join"
- "UT2004 community"
- "Developed by Nick"

**After:**
- "Use `.j <mode>` to join"
- "Competitive Gaming Communities"
- "Developed by fallacy"

---

## New Features

### 1. Customization Section
Added clear customization section at top of `pug_bot.py`:
```python
# ============================================================================
# CUSTOMIZATION SECTION - Configure these for your game/community
# ============================================================================

# Channel where PUG commands work
ALLOWED_CHANNEL_NAME = "tampro"  # Change to your channel

# Your Discord Bot Token
BOT_TOKEN = "your-bot-token-here"  # Add your token here
```

### 2. CUSTOMIZATION.md Guide
Complete guide for adapting bot to any game:
- Counter-Strike / Valorant examples
- League of Legends / DOTA examples
- Rocket League examples
- Battle Royale examples
- Custom game examples

### 3. Improved Startup
Bot now checks configuration and shows helpful errors:
```
❌ ERROR: Bot token not configured!
Please edit pug_bot.py and set your Discord bot token:
  1. Find the line: BOT_TOKEN = "your-bot-token-here"
  2. Replace with:  BOT_TOKEN = "paste-your-actual-token-here"
```

---

## How to Configure for Your Game

### Step 1: Edit pug_bot.py

```python
# Set your bot token
BOT_TOKEN = "your-actual-token-here"

# Set your channel name
ALLOWED_CHANNEL_NAME = "pugs"  # or whatever you want

# (Optional) Add your game's maps
MAP_POOL = ["Map1", "Map2", "Map3"]  # or leave empty
```

### Step 2: Start Bot

```bash
python pug_bot.py
```

### Step 3: Create Game Modes

```
Admin: .addmode 5v5 10       # For 5v5 games
Admin: .addmode 2v2 4        # For 2v2 games
Admin: .autopick 5v5         # Enable auto-balance
```

### Step 4: Add Maps (Optional)

```
Admin: .addmap Dust2
Admin: .addmap Mirage
Admin: .showmaps
```

---

## Package Contents

```
PUGPro-Bot-Complete.tar.gz contains:

Documentation:
├── README.md               - Overview
├── QUICKSTART.md          - 5-minute setup
├── CUSTOMIZATION.md       - Configure for your game (NEW!)
├── INSTALL.md             - Detailed installation
├── PLAYER_GUIDE.md        - Player commands
├── ADMIN_GUIDE.md         - Admin management
├── COMMANDS.md            - Complete command list
├── ELO_EXPLAINED.md       - ELO system guide
├── TROUBLESHOOTING.md     - Fix common issues
├── CHANGELOG.md           - Version history
└── LICENSE.txt            - MIT License

Code:
├── pug_bot.py             - Main bot (configured for generic use)
├── database.py            - Database manager
└── requirements.txt       - Python dependencies
```

---

## Supported Games

This bot now works with **ANY** competitive game:

### FPS Games
- Counter-Strike
- Valorant
- Call of Duty
- Apex Legends
- Overwatch
- Rainbow Six Siege

### MOBA Games
- League of Legends
- DOTA 2
- Heroes of the Storm
- Smite

### Sports Games
- Rocket League
- FIFA
- NBA 2K

### Fighting Games
- Street Fighter
- Tekken
- Smash Bros

### Battle Royale
- Fortnite
- PUBG
- Apex Legends

### And More!
- Custom games
- Indie games
- Any competitive format

---

## Credits

**Original Development:** fallacy
**Purpose:** Competitive Gaming Communities
**License:** MIT

*Bot made for Competitive Gaming Communities to use for Pick Up Games (PUGs)*

**Any questions? Please message fallacy on Discord.**

---

## Quick Start

1. **Extract** package
2. **Edit** pug_bot.py (set BOT_TOKEN and ALLOWED_CHANNEL_NAME)
3. **Run** `python pug_bot.py`
4. **Configure** modes with `.addmode` in Discord
5. **Play PUGs!** 🎮

**Full guide:** See CUSTOMIZATION.md

---

**Download:** PUGPro-Bot-Complete.tar.gz

**Ready to use with your game!**
