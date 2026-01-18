# Scraper Configuration Guide

**PUG Pro Bot - External Stats Integration**

A customizable version of the TAM Pro Bot  
Originally developed for the UT2004 Unreal Fight Club Discord Community

**Developed by:** fallacy  
**Any questions? Please message fallacy on Discord.**

---

## Overview

The PUG Pro Bot includes optional integration with external game stat tracking websites. This allows players to link their in-game accounts and display stats from services like tracker.gg, op.gg, or custom stats sites.

**This feature is completely optional!** If your game doesn't have external stats tracking, you can ignore this file.

---

## Quick Start

### Option 1: Disable Stats Integration (Recommended for most users)

If you don't need external stats, do nothing! The bot works perfectly without it.

Players will see:
```
Player: .linkstats MyGameName
Bot: Stat scraping is currently disabled
```

---

### Option 2: Enable Stats Integration

If your game has a stats tracking website, follow these steps:

#### 1. Edit scraper.py

Find the configuration section (around line 50):

```python
# Base URL of the stats website
BASE_URL = "https://your-stats-website.com"

# Search URL format
SEARCH_URL = f"{BASE_URL}/search"
```

Change to your game's stats website:

```python
BASE_URL = "https://tracker.gg/valorant"
SEARCH_URL = f"{BASE_URL}/profile/search"
```

#### 2. Customize the Parser

Update the `_parse_html_stats()` or `_parse_json_stats()` method to extract stats from your website.

See examples below for different games.

#### 3. Test the Scraper

Run the scraper directly to test:

```bash
python scraper.py
```

Enter a player name and verify stats are retrieved correctly.

#### 4. Enable in Bot

In your database, enable scraping:

```sql
UPDATE bot_settings SET value='true' WHERE key='scraping_enabled';
```

Or use a database browser to change the value.

---

## Supported Stat Websites

### Popular Options

**Tracker Network (tracker.gg)**
- Apex Legends
- Valorant
- Fortnite
- Call of Duty
- Destiny 2

**Game-Specific Sites**
- op.gg (League of Legends)
- r6.tracker.network (Rainbow Six Siege)  
- fortnitetracker.com (Fortnite)
- destinytracker.com (Destiny 2)
- stats.ut2k4.com (UT2004)

**Custom Stats Sites**
- Your own game's stats API
- Community-run stat trackers

---

## Configuration Examples

### Example 1: Valorant (tracker.gg)

```python
class GameStatsScraper:
    BASE_URL = "https://tracker.gg/valorant"
    SEARCH_URL = f"{BASE_URL}/profile/riot"
    
    async def search_player(self, player_name: str) -> Optional[Dict]:
        await self.init_session()
        
        try:
            # Valorant uses riot ID format: Name%23Tag
            player_name = player_name.replace('#', '%23')
            url = f"{self.SEARCH_URL}/{player_name}/overview"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract stats from HTML
                kills_elem = soup.find('span', {'data-stat': 'kills'})
                deaths_elem = soup.find('span', {'data-stat': 'deaths'})
                
                if not kills_elem or not deaths_elem:
                    return None
                
                kills = int(kills_elem.text.replace(',', ''))
                deaths = int(deaths_elem.text.replace(',', ''))
                
                return {
                    'kills': kills,
                    'deaths': deaths,
                    'suicides': 0,
                    'efficiency': (kills / max(deaths, 1)) * 100,
                    'matches_played': 0,
                    'time_played': 'N/A',
                    'favorite_weapon': 'N/A'
                }
        except Exception as e:
            print(f"Error: {e}")
            return None
```

### Example 2: League of Legends (op.gg)

```python
class GameStatsScraper:
    BASE_URL = "https://www.op.gg"
    SEARCH_URL = f"{BASE_URL}/summoners"
    
    async def search_player(self, player_name: str) -> Optional[Dict]:
        await self.init_session()
        
        try:
            # op.gg uses region-based URLs
            url = f"{self.SEARCH_URL}/na/{player_name}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract stats
                stats_div = soup.find('div', {'class': 'stats'})
                if not stats_div:
                    return None
                
                kills = int(stats_div.find('span', {'class': 'kills'}).text)
                deaths = int(stats_div.find('span', {'class': 'deaths'}).text)
                
                return {
                    'kills': kills,
                    'deaths': deaths,
                    'suicides': 0,
                    'efficiency': (kills / max(deaths, 1)) * 100,
                    'matches_played': 0,
                    'time_played': 'N/A',
                    'favorite_weapon': 'N/A'
                }
        except Exception as e:
            print(f"Error: {e}")
            return None
```

### Example 3: JSON API

If your stats site provides a JSON API:

```python
async def search_player(self, player_name: str) -> Optional[Dict]:
    await self.init_session()
    
    try:
        url = f"{self.BASE_URL}/api/players/{player_name}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                return None
            
            data = await response.json()
            
            return {
                'kills': data['stats']['kills'],
                'deaths': data['stats']['deaths'],
                'suicides': data['stats'].get('suicides', 0),
                'efficiency': data['stats']['kd_ratio'] * 100,
                'matches_played': data['stats']['matches'],
                'time_played': data['stats']['playtime'],
                'favorite_weapon': data['stats']['top_weapon']
            }
    except Exception as e:
        print(f"Error: {e}")
        return None
```

