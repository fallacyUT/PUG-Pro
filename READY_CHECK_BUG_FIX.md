# Ready Check Bug Fixes

## Bug #1: Promoted Players Removed During Ready Check

### Problem Description

When a player was promoted from the waiting list during an active ready check (because someone declined), they were incorrectly being removed for "not readying up in time."

### The Sequence of Events

1. Queue fills (8/8 players) → Ready check starts
2. Player joins after queue is full → Added to waiting list ✓
3. Player declines ready check → Removed from queue
4. Bot promotes player from waiting list to fill the spot
5. **BUG**: Promoted player is initialized with `ready_responses[player_id] = False`
6. Ready check timeout expires
7. Bot removes anyone with `response != True and response != 'declined'`
8. **Promoted player is removed** despite not having enough time to react

### Example from Your Logs

```
1. jackbernardson declined the ready check and has been removed from the queue
2. humpty promoted from waiting list to 4v4 (8/8)
3. Ready Check - 4v4 (4v4) - Queue is full! React with ✅ within 60 seconds.
4. humpty removed from pug for not readying up in time.
```

## Root Cause

In the `promote_from_waiting_queue()` function (line 264), promoted players during an active ready check were initialized with:

```python
self.ready_responses[promoted_id] = False
```

This meant they were treated the same as players who were in the original queue but didn't react. The timeout logic at line 586 then removed them:

```python
if response != True and response != 'declined':
    not_ready.append(uid)
    self.queue.remove(uid)
```

## The Fix

**Solution**: Auto-ready promoted players since they clearly want to play.

### Changes Made

**File**: `pug_bot.py`, lines 262-272 in `promote_from_waiting_queue()` function

**Before**:
```python
# If we're in ready_check state, initialize ready response for new player
if self.state == 'ready_check':
    self.ready_responses[promoted_id] = False
    # Update the ready check display immediately
    await self.update_ready_check_display()
```

**After**:
```python
# If we're in ready_check state, automatically mark promoted player as ready
# They joined the waiting list knowing they wanted to play, so assume they're ready
if self.state == 'ready_check':
    self.ready_responses[promoted_id] = True
    # Update the ready check display immediately
    await self.update_ready_check_display()
    
    # Check if all players are now ready - if so, proceed immediately
    all_ready = all(self.ready_responses.get(uid, False) == True for uid in self.queue)
    if all_ready and self.ready_check_task:
        self.ready_check_task.cancel()
```

## Benefits of This Fix

1. **Prevents unfair removal**: Promoted players are no longer penalized for joining mid-ready-check
2. **Logical assumption**: If someone joins the waiting list, they clearly want to play
3. **Faster PUG starts**: If the promoted player makes everyone ready, the PUG proceeds immediately
4. **Better UX**: Players don't get removed after explicitly showing interest by joining the wait list

## Testing Recommendations

Test the following scenarios:

1. **Basic promotion during ready check**:
   - Fill queue (8/8)
   - Player joins → goes to waiting list
   - Someone declines ready check
   - Verify promoted player is marked ready
   - Verify they are NOT removed when timeout expires

2. **Everyone ready after promotion**:
   - Fill queue (8/8)
   - All but 1 player ready up
   - That 1 player declines
   - Player from waiting list promoted
   - Verify PUG proceeds immediately (since everyone is now ready)

3. **Multiple promotions**:
   - Fill queue (8/8)
   - Multiple players decline during ready check
   - Multiple players promoted from waiting list
   - Verify all promoted players are auto-readied
   - Verify only non-ready original players are removed on timeout

## Alternative Solutions Considered

1. **Don't track promoted players**: Remove them from `ready_responses` entirely
   - Rejected: Could cause confusion in status display

2. **Use sentinel value**: Set `ready_responses[promoted_id] = 'promoted'`
   - Rejected: More complex, requires changes to multiple code paths

3. **Restart ready check**: Reset timer when someone is promoted
   - Rejected: Could delay PUG starts unnecessarily

4. **Auto-ready (chosen)**: Set `ready_responses[promoted_id] = True`
   - ✓ Simple, logical, and improves UX

## Files Changed

- `pug_bot.py`: 
  - Lines 262-272 (function `promote_from_waiting_queue`) - Bug #1 fix
  - Lines 337-355 (function `remove_player`) - Bug #2 fix  
  - Lines 1816-1834 (reaction handler for ❌) - Bug #2 fix

---

## Bug #2: All Players Removed When Ready Check Cancelled Manually

### Problem Description

When a player manually cancelled their ready check (either by using `.leave` or clicking ❌ to decline), and this caused the queue to drop below full, ALL players who hadn't yet clicked ✅ were being removed from the queue with the message "removed from pug for not readying up in time."

This was incorrect behavior - only players who **timeout** should be removed. Players still in queue when someone else manually cancels should remain in the queue.

### The Sequence of Events

1. Ready check is active with 8/8 players
2. Some players click ✅, others haven't responded yet
3. One player manually leaves (uses `.leave` command) OR clicks ❌ 
4. Queue becomes 7/8 (no longer full)
5. Bot tries to cancel the ready check
6. **BUG**: All players who hadn't clicked ✅ yet get removed with "not readying up in time" message
7. Queue ends up with only 2-3 players instead of 7

