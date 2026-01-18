# PUG Pro Discord Bot

A customizable version of the TAM Pro Bot
Originally developed for the UT2004 Unreal Fight Club Discord Community


**Version:** 2.1.0  
**Developed by:** fallacy  
**For:** Competitive Gaming Communities  

*Bot made for Competitive Gaming Communities to use for Pick Up Games (PUGs)*

**Any questions? Please message fallacy on Discord.**

---

## 📋 Overview

PUG Pro Bot is a comprehensive PUG (Pick Up Game) management system for Discord. It handles everything from queue management and team picking to ELO ratings and statistics tracking. The bot automatically organizes matches, balances teams, and tracks competitive performance over time.

## ✨ Key Features

- **Queue Management** - Automated player queuing with ready checks
- **Team Selection** - Captain picking or automatic team balancing
- **ELO Rating System** - Track player skill with competitive rankings
- **Statistics Tracking** - Complete match history and player stats
- **Multiple Game Modes** - Support for different team sizes and formats
- **Auto-Updates** - Real-time leaderboard updates after every match
- **Vote System** - Democratic winner declaration with safeguards
- **Admin Controls** - Comprehensive management tools

## 🚀 Quick Start

1. **Prerequisites**
   - Python 3.8 or higher
   - Discord Bot Token
   - Discord Server with appropriate permissions

2. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Edit `pug_bot.py` and add your Discord bot token
   - Set `ALLOWED_CHANNEL_NAME` to your PUG channel name

4. **Run the Bot**
   ```bash
   python pug_bot.py
   ```

5. **Initial Setup**
   - Create `#tampro` channel (or your configured channel)
   - Create `#leaderboard` channel (optional but recommended)
   - Run `.register` to create your first player
   - Bot auto-creates leaderboard on startup

For detailed installation instructions, see **INSTALL.md**.

## 📚 Documentation

- **[Installation Guide](INSTALL.md)** - Step-by-step setup instructions
- **[Player Guide](PLAYER_GUIDE.md)** - How to use the bot as a player
- **[Admin Guide](ADMIN_GUIDE.md)** - Server setup and management
- **[Command Reference](COMMANDS.md)** - Complete command list
- **[ELO System](ELO_EXPLAINED.md)** - Understanding the rating system
- **[Troubleshooting](TROUBLESHOOTING.md)** - Fixing common issues

## 🎮 Core Workflow

1. **Queue Phase** - Players join with `.j` or `++`
2. **Ready Check** - All players click ✅ (90 seconds)
3. **Team Selection** - Captains pick or auto-balance
4. **Match Play** - Join server and compete
5. **Report Results** - Vote for winner with `.winner red/blue`
6. **ELO Update** - Automatic rating adjustments

## 🏆 Popular Commands

### Players
```
.register        - Register for PUG tracking
.j competitive          - Join default 4v4 mode
++               - Quick join all active queues
.l               - Leave all queues
.mystats         - View your statistics
.topelo          - See top 10 ELO rankings
.winner red      - Vote for red team victory
```

### Admins
```
.setelo @user 1200    - Set player ELO
.reset competitive           - Reset queue
.setwinner 147 red    - Override PUG result
.exportstats          - Export player data
```

## ⚙️ Configuration Options

Edit these constants in `pug_bot.py`:

```python
ALLOWED_CHANNEL_NAME = 'tampro'     # PUG command channel
BOT_TOKEN = 'your-token-here'       # Discord bot token
```

## 🆘 Support

**Having issues?** Check these resources:

1. **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common problems and solutions
2. **[Admin Guide](ADMIN_GUIDE.md)** - Setup and configuration help
3. **Discord** - Message **fallacy** on Discord for support


## 📜 License

MIT License - See LICENSE.txt for details

## 🙏 Credits

**Developer:** fallacy  
**Purpose:** Competitive Gaming Communities  
**For:** Pick Up Game (PUG) Management  

*Bot made for Competitive Gaming Communities to use for Pick Up Games (PUGs)*

---

**Ready to get started?** Head to **[INSTALL.md](INSTALL.md)** for installation instructions!

