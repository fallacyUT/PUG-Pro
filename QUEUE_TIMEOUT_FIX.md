# Queue Timeout System - Fixed

**PUG Pro Bot**  
**A customizable version of the TAM Pro Bot**  
**Originally developed for the UT2004 Unreal Fight Club Discord Community**

**Developed by:** fallacy  
**Any questions? Please message fallacy on Discord.**

---

## Issue Fixed

### Problem (Before)
The queue timeout was based on when the first player joined, and never reset. This caused issues:

**Scenario:**
```
Time 0:00 - Player 1 joins queue
Time 3:55 - Player 2 joins queue
Time 4:00 - Queue cleared! ❌

Problem: Player 2 just joined 5 minutes ago, but queue cleared anyway
```

The 4-hour timer started when Player 1 joined and never reset, even when new players joined.

---

## Solution (Now)

### How It Works Now
The queue timeout **resets every time a player joins**. The 4-hour countdown starts fresh with each new join.

**Scenario:**
```
Time 0:00 - Player 1 joins queue → Timer starts (4 hours from now)
Time 3:55 - Player 2 joins queue → Timer RESETS (4 hours from now)
Time 7:50 - Player 3 joins queue → Timer RESETS (4 hours from now)
Time 11:49 - Player 4 joins queue → Timer RESETS (4 hours from now)

Queue stays active as long as players keep joining!
```

---

## How Queue Timeout Works

### Trigger
Queue is cleared if **no players join for 4 hours straight**.

### Reset Triggers
The 4-hour countdown resets when:
- ✅ A player joins the queue (`.j <mode>`)
- ✅ A player is added manually (`.add @player <mode>`)
- ✅ A player is promoted from wait list

### Does NOT Reset
The countdown does NOT reset when:
- ❌ Players leave the queue
- ❌ Players mark ready/unready
- ❌ Admin uses `.reset` command
- ❌ Match completes

**Key Point:** Only NEW PLAYERS joining resets the timer.

---

## Examples

### Example 1: Active Queue
```
12:00 PM - Player A joins → Timer set to 4:00 PM
1:30 PM  - Player B joins → Timer reset to 5:30 PM
2:45 PM  - Player C joins → Timer reset to 6:45 PM
4:00 PM  - Player D joins → Timer reset to 8:00 PM
5:15 PM  - Player E joins → Timer reset to 9:15 PM

Queue stays active! New players keep resetting timer.
```

### Example 2: Stale Queue
```
12:00 PM - Player A joins → Timer set to 4:00 PM
1:00 PM  - Player B joins → Timer reset to 5:00 PM
... no more joins ...
5:00 PM  - Queue CLEARED (4 hours since last join)

Message: "⏱️ Queue has been inactive for 4 hours and has been cleared due to inactivity."
```

### Example 3: Wait List Activity
```
12:00 PM - 10 players join (queue full, 2 in wait list)
1:00 PM  - Match starts and completes
1:05 PM  - 2 wait list players promoted → Timer RESETS
... no more joins ...
5:05 PM  - Queue CLEARED (4 hours since promotion)
```

---

## Why This Matters

### Before (Broken)
```
Player 1 joins at 1:00 PM
Player 2 joins at 4:55 PM
Queue clears at 5:00 PM ❌

Player 2: "I just joined 5 minutes ago!"
```

Unfair to recent joiners. Queue cleared even with activity.

### After (Fixed)
```
Player 1 joins at 1:00 PM
Player 2 joins at 4:55 PM
Queue clears at 8:55 PM ✅

Timer reset when Player 2 joined.
```

Fair to all players. Queue only clears after true inactivity.

---

## Technical Details

### Implementation

**Old Code:**
```python
async def start_inactivity_timer(self):
    # Only set time if not already set
    if self.queue_start_time is None:
        self.queue_start_time = time.time()
    
    # Start timer once...
```

**Problem:** Timer only set once, never updated.

**New Code:**
```python
async def start_inactivity_timer(self):
    # Always update to current time (resets countdown)
    self.queue_start_time = time.time()
    
    # Cancel old timer
    if self.inactivity_timer:
        self.inactivity_timer.cancel()
    
    # Start fresh timer
    self.inactivity_timer = asyncio.create_task(inactivity_check())
```

**Solution:** Timer updates every time someone joins.

### When Timer Starts/Resets

