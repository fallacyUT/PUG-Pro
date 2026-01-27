#!/usr/bin/env python3
"""
Database Migration Verification Script
Tests that tiebreaker_enabled column exists and works correctly
"""

import sqlite3
import os

def test_migration():
    """Test the tiebreaker_enabled migration"""
    db_path = "test_migration.db"
    
    # Clean up any existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print("=" * 60)
    print("DATABASE MIGRATION TEST: tiebreaker_enabled")
    print("=" * 60)
    
    # Step 1: Create OLD database (without tiebreaker_enabled column)
    print("\n[Step 1] Creating OLD database schema (v2.0)...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE game_modes (
            mode_name TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            team_size INTEGER NOT NULL,
            description TEXT,
            per_mode_elo_enabled INTEGER DEFAULT 0,
            elo_prefix TEXT
        )
    ''')
    
    # Insert test data
    cursor.execute('''
        INSERT INTO game_modes (mode_name, display_name, team_size, description)
        VALUES ('tam', 'TAM 4v4', 8, 'Team Arena Master')
    ''')
    
    cursor.execute('''
        INSERT INTO game_modes (mode_name, display_name, team_size, description)
        VALUES ('ctf', 'CTF 4v4', 8, 'Capture the Flag')
    ''')
    
    conn.commit()
    print("✅ Created old schema with 2 test modes")
    
    # Verify tiebreaker_enabled doesn't exist yet
    cursor.execute("PRAGMA table_info(game_modes)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'tiebreaker_enabled' in columns:
        print("❌ FAIL: tiebreaker_enabled should not exist yet!")
        conn.close()
        return False
    else:
        print("✅ Confirmed: tiebreaker_enabled column does not exist (as expected)")
    
    conn.close()
    
    # Step 2: Run migration (simulate bot startup)
    print("\n[Step 2] Running migration (simulating bot startup)...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Migration code (same as in database.py)
    try:
        cursor.execute("SELECT tiebreaker_enabled FROM game_modes LIMIT 1")
        print("⚠️  Column already exists (should not happen in this test)")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE game_modes ADD COLUMN tiebreaker_enabled INTEGER DEFAULT 1")
        conn.commit()
        print("✅ Migration: Added 'tiebreaker_enabled' column to game_modes table")
    
    # Step 3: Verify migration worked
    print("\n[Step 3] Verifying migration...")
    cursor.execute("PRAGMA table_info(game_modes)")
    columns = {col[1]: col for col in cursor.fetchall()}
    
    if 'tiebreaker_enabled' not in columns:
        print("❌ FAIL: tiebreaker_enabled column not found after migration!")
        conn.close()
        return False
    
    print("✅ Column exists after migration")
    
    # Check default value
    cursor.execute("SELECT mode_name, tiebreaker_enabled FROM game_modes")
    rows = cursor.fetchall()
    
    print(f"\n[Step 4] Checking default values for {len(rows)} existing modes...")
    all_default_correct = True
    for mode_name, tiebreaker_enabled in rows:
        if tiebreaker_enabled == 1:
            print(f"  ✅ {mode_name}: tiebreaker_enabled = 1 (enabled by default)")
        else:
            print(f"  ❌ {mode_name}: tiebreaker_enabled = {tiebreaker_enabled} (should be 1)")
            all_default_correct = False
    
    if not all_default_correct:
        print("❌ FAIL: Default values incorrect!")
        conn.close()
        return False
    
    # Step 5: Test setting and getting values
    print("\n[Step 5] Testing set/get operations...")
    
    # Disable tiebreaker for tam
    cursor.execute("UPDATE game_modes SET tiebreaker_enabled = 0 WHERE mode_name = 'tam'")
    conn.commit()
    
    # Verify
    cursor.execute("SELECT tiebreaker_enabled FROM game_modes WHERE mode_name = 'tam'")
    tam_value = cursor.fetchone()[0]
    
    if tam_value == 0:
        print("  ✅ Successfully set tam tiebreaker to disabled (0)")
    else:
        print(f"  ❌ FAIL: tam tiebreaker = {tam_value}, expected 0")
        conn.close()
        return False
    
    # Verify ctf is still enabled
    cursor.execute("SELECT tiebreaker_enabled FROM game_modes WHERE mode_name = 'ctf'")
    ctf_value = cursor.fetchone()[0]
    
    if ctf_value == 1:
        print("  ✅ ctf tiebreaker still enabled (1)")
    else:
        print(f"  ❌ FAIL: ctf tiebreaker = {ctf_value}, expected 1")
        conn.close()
        return False
    
    conn.close()
    
    # Clean up
    os.remove(db_path)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nConclusion:")
    print("• Migration adds tiebreaker_enabled column successfully")
    print("• Default value is 1 (enabled) for existing modes")
    print("• Set/Get operations work correctly")
    print("• No 'no such column' errors will occur")
    
    return True

if __name__ == "__main__":
    success = test_migration()
    exit(0 if success else 1)
