# Feature Update: Ready Check Message Reposting & Captain Display

## Feature 1: Ready Check Message Deletion and Reposting

### Problem
When a ready check failed (due to timeout, manual cancellation, or player leaving), the old ready check message would remain in chat. As new messages were posted, players had to scroll up to find the ready check message when the queue refilled. This created a poor user experience, especially in busy channels.

### Solution
The bot now deletes the old ready check message whenever a ready check is cancelled for any reason. When the queue refills and triggers a new ready check, a fresh message is posted at the bottom of the chat where players can easily see it.

### Implementation Details

**Three scenarios where ready check messages are now deleted:**

#### 1. Player Manually Leaves During Ready Check
**File**: `pug_bot.py`, function `remove_player()` (lines 337-362)

When a player uses `.leave` or is removed during a ready check, if this causes the queue to drop below full:
```python
# Delete the old ready check message so it can be reposted when queue refills
if self.ready_check_message:
    try:
        await self.ready_check_message.delete()
    except:
        pass
    self.ready_check_message = None
```

#### 2. Player Declines Ready Check (❌ Reaction)
**File**: `pug_bot.py`, reaction handler (lines 1817-1842)

When a player clicks ❌ to decline and the queue becomes non-full:
```python
# Delete the old ready check message so it can be reposted when queue refills
if queue.ready_check_message:
    try:
        await queue.ready_check_message.delete()
    except:
        pass
    queue.ready_check_message = None
```

#### 3. Ready Check Times Out and Queue Doesn't Refill
**File**: `pug_bot.py`, function `wait_for_ready_check()` (lines 650-664)

When players fail to ready up in time and promotions from waiting list don't fill the queue:
```python
# Delete the old ready check message so it can be reposted when queue refills
if self.ready_check_message:
    try:
        await self.ready_check_message.delete()
    except:
        pass
    self.ready_check_message = None
```

### User Experience Improvements

**Before:**
1. Queue fills (8/8) → Ready check posted at message #100
2. Player leaves → Queue becomes 7/8
3. New chat messages push to #105, #106, #107...
4. Queue refills (8/8) → Old ready check at #100 is updated
5. Players must scroll up to find it