---

## Required Stats Format

Your scraper must return a dictionary with these keys:

```python
{
    'kills': int,              # Total kills
    'deaths': int,             # Total deaths
    'suicides': int,           # Suicides (or 0 if not applicable)
    'efficiency': float,       # K/D ratio as percentage
    'matches_played': int,     # Total matches
    'time_played': str,        # Formatted time string (e.g., "123h 45m")
    'favorite_weapon': str     # Most used weapon/character
}
```

**If a stat isn't available**, use sensible defaults:
- Numbers: `0`
- Percentages: `0.0`
- Strings: `'N/A'` or `'Unknown'`

---

## Testing Your Scraper

### 1. Test from Command Line

```bash
python scraper.py
```

Enter a known player name and verify output.

### 2. Test in Discord

```
Player: .linkstats TestPlayer
Bot: [Should link account]

Player: .gamestats
Bot: [Should display stats]
```

### 3. Check Console

Watch for error messages:
```
Error scraping stats for TestPlayer: ...
```

Common issues:
- Wrong URL format
- Incorrect HTML selectors
- Missing authentication
- Rate limiting

---

## Troubleshooting

### Stats Not Found

**Problem:** Bot can't find player stats

**Solutions:**
1. Verify player name is correct
2. Check BASE_URL is correct
3. Test URL in browser manually
4. Check website hasn't changed HTML structure

### HTML Parsing Errors

**Problem:** Can't extract stats from HTML

**Solutions:**
1. Inspect website HTML in browser
2. Update CSS selectors in `_parse_html_stats()`
3. Check for JavaScript-rendered content (may need different approach)

### Rate Limiting

**Problem:** Website blocks requests

**Solutions:**
1. Add delays between requests
2. Use API key if available
3. Add User-Agent header
4. Consider caching results

### Authentication Required

**Problem:** Website requires login

**Solutions:**
1. Get API key from website
2. Add authentication headers
3. Use OAuth if supported
4. Contact website for API access

---

## Advanced Configuration

### Adding API Key

```python
class GameStatsScraper:
    API_KEY = "your-api-key-here"
    
    async def search_player(self, player_name: str) -> Optional[Dict]:
        await self.init_session()
        
        headers = {
            'Authorization': f'Bearer {self.API_KEY}',
            'User-Agent': 'PUGProBot/1.0'
        }
        
        async with self.session.get(url, headers=headers) as response:
            # ...
```

### Adding Rate Limiting

```python
from datetime import datetime, timedelta

class GameStatsScraper:
    def __init__(self):
        self.session = None
        self.last_request = None
        self.min_delay = 1.0  # seconds
    
    async def search_player(self, player_name: str) -> Optional[Dict]:
        # Rate limit check
        if self.last_request:
            elapsed = (datetime.now() - self.last_request).total_seconds()
            if elapsed < self.min_delay:
                await asyncio.sleep(self.min_delay - elapsed)
        
        self.last_request = datetime.now()
        
        # Continue with request...
```

### Caching Results

```python
class GameStatsScraper:
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    async def search_player(self, player_name: str) -> Optional[Dict]:
        # Check cache
        cache_key = player_name.lower()
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.cache_duration:
                return cached_data
        
        # Fetch and cache...
        stats = await self._fetch_stats(player_name)
        if stats:
            self.cache[cache_key] = (stats, datetime.now())
        return stats
```

---

## Disabling Stats Integration

If you decide not to use external stats:

1. Leave scraper.py as-is (already disabled by default)
2. Don't enable scraping in database
3. Bot will work normally without this feature

Players will see:
```
Player: .linkstats Name
Bot: Stat scraping is currently disabled
```

---

## Bot Commands

When scraping is enabled, players can use:

```
.linkstats <playername>     - Link in-game account
.gamestats [@user]          - View stats
.scrapestatus (admin)       - Check if enabled
```

---

## Need Help?

**Having trouble configuring the scraper?**

1. Check console for error messages
2. Test scraper directly: `python scraper.py`
3. Verify website URL is correct
4. Message **fallacy** on Discord

**Don't need stats integration?**

Just ignore this file! The bot works great without it.

---

## Summary

**Optional Feature:**
- Integrates with external stats websites
- Completely optional - bot works without it
- Requires customization for your game

**To Use:**
1. Edit scraper.py (BASE_URL, parsing logic)
2. Test with `python scraper.py`
3. Enable in database
4. Players use `.linkstats` and `.gamestats`

**To Skip:**
- Leave scraper.py as-is
- Don't enable in database
- Bot works normally

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*A customizable version of the TAM Pro Bot*  
*Originally developed for the UT2004 Unreal Fight Club Discord Community*

**Questions?** Message **fallacy** on Discord!