**Queue join:**
```python
async def join(self, user):
    # ... validation ...
    self.queue.append(user.id)
    
    # ALWAYS reset timer on join
    await self.start_inactivity_timer()
```

**Promotion from wait list:**
```python
async def promote_from_waiting_queue(self):
    promoted_id = self.waiting_queue.pop(0)
    self.queue.append(promoted_id)
    
    # Timer resets here too
    await self.start_inactivity_timer()
```

---

## Edge Cases Handled

### Case 1: Player Leaves and Rejoins
```
12:00 PM - Player A joins → Timer set
1:00 PM  - Player A leaves
2:00 PM  - Player A rejoins → Timer RESETS

Result: Timer is at 6:00 PM, not 4:00 PM
```

### Case 2: Multiple Joins in Short Time
```
12:00 PM - Player A joins → Timer set to 4:00 PM
12:01 PM - Player B joins → Timer reset to 4:01 PM
12:02 PM - Player C joins → Timer reset to 4:02 PM

Each join resets the timer, no matter how quick.
```

### Case 3: Queue Full, Then Opens
```
12:00 PM - Queue fills (8/8)
1:00 PM  - Match completes, queue empties
1:05 PM  - Player Z joins empty queue → Timer RESETS

Timer doesn't carry over from before match.
```

---

## What Gets Cleared

When the 4-hour timeout triggers:

**Cleared:**
- ✅ All players in queue
- ✅ All players in wait list
- ✅ Ready check state
- ✅ Captain picks in progress

**Preserved:**
- ✅ Player ELOs
- ✅ Player stats
- ✅ Completed PUG history
- ✅ Mode configuration

Only the current queue state is reset.

---

## Admin Notes

### Timeout Duration
Hardcoded to 4 hours in code:
```python
self.inactivity_timeout = 4 * 60 * 60  # 4 hours in seconds
```

To change, edit this line in `pug_bot.py`.

### Monitoring
Watch console for timeout messages:
```
⏱️ Queue has been inactive for 4 hours and has been cleared due to inactivity.
```

### Manual Clear
Admins can manually clear without waiting:
```
.clearqueue <mode>
```

This is immediate and doesn't wait for timeout.

---

## Benefits

### ✅ Fair to Recent Joiners
Players who just joined won't have queue cleared under them.

### ✅ Prevents Stale Queues
Queues with no activity for 4 hours still get cleared.

### ✅ Automatic Cleanup
No admin intervention needed for abandoned queues.

### ✅ Encourages Activity
Players know queue stays alive with joins.

---

## Comparison

### Before Fix
```
Player 1: 1:00 PM
Player 2: 4:55 PM
Timeout:  5:00 PM ❌ (only 5 min after Player 2)
```

### After Fix
```
Player 1: 1:00 PM
Player 2: 4:55 PM
Timeout:  8:55 PM ✅ (4 hours after Player 2)
```

---

## FAQ

**Q: What if I want a different timeout duration?**  
A: Edit `self.inactivity_timeout` in pug_bot.py. Examples:
```python
self.inactivity_timeout = 2 * 60 * 60  # 2 hours
self.inactivity_timeout = 6 * 60 * 60  # 6 hours
self.inactivity_timeout = 1 * 60 * 60  # 1 hour
```

**Q: Does the timer reset when someone leaves?**  
A: No. Only when someone JOINS.

**Q: What if players are just sitting in queue but not actually playing?**  
A: As long as no new players join, queue will clear after 4 hours. This is intentional.

**Q: Can I disable the timeout completely?**  
A: Set it to a very large number:
```python
self.inactivity_timeout = 365 * 24 * 60 * 60  # 1 year
```

**Q: Is there a warning before the queue clears?**  
A: No. It just clears after 4 hours of no joins. Consider adding a warning message in future.

**Q: Does this affect completed PUG history?**  
A: No. Only affects active queue state. History is preserved.

---

## Summary

**Old Behavior:**
- Timer started on first join
- Never reset
- Queue could clear even with recent activity

**New Behavior:**
- Timer resets on every join
- Queue only clears after true 4-hour inactivity
- Fair to all players

**Key Principle:**
The 4-hour countdown measures time since **last player joined**, not since queue started.

---

**Questions?** Message **fallacy** on Discord!

---

**Developed by:** fallacy  
**For:** Competitive Gaming Communities  
*A customizable version of the TAM Pro Bot*  
*Originally developed for the UT2004 Unreal Fight Club Discord Community*