**After:**
1. Queue fills (8/8) → Ready check posted at message #100
2. Player leaves → Queue becomes 7/8, message #100 is **deleted**
3. New chat messages continue normally
4. Queue refills (8/8) → **New** ready check posted at current message (e.g., #107)
5. Players can see it immediately without scrolling

### Benefits
- ✅ Ready check always visible at bottom of chat
- ✅ No scrolling required to find active ready check
- ✅ Cleaner chat history (removes stale ready check messages)
- ✅ Better mobile experience (small screens benefit from less scrolling)
- ✅ Preserves ready status when queue refills (players who already readied stay ready)

---

## Feature 2: Captain Display in `.last` Commands

### Problem
When viewing past PUGs using `.last`, `.mylast`, `.lastt`, or `.lasttt` commands, there was no indication of who the captains were. Players couldn't tell who had captain responsibilities in each game.

### Solution
The bot now displays a crown emoji (👑) next to captain names in the team lists when viewing past PUGs.

### Implementation Details

#### Database Changes

**File**: `database.py`

**1. Table Schema Migration** (lines 236-250)
Added two new columns to the `pugs` table:
```python
# Migration: Add captain columns if they don't exist
try:
    cursor.execute("SELECT red_captain FROM pugs LIMIT 1")
except:
    cursor.execute("ALTER TABLE pugs ADD COLUMN red_captain TEXT")
    conn.commit()
    print("✅ Database migration: Added 'red_captain' column to pugs table")

try:
    cursor.execute("SELECT blue_captain FROM pugs LIMIT 1")
except:
    cursor.execute("ALTER TABLE pugs ADD COLUMN blue_captain TEXT")
    conn.commit()
    print("✅ Database migration: Added 'blue_captain' column to pugs table")
```

**2. Updated `add_pug()` Function** (lines 806-822)
- Added `red_captain` and `blue_captain` parameters
- Stores captain Discord IDs when creating PUG records

**3. Updated `get_recent_pugs()` Function** (lines 867-921)
- Retrieves captain data from database
- Includes captain IDs in returned PUG dictionaries

#### Bot Changes

**File**: `pug_bot.py`

**1. Save Captain Data** (lines 1241-1250)
When a PUG finishes, captain information is now saved:
```python
pug_number = db_manager.add_pug(
    red_team=self.red_team,
    blue_team=self.blue_team,
    game_mode=self.game_mode_name,
    avg_red_elo=avg_red_elo,
    avg_blue_elo=avg_blue_elo,
    tiebreaker_map=self.selected_tiebreaker if self.team_size == 8 else None,
    red_captain=self.red_captain,
    blue_captain=self.blue_captain
)
```

**2. Display Captain Emoji** (lines 4583-4660)

Red team display:
```python
# Add captain emoji if this player is the red captain
if pug.get('red_captain') and str(uid) == str(pug['red_captain']):
    name = f"👑 {name}"
```

Blue team display:
```python
# Add captain emoji if this player is the blue captain
if pug.get('blue_captain') and str(uid) == str(pug['blue_captain']):
    name = f"👑 {name}"
```

### Example Output

**Before:**
```
PUG #1234
🔴 Red Team: Player1, Player2, Player3, Player4
🔵 Blue Team: Player5, Player6, Player7, Player8
```

**After:**
```
PUG #1234
🔴 Red Team: 👑 Player1, Player2, Player3, Player4
🔵 Blue Team: 👑 Player5, Player6, Player7, Player8
```

### Commands Affected
All these commands now show captain emoji:
- `.last` - Most recent PUG
- `.last @Player` - Specific player's last PUG
- `.mylast` - Your most recent PUG
- `.lastt` - Second most recent PUG
- `.lasttt` - Third most recent PUG

### Benefits
- ✅ Easy identification of captains in historical PUGs
- ✅ Helps with accountability and leadership tracking
- ✅ Visual distinction makes team structure clearer
- ✅ Works retroactively - old PUGs without captain data gracefully show no emoji
- ✅ Automatic database migration - no manual setup required

---

## Database Migration Notes

The database migration is **automatic** and happens when the bot starts:

1. On first run with new code, the bot checks if captain columns exist
2. If they don't exist, they are added automatically
3. Migration messages are printed to console:
   - `✅ Database migration: Added 'red_captain' column to pugs table`
   - `✅ Database migration: Added 'blue_captain' column to pugs table`
4. Existing PUG records will have `NULL` for captain fields (shows no emoji)
5. New PUGs will have captain data saved automatically

**No manual intervention required!**

---

## Testing Recommendations

### Ready Check Message Deletion
1. **Test manual leave during ready check:**
   - Fill queue (8/8)
   - Note the message number of ready check
   - Have someone use `.leave`
   - Verify ready check message is deleted
   - Refill queue
   - Verify new ready check appears at bottom of chat

2. **Test decline reaction:**
   - Fill queue (8/8)
   - Note ready check message number
   - Have someone click ❌
   - Verify message is deleted
   - Refill queue
   - Verify new message at bottom

3. **Test timeout scenario:**
   - Fill queue (8/8)
   - Wait for timeout without everyone readying
   - Verify old message deleted if queue doesn't refill
   - Refill queue later
   - Verify new message at bottom

4. **Test ready status preservation:**
   - Fill queue (8/8)
   - 4 players click ✅
   - Someone leaves → ready check cancelled
   - Queue refills
   - Verify the 4 who readied before are still shown as ready

### Captain Display
1. **Test captain display in .last:**
   - Complete a PUG with captains
   - Use `.last`
   - Verify captains have 👑 emoji

2. **Test different commands:**
   - Use `.mylast`, `.lastt`, `.lasttt`
   - Verify captain emoji appears consistently

3. **Test edge cases:**
   - View old PUGs (before captain tracking)
   - Verify no errors, just no emoji
   - View autopick PUGs (might not have captains)
   - Verify graceful handling

4. **Test captain left server:**
   - Captain leaves Discord server
   - Use `.last` to view that PUG
   - Verify emoji still appears next to fetched name

---

## Files Changed

### pug_bot.py
- Lines 337-362: `remove_player()` - Delete message on manual leave
- Lines 650-664: `wait_for_ready_check()` - Delete message on timeout
- Lines 1241-1250: Save captain data when creating PUG
- Lines 1817-1842: Reaction handler - Delete message on decline
- Lines 4583-4612: Red team display with captain emoji
- Lines 4614-4643: Blue team display with captain emoji

### database.py  
- Lines 228-250: Database migration for captain columns
- Lines 806-822: `add_pug()` - Accept and save captain parameters
- Lines 867-873: `get_recent_pugs()` - Retrieve captain data
- Lines 891-903: Include captain data in returned dict

---

## Backward Compatibility

Both features maintain full backward compatibility:

### Ready Check Deletion
- Works with existing queue system
- No breaking changes to ready check flow
- Players who already readied stay ready across cancellations

### Captain Display
- Old PUGs without captain data: Shows teams normally (no emoji)
- New PUGs with captain data: Shows teams with 👑 emoji
- Database migration is automatic and safe
- No data loss or corruption risk

---

## Performance Notes

### Ready Check Message Deletion
- Message deletion is wrapped in try/except (handles already-deleted messages)
- Deletion happens asynchronously (doesn't block other operations)
- No performance impact on ready check flow

### Captain Display
- Captain lookup is O(1) dictionary check per player
- No additional database queries needed
- Minimal overhead in `.last` command execution