### Root Cause

**Race condition in task cancellation order**

The code was cancelling the `ready_check_task` **before** changing the `state` from `'ready_check'` to `'waiting'`:

```python
# OLD CODE - WRONG ORDER
if self.ready_check_task:
    self.ready_check_task.cancel()  # Cancel task first

self.state = 'waiting'  # Change state after
self.ready_responses = {}
```

When `task.cancel()` is called, it raises `CancelledError` in the `wait_for_ready_check()` function. That function then checks:

```python
if self.state != 'ready_check':
    return  # Don't remove anyone
```

**The Race Condition:**
Between the task being cancelled (line 1) and the state being changed (line 2), the cancelled task might wake up and check the state. If it checks **before** the state changes, it sees `state == 'ready_check'` and proceeds to remove all non-ready players!

This is a classic async race condition - the order of operations matters when dealing with concurrent tasks.

### The Fix

**Solution**: Change the state **before** cancelling the task.

This ensures that when the cancelled task wakes up and checks the state, it will always see `state == 'waiting'` and return early without removing anyone.

### Changes Made

**File**: `pug_bot.py`

**Location 1**: Lines 337-355 in `remove_player()` function (manual `.leave` command)

**Before**:
```python
if was_in_ready_check and len(self.queue) < self.team_size:
    # Cancel ready check task
    if self.ready_check_task:
        self.ready_check_task.cancel()
    
    # Return to waiting state
    self.state = 'waiting'
    self.ready_responses = {}
```

**After**:
```python
if was_in_ready_check and len(self.queue) < self.team_size:
    # IMPORTANT: Change state BEFORE cancelling task to prevent race condition
    # This ensures wait_for_ready_check sees the correct state when it wakes up
    self.state = 'waiting'
    self.ready_responses = {}
    
    # Now cancel the ready check task
    if self.ready_check_task:
        self.ready_check_task.cancel()
```

**Location 2**: Lines 1816-1834 in reaction handler (❌ decline reaction)

**Before**:
```python
if len(queue.queue) < queue.team_size:
    # Queue is no longer full, abort ready check and return to waiting
    if queue.ready_check_task:
        queue.ready_check_task.cancel()
    
    queue.state = 'waiting'
    queue.ready_responses = {}
```

**After**:
```python
if len(queue.queue) < queue.team_size:
    # Queue is no longer full, abort ready check and return to waiting
    # IMPORTANT: Change state BEFORE cancelling task to prevent race condition
    queue.state = 'waiting'
    queue.ready_responses = {}
    
    # Now cancel the ready check task
    if queue.ready_check_task:
        queue.ready_check_task.cancel()
```

### Why This Fix Works

1. **Atomic state transition**: The state is changed to `'waiting'` **before** any cancellation happens
2. **Cancelled task protection**: When the `wait_for_ready_check()` task wakes up from cancellation, it immediately checks the state
3. **Early return**: Since state is now `'waiting'`, the task returns early without removing anyone
4. **No race condition**: There's no window where the task can see the old state

### Benefits of This Fix

1. **Correct behavior**: Only players who actually timeout get removed
2. **Better UX**: Players don't get punished when someone else manually cancels
3. **Queue preservation**: Queue stays populated with players who are still interested
4. **Predictable**: Manual cancellation is clearly different from timeout

### Testing Recommendations

Test the following scenarios:

1. **Manual leave during ready check**:
   - Fill queue (8/8), start ready check
   - 4 players click ✅, 4 haven't responded yet
   - One of the ready players uses `.leave` command
   - Verify: Queue should have 7 players (the 4 who were ready + the 3 who hadn't responded)
   - Verify: No one should be removed with "not readying up in time" message

2. **Decline reaction during ready check**:
   - Fill queue (8/8), start ready check  
   - 3 players click ✅, 5 haven't responded yet
   - One player clicks ❌ to decline
   - Verify: Queue should have 7 players remaining
   - Verify: Only the declining player should be removed
   - Verify: Message should say "queue no longer full", NOT "removed for not readying up"

3. **Actual timeout still works**:
   - Fill queue (8/8), start ready check
   - 4 players click ✅, 4 never respond
   - Let the 60 second timeout expire naturally
   - Verify: The 4 non-responsive players ARE removed with "not readying up in time" message
   - Verify: The 4 ready players remain in queue

4. **Combined scenario**:
   - Fill queue (8/8), start ready check
   - 2 players click ✅ immediately
   - 1 player clicks ❌ (decline) → queue becomes 7/8
   - Verify: Ready check is cancelled, 7 players remain
   - No one removed except the person who declined

### Technical Details: AsyncIO Task Cancellation

This fix demonstrates an important principle in asyncio programming:

**When cancelling a task that checks state, always update the state BEFORE cancelling the task.**

```python
# WRONG - Race condition possible
task.cancel()  # Task might check state before next line executes
self.state = 'new_state'

# RIGHT - State is guaranteed to be correct when task checks it
self.state = 'new_state'  # Update state first
task.cancel()  # Task will see correct state when it wakes up
```

This is because `task.cancel()` doesn't immediately stop the task - it raises `CancelledError` at the next `await` point. If there are any operations between the cancel and the state change, the task might observe the old state.
