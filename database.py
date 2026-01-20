"""
PUG Pro Discord Bot - Database Manager

A customizable version of the TAM Pro Bot
Originally developed for the UT2004 Unreal Fight Club Discord Community

Developed by: fallacy

Bot made for Competitive Gaming Communities to use for Pick Up Games (PUGs)
Any questions? Please message fallacy on Discord.
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import json

class DatabaseManager:
    def __init__(self, db_path='pug_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                discord_id TEXT,
                server_id TEXT,
                discord_name TEXT,
                display_name TEXT,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                total_pugs INTEGER DEFAULT 0,
                elo REAL DEFAULT 1000,
                ut2k4_player_name TEXT,
                ut2k4_last_scraped TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (discord_id, server_id)
            )
        ''')
        
        # Migration: Add discord_name and display_name columns if they don't exist
        try:
            cursor.execute("SELECT discord_name FROM players LIMIT 1")
        except:
            print("⚠️  Adding discord_name and display_name columns to players table...")
            cursor.execute("ALTER TABLE players ADD COLUMN discord_name TEXT")
            cursor.execute("ALTER TABLE players ADD COLUMN display_name TEXT")
            conn.commit()
            print("✅ Added discord_name and display_name columns")
        
        # Migration: Add server_id to players if it doesn't exist
        try:
            cursor.execute("SELECT server_id FROM players LIMIT 1")
        except:
            # Column doesn't exist, need to migrate
            print("⚠️  Migrating players table to add server_id...")
            print("   This migration PRESERVES all existing player data!")
            
            # Get existing players with ALL columns
            cursor.execute("SELECT * FROM players")
            old_players = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(players)")
            old_columns = [col[1] for col in cursor.fetchall()]
            
            print(f"   Found {len(old_players)} players to migrate...")
            
            # Rename old table
            cursor.execute("ALTER TABLE players RENAME TO players_old")
            
            # Create new table with server_id
            cursor.execute('''
                CREATE TABLE players (
                    discord_id TEXT,
                    server_id TEXT,
                    discord_name TEXT,
                    display_name TEXT,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    total_pugs INTEGER DEFAULT 0,
                    elo REAL DEFAULT 1000,
                    ut2k4_player_name TEXT,
                    ut2k4_last_scraped TEXT,
                    peak_elo REAL,
                    current_streak INTEGER DEFAULT 0,
                    best_win_streak INTEGER DEFAULT 0,
                    best_loss_streak INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (discord_id, server_id)
                )
            ''')
            
            # Migrate data - need to assign a default server_id
            # Use 'default' as server_id for all existing players
            print("   Migrating player data with server_id='default'...")
            
            # Build insert based on old columns
            for old_player in old_players:
                # Map old columns to values
                player_dict = dict(zip(old_columns, old_player))
                
                cursor.execute('''
                    INSERT INTO players 
                    (discord_id, server_id, discord_name, display_name, wins, losses, total_pugs, 
                     elo, ut2k4_player_name, ut2k4_last_scraped, peak_elo, current_streak, 
                     best_win_streak, best_loss_streak, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_dict.get('discord_id'),
                    'default',  # Default server_id for migrated players
                    player_dict.get('discord_name'),
                    player_dict.get('display_name'),
                    player_dict.get('wins', 0),
                    player_dict.get('losses', 0),
                    player_dict.get('total_pugs', 0),
                    player_dict.get('elo', 1000),
                    player_dict.get('ut2k4_player_name'),
                    player_dict.get('ut2k4_last_scraped'),
                    player_dict.get('peak_elo', player_dict.get('elo', 1000)),
                    player_dict.get('current_streak', 0),
                    player_dict.get('best_win_streak', 0),
                    player_dict.get('best_loss_streak', 0),
                    player_dict.get('created_at')
                ))
            
            # Drop old table
            cursor.execute("DROP TABLE players_old")
            
            conn.commit()
            print(f"✅ Players table migrated successfully!")
            print(f"   {len(old_players)} players migrated with server_id='default'")
            print(f"   All ELOs, stats, and player data PRESERVED!")

        # Migration: Add current_streak column if it doesn't exist
        try:
            cursor.execute("SELECT current_streak FROM players LIMIT 1")
        except:
            print("⚠️  Adding current_streak column to players table...")
            cursor.execute("ALTER TABLE players ADD COLUMN current_streak INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Added current_streak column")
        
        # Migration: Add peak_elo column if it doesn't exist
        try:
            cursor.execute("SELECT peak_elo FROM players LIMIT 1")
        except:
            print("⚠️  Adding peak_elo column to players table...")
            cursor.execute("ALTER TABLE players ADD COLUMN peak_elo REAL DEFAULT 1000")
            # Update existing players' peak_elo to their current ELO
            cursor.execute("UPDATE players SET peak_elo = elo WHERE peak_elo IS NULL OR peak_elo < elo")
            conn.commit()
            print("✅ Added peak_elo column")
        
        # Migration already completed - peak_elo values have been reset
        # Skipping to avoid UNIQUE constraint error
        reset_done = True  # Force skip
        
        # if not reset_done:
        #     print("⚠️  Resetting all peak_elo values to current ELO (one-time fix)...")
        #     cursor.execute("UPDATE players SET peak_elo = elo")
        #     fixed_count = cursor.rowcount
        #     cursor.execute("INSERT INTO migrations (name) VALUES ('reset_peak_v2')")
        #     conn.commit()
        #     print(f"✅ Reset peak_elo for {fixed_count} player(s) - will track correctly going forward")
        
        # Migration: Add registered column if it doesn't exist
        try:
            cursor.execute("SELECT registered FROM players LIMIT 1")
        except:
            print("⚠️  Adding registered column to players table...")
            cursor.execute("ALTER TABLE players ADD COLUMN registered INTEGER DEFAULT 0")
            # Mark existing players (who have played PUGs) as registered
            cursor.execute("UPDATE players SET registered = 1 WHERE total_pugs > 0")
            conn.commit()
            print("✅ Added registered column")
        
        # Migration: Add best_win_streak column if it doesn't exist
        try:
            cursor.execute("SELECT best_win_streak FROM players LIMIT 1")
        except:
            print("⚠️  Adding best_win_streak column to players table...")
            cursor.execute("ALTER TABLE players ADD COLUMN best_win_streak INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Added best_win_streak column")
        
        # Migration: Add best_loss_streak column if it doesn't exist
        try:
            cursor.execute("SELECT best_loss_streak FROM players LIMIT 1")
        except:
            print("⚠️  Adding best_loss_streak column to players table...")
            cursor.execute("ALTER TABLE players ADD COLUMN best_loss_streak INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Added best_loss_streak column")
        
        # PUGs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pugs (
                pug_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_mode TEXT NOT NULL,
                winner TEXT,
                avg_red_elo REAL,
                avg_blue_elo REAL,
                status TEXT DEFAULT 'active',
                tiebreaker_map TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration: Add status column if it doesn't exist (for existing databases)
        try:
            cursor.execute("SELECT status FROM pugs LIMIT 1")
        except:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE pugs ADD COLUMN status TEXT DEFAULT 'active'")
            conn.commit()
            print("✅ Database migration: Added 'status' column to pugs table")
        
        # Migration: Add tiebreaker_map column if it doesn't exist
        try:
            cursor.execute("SELECT tiebreaker_map FROM pugs LIMIT 1")
        except:
            cursor.execute("ALTER TABLE pugs ADD COLUMN tiebreaker_map TEXT")
            conn.commit()
            print("✅ Database migration: Added 'tiebreaker_map' column to pugs table")
        
        # PUG teams table (many-to-many relationship)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pug_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pug_id INTEGER NOT NULL,
                discord_id TEXT NOT NULL,
                team TEXT NOT NULL,
                FOREIGN KEY (pug_id) REFERENCES pugs (pug_id),
                FOREIGN KEY (discord_id) REFERENCES players (discord_id)
            )
        ''')
        
        # Timeouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeouts (
                discord_id TEXT PRIMARY KEY,
                timeout_end TEXT NOT NULL,
                FOREIGN KEY (discord_id) REFERENCES players (discord_id)
            )
        ''')
        
        # PUG Admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pug_admins (
                discord_id TEXT,
                server_id TEXT,
                PRIMARY KEY (discord_id, server_id)
            )
        ''')
        
        # Migration: Add server_id column if it doesn't exist
        try:
            cursor.execute("SELECT server_id FROM pug_admins LIMIT 1")
        except:
            # Column doesn't exist, need to migrate
            print("⚠️  Migrating pug_admins table to add server_id...")
            
            # Get existing admins
            cursor.execute("SELECT discord_id FROM pug_admins")
            old_admins = cursor.fetchall()
            
            print(f"   Found {len(old_admins)} admins to migrate...")
            
            # Rename old table
            cursor.execute("ALTER TABLE pug_admins RENAME TO pug_admins_old")
            
            # Create new table
            cursor.execute('''
                CREATE TABLE pug_admins (
                    discord_id TEXT,
                    server_id TEXT,
                    PRIMARY KEY (discord_id, server_id)
                )
            ''')
            
            # Re-add old admins with default server_id
            print("   Migrating admins with server_id='default'...")
            for admin in old_admins:
                cursor.execute('''
                    INSERT INTO pug_admins (discord_id, server_id)
                    VALUES (?, ?)
                ''', (admin[0], 'default'))
            
            # Drop old table
            cursor.execute("DROP TABLE pug_admins_old")
            
            conn.commit()
            print(f"✅ Database migration: Added 'server_id' to pug_admins table")
            print(f"   {len(old_admins)} admins migrated with server_id='default'")
            print(f"   All admin permissions PRESERVED!")
        
        # Game Modes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_modes (
                mode_name TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                team_size INTEGER NOT NULL,
                description TEXT,
                per_mode_elo_enabled INTEGER DEFAULT 0,
                elo_prefix TEXT
            )
        ''')
        
        # Migration: Add elo_prefix column if it doesn't exist
        try:
            cursor.execute("SELECT elo_prefix FROM game_modes LIMIT 1")
        except:
            cursor.execute("ALTER TABLE game_modes ADD COLUMN elo_prefix TEXT")
            conn.commit()
            print("✅ Database migration: Added 'elo_prefix' column to game_modes table")
        
        # Migration: Add per_mode_elo_enabled column if it doesn't exist
        try:
            cursor.execute("SELECT per_mode_elo_enabled FROM game_modes LIMIT 1")
        except:
            cursor.execute("ALTER TABLE game_modes ADD COLUMN per_mode_elo_enabled INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Database migration: Added 'per_mode_elo_enabled' column to game_modes table")
        
        # Mode Aliases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mode_aliases (
                alias TEXT PRIMARY KEY,
                mode_name TEXT NOT NULL,
                FOREIGN KEY (mode_name) REFERENCES game_modes(mode_name) ON DELETE CASCADE
            )
        ''')
        
        # Player Mode ELOs table - separate ELO per mode per player
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_mode_elos (
                discord_id TEXT,
                server_id TEXT,
                mode_name TEXT,
                elo REAL DEFAULT 1000,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                peak_elo REAL DEFAULT 1000,
                current_streak INTEGER DEFAULT 0,
                best_win_streak INTEGER DEFAULT 0,
                best_loss_streak INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (discord_id, server_id, mode_name),
                FOREIGN KEY (mode_name) REFERENCES game_modes(mode_name) ON DELETE CASCADE
            )
        ''')
        
        # Maps table - store maps per mode/prefix
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                mode_prefix TEXT NOT NULL,
                map_name TEXT NOT NULL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(server_id, mode_prefix, map_name)
            )
        ''')
        
        # Map cooldowns table - track recently used maps per server
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS map_cooldowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                mode_prefix TEXT NOT NULL,
                map_name TEXT NOT NULL,
                used_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bot Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # NOTE: No default game modes are created
        # Admins must create game modes with .addmode command
        # Example: .addmode 4v4 8 (creates a 4v4 mode with 8 total players)
        
        # Initialize scraping setting
        cursor.execute('''
            INSERT OR IGNORE INTO bot_settings (key, value)
            VALUES ('scraping_enabled', 'false')
        ''')
        
        # Initialize per-mode ELO setting
        cursor.execute('''
            INSERT OR IGNORE INTO bot_settings (key, value)
            VALUES ('per_mode_elo_enabled', 'false')
        ''')
        
        # Initialize pug counter
        cursor.execute('''
            INSERT OR IGNORE INTO bot_settings (key, value)
            VALUES ('pug_counter', '0')
        ''')
        
        conn.commit()
        conn.close()
    
    # Player operations
    def get_player(self, discord_id: str, server_id: str = None) -> Dict:
        """Get player (server-scoped) - does NOT auto-create"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # If no server_id provided, this is an error in new system
        if not server_id:
            raise ValueError("server_id is required for get_player")
        
        cursor.execute('''
            SELECT discord_id, server_id, discord_name, display_name, 
                   wins, losses, total_pugs, elo, 
                   ut2k4_player_name, ut2k4_last_scraped, current_streak, registered, peak_elo
            FROM players 
            WHERE discord_id = ? AND server_id = ?
        ''', (str(discord_id), str(server_id)))
        row = cursor.fetchone()
        
        if row:
            player = {
                'discord_id': row[0],
                'server_id': row[1],
                'discord_name': row[2],
                'display_name': row[3],
                'wins': row[4],
                'losses': row[5],
                'total_pugs': row[6],
                'elo': row[7],
                'ut2k4_player_name': row[8],
                'ut2k4_last_scraped': row[9],
                'current_streak': row[10] if len(row) > 10 else 0,
                'registered': row[11] if len(row) > 11 else 0,
                'peak_elo': row[12] if len(row) > 12 else row[7]
            }
        else:
            player = None
        
        conn.close()
        return player
    
    def register_player(self, discord_id: str, server_id: str, discord_name: str = None, display_name: str = None) -> Dict:
        """Register a new player (creates with registered=1, elo needs to be set by admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already exists
        existing = self.get_player(discord_id, server_id)
        if existing:
            # If already exists but not registered, mark as registered
            if not existing.get('registered'):
                cursor.execute('''
                    UPDATE players 
                    SET registered = 1
                    WHERE discord_id = ? AND server_id = ?
                ''', (str(discord_id), str(server_id)))
                conn.commit()
                existing['registered'] = 1
            conn.close()
            return existing
        
        # Create new registered player
        cursor.execute('''
            INSERT INTO players (discord_id, server_id, discord_name, display_name, wins, losses, total_pugs, elo, current_streak, registered, peak_elo)
            VALUES (?, ?, ?, ?, 0, 0, 0, 1000, 0, 1, NULL)
        ''', (str(discord_id), str(server_id), discord_name, display_name))
        conn.commit()
        
        player = {
            'discord_id': str(discord_id),
            'server_id': str(server_id),
            'discord_name': discord_name,
            'display_name': display_name,
            'wins': 0,
            'losses': 0,
            'total_pugs': 0,
            'elo': 1000.0,
            'ut2k4_player_name': None,
            'ut2k4_last_scraped': None,
            'current_streak': 0,
            'registered': 1,
            'peak_elo': None
        }
        
        conn.close()
        return player
    
    def player_exists(self, discord_id: str, server_id: str) -> bool:
        """Check if a player is registered without creating them"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT discord_id FROM players WHERE discord_id = ? AND server_id = ?', 
                      (str(discord_id), str(server_id)))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def update_player_names(self, discord_id: str, server_id: str, discord_name: str, display_name: str):
        """Update player's Discord username and display name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE players 
            SET discord_name = ?, display_name = ?
            WHERE discord_id = ? AND server_id = ?
        ''', (discord_name, display_name, str(discord_id), str(server_id)))
        
        conn.commit()
        conn.close()
    
    def find_player_by_name(self, server_id: str, name: str) -> str:
        """Find a player's Discord ID by their Discord username or display name (case-insensitive)
        Returns discord_id if found, None otherwise"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT discord_id FROM players 
            WHERE server_id = ? 
            AND (LOWER(discord_name) = LOWER(?) OR LOWER(display_name) = LOWER(?))
            LIMIT 1
        ''', (str(server_id), name, name))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def delete_player(self, discord_id: str, server_id: str) -> bool:
        """Delete a player from the database (server-scoped)
        Returns True if player was deleted, False if player didn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if player exists
        cursor.execute('SELECT discord_id FROM players WHERE discord_id = ? AND server_id = ?', 
                      (str(discord_id), str(server_id)))
        exists = cursor.fetchone() is not None
        
        if exists:
            # Delete player
            cursor.execute('DELETE FROM players WHERE discord_id = ? AND server_id = ?', 
                          (str(discord_id), str(server_id)))
            conn.commit()
        
        conn.close()
        return exists
    
    def update_player_stats(self, discord_id: str, server_id: str, won: bool):
        """Update player win/loss stats and streak (server-scoped)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current streak and best streaks
        cursor.execute('''
            SELECT current_streak, best_win_streak, best_loss_streak 
            FROM players 
            WHERE discord_id = ? AND server_id = ?
        ''', (str(discord_id), str(server_id)))
        result = cursor.fetchone()
        current_streak = result[0] if result and result[0] is not None else 0
        best_win_streak = result[1] if result and len(result) > 1 and result[1] is not None else 0
        best_loss_streak = result[2] if result and len(result) > 2 and result[2] is not None else 0
        
        if won:
            # Win: increment positive streak or start new one
            new_streak = current_streak + 1 if current_streak >= 0 else 1
            
            # Update best win streak if this is a new record
            new_best_win = max(best_win_streak, new_streak)
            
            cursor.execute('''
                UPDATE players 
                SET wins = wins + 1, 
                    total_pugs = total_pugs + 1, 
                    current_streak = ?,
                    best_win_streak = ?
                WHERE discord_id = ? AND server_id = ?
            ''', (new_streak, new_best_win, str(discord_id), str(server_id)))
        else:
            # Loss: decrement negative streak or start new one
            new_streak = current_streak - 1 if current_streak <= 0 else -1
            
            # Update best loss streak if this is a new record (stored as positive number)
            new_best_loss = max(best_loss_streak, abs(new_streak))
            
            cursor.execute('''
                UPDATE players 
                SET losses = losses + 1, 
                    total_pugs = total_pugs + 1, 
                    current_streak = ?,
                    best_loss_streak = ?
                WHERE discord_id = ? AND server_id = ?
            ''', (new_streak, new_best_loss, str(discord_id), str(server_id)))
        
        conn.commit()
        conn.close()
    
    def update_player_elo(self, discord_id: str, server_id: str, new_elo: float):
        """Update player ELO and peak ELO if new high (server-scoped)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Update ELO and peak_elo
        # If peak_elo is NULL (first game), set it to new_elo
        # Otherwise, only update if new_elo is higher
        cursor.execute('''
            UPDATE players 
            SET elo = ?,
                peak_elo = CASE 
                    WHEN peak_elo IS NULL THEN ?
                    WHEN ? > peak_elo THEN ? 
                    ELSE peak_elo 
                END
            WHERE discord_id = ? AND server_id = ?
        ''', (new_elo, new_elo, new_elo, new_elo, str(discord_id), str(server_id)))
        
        conn.commit()
        conn.close()
    
    def update_ut2k4_info(self, discord_id: str, server_id: str, ut2k4_name: str):
        """Update player's UT2K4 name (server-scoped)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE players 
            SET ut2k4_player_name = ?, ut2k4_last_scraped = ?
            WHERE discord_id = ? AND server_id = ?
        ''', (ut2k4_name, datetime.now().isoformat(), str(discord_id), str(server_id)))
        
        conn.commit()
        conn.close()
    
    def update_player_total_pugs(self, discord_id: str, server_id: str, total_pugs: int) -> bool:
        """Update player's total PUG count without affecting ELO or win/loss (server-scoped)
        
        This is used for importing historical data from previous bots.
        Returns True if successful, False otherwise.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Update only the total_pugs field
            cursor.execute('''
                UPDATE players 
                SET total_pugs = ?
                WHERE discord_id = ? AND server_id = ?
            ''', (total_pugs, str(discord_id), str(server_id)))
            
            # Check if any row was actually updated
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating player total_pugs: {e}")
            return False
    
    def get_all_players(self, server_id: str = None) -> List[Dict]:
        """Get all players, optionally filtered by server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if server_id:
            cursor.execute('''
                SELECT discord_id, server_id, discord_name, display_name,
                       wins, losses, total_pugs, elo, peak_elo,
                       ut2k4_player_name, ut2k4_last_scraped, current_streak, registered,
                       best_win_streak, best_loss_streak
                FROM players 
                WHERE server_id = ?
            ''', (str(server_id),))
        else:
            cursor.execute('''
                SELECT discord_id, server_id, discord_name, display_name,
                       wins, losses, total_pugs, elo, peak_elo,
                       ut2k4_player_name, ut2k4_last_scraped, current_streak, registered,
                       best_win_streak, best_loss_streak
                FROM players
            ''')
        
        rows = cursor.fetchall()
        
        players = []
        for row in rows:
            players.append({
                'discord_id': row[0],
                'server_id': row[1],
                'discord_name': row[2],
                'display_name': row[3],
                'wins': row[4],
                'losses': row[5],
                'total_pugs': row[6],
                'elo': row[7],
                'peak_elo': row[8] if len(row) > 8 else row[7],  # Default to current elo
                'ut2k4_player_name': row[9] if len(row) > 9 else None,
                'ut2k4_last_scraped': row[10] if len(row) > 10 else None,
                'current_streak': row[11] if len(row) > 11 else 0,
                'registered': row[12] if len(row) > 12 else 0,
                'best_win_streak': row[13] if len(row) > 13 else 0,
                'best_loss_streak': row[14] if len(row) > 14 else 0
            })
        
        conn.close()
        return players
    
    def bulk_update_elos(self, server_id: str, elo_updates: List[tuple]) -> tuple:
        """
        Bulk update ELOs for a server
        elo_updates: List of (discord_id, new_elo) tuples
        Returns: (success_count, error_count, errors_list)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        success_count = 0
        error_count = 0
        errors = []
        
        for discord_id, new_elo in elo_updates:
            try:
                # Validate that discord_id is numeric
                if not str(discord_id).isdigit():
                    error_count += 1
                    errors.append(f"Invalid Discord ID '{discord_id}': must be numeric")
                    continue
                
                # Check if player exists for this server
                cursor.execute('SELECT discord_id FROM players WHERE discord_id = ? AND server_id = ?',
                              (str(discord_id), str(server_id)))
                if cursor.fetchone():
                    # Update existing player
                    cursor.execute('UPDATE players SET elo = ? WHERE discord_id = ? AND server_id = ?',
                                  (float(new_elo), str(discord_id), str(server_id)))
                    success_count += 1
                else:
                    # Create new player with this ELO
                    cursor.execute('''
                        INSERT INTO players (discord_id, server_id, wins, losses, total_pugs, elo)
                        VALUES (?, ?, 0, 0, 0, ?)
                    ''', (str(discord_id), str(server_id), float(new_elo)))
                    success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Discord ID {discord_id}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return (success_count, error_count, errors)
    
    # PUG operations
    def add_pug(self, red_team: List[str], blue_team: List[str], game_mode: str, 
                avg_red_elo: float, avg_blue_elo: float, tiebreaker_map: str = None) -> int:
        """Add a new PUG and return the pug_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert PUG
        cursor.execute('''
            INSERT INTO pugs (game_mode, avg_red_elo, avg_blue_elo, tiebreaker_map)
            VALUES (?, ?, ?, ?)
        ''', (game_mode, avg_red_elo, avg_blue_elo, tiebreaker_map))
        
        pug_id = cursor.lastrowid
        
        # Insert red team members
        for discord_id in red_team:
            cursor.execute('''
                INSERT INTO pug_teams (pug_id, discord_id, team)
                VALUES (?, ?, 'red')
            ''', (pug_id, str(discord_id)))
        
        # Insert blue team members
        for discord_id in blue_team:
            cursor.execute('''
                INSERT INTO pug_teams (pug_id, discord_id, team)
                VALUES (?, ?, 'blue')
            ''', (pug_id, str(discord_id)))
        
        conn.commit()
        conn.close()
        
        # Return the pug_id which serves as the PUG number
        return pug_id
    
    def update_pug_winner(self, pug_id: int, winner: str):
        """Update PUG winner"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE pugs SET winner = ? WHERE pug_id = ?', 
                      (winner, pug_id))
        
        conn.commit()
        conn.close()
    
    def delete_pug(self, pug_id: int):
        """Mark a PUG as killed (don't actually delete it)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Mark the PUG as killed instead of deleting
        cursor.execute("UPDATE pugs SET status = 'killed' WHERE pug_id = ?", (pug_id,))
        
        conn.commit()
        conn.close()
    
    def get_recent_pugs(self, limit: int = 3) -> List[Dict]:
        """Get recent PUGs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pug_id, game_mode, winner, avg_red_elo, avg_blue_elo, timestamp, status, tiebreaker_map
            FROM pugs
            ORDER BY pug_id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        pugs = []
        
        for row in rows:
            pug_id = row[0]
            
            # Get team members
            cursor.execute('''
                SELECT discord_id, team 
                FROM pug_teams 
                WHERE pug_id = ?
            ''', (pug_id,))
            
            team_rows = cursor.fetchall()
            red_team = [r[0] for r in team_rows if r[1] == 'red']
            blue_team = [r[0] for r in team_rows if r[1] == 'blue']
            
            pugs.append({
                'pug_id': pug_id,
                'number': pug_id,
                'game_mode': row[1],
                'winner': row[2],
                'avg_red_elo': row[3],
                'avg_blue_elo': row[4],
                'timestamp': row[5],
                'status': row[6] if len(row) > 6 else 'active',
                'tiebreaker_map': row[7] if len(row) > 7 else None,
                'red_team': red_team,
                'blue_team': blue_team
            })
        
        conn.close()
        return pugs
    
    def get_last_pug_id(self) -> Optional[int]:
        """Get the last PUG ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(pug_id) FROM pugs')
        result = cursor.fetchone()[0]
        
        conn.close()
        return result
    
    # Timeout operations
    def add_timeout(self, discord_id: str, timeout_end: datetime):
        """Add a timeout for a player"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO timeouts (discord_id, timeout_end)
            VALUES (?, ?)
        ''', (str(discord_id), timeout_end.isoformat()))
        
        conn.commit()
        conn.close()
    
    def is_timed_out(self, discord_id: str) -> Tuple[bool, Optional[datetime]]:
        """Check if player is timed out"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT timeout_end FROM timeouts WHERE discord_id = ?', 
                      (str(discord_id),))
        row = cursor.fetchone()
        
        if row:
            timeout_end = datetime.fromisoformat(row[0])
            if datetime.now() < timeout_end:
                conn.close()
                return True, timeout_end
            else:
                # Timeout expired, remove it
                cursor.execute('DELETE FROM timeouts WHERE discord_id = ?', 
                             (str(discord_id),))
                conn.commit()
        
        conn.close()
        return False, None
    
    # PUG Admin operations
    def add_pug_admin(self, discord_id: str, server_id: str):
        """Add a PUG admin for a specific server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT OR IGNORE INTO pug_admins (discord_id, server_id) VALUES (?, ?)', 
                      (str(discord_id), str(server_id)))
        
        conn.commit()
        conn.close()
    
    def remove_pug_admin(self, discord_id: str, server_id: str):
        """Remove a PUG admin from a specific server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM pug_admins WHERE discord_id = ? AND server_id = ?', 
                      (str(discord_id), str(server_id)))
        
        conn.commit()
        conn.close()
    
    def is_pug_admin(self, discord_id: str, server_id: str) -> bool:
        """Check if user is a PUG admin on a specific server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT discord_id FROM pug_admins WHERE discord_id = ? AND server_id = ?', 
                      (str(discord_id), str(server_id)))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def get_pug_admins(self, server_id: str = None) -> List[str]:
        """Get all PUG admins for a specific server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if server_id:
            cursor.execute('SELECT discord_id FROM pug_admins WHERE server_id = ?', (str(server_id),))
        else:
            cursor.execute('SELECT discord_id FROM pug_admins')
        
        rows = cursor.fetchall()
        
        conn.close()
        return [row[0] for row in rows]
    
    # Game Mode operations
    def add_game_mode(self, mode_name: str, display_name: str, team_size: int, 
                     description: str = "") -> Tuple[bool, Optional[str]]:
        """Add a game mode"""
        if team_size < 2 or team_size % 2 != 0:
            return False, "Team size must be an even number of at least 2!"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO game_modes (mode_name, display_name, team_size, description)
                VALUES (?, ?, ?, ?)
            ''', (mode_name.lower(), display_name, team_size, description))
            conn.commit()
            conn.close()
            return True, None
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Game mode already exists!"
    
    def remove_game_mode(self, mode_name: str) -> Tuple[bool, Optional[str]]:
        """Remove a game mode"""
        if mode_name.lower() == 'default':
            return False, "Cannot remove the default game mode!"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM game_modes WHERE mode_name = ?', 
                      (mode_name.lower(),))
        
        if cursor.rowcount == 0:
            conn.close()
            return False, "Game mode does not exist!"
        
        conn.commit()
        conn.close()
        return True, None
    
    def get_game_mode(self, mode_name: str) -> Optional[Dict]:
        """Get a game mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mode_name, display_name, team_size, description 
            FROM game_modes 
            WHERE mode_name = ?
        ''', (mode_name.lower(),))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'name': row[1],  # display_name
                'team_size': row[2],
                'description': row[3]
            }
        return None
    
    def get_all_game_modes(self) -> Dict:
        """Get all game modes sorted by player count (descending)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT mode_name, display_name, team_size, description FROM game_modes ORDER BY team_size DESC')
        rows = cursor.fetchall()
        
        modes = {}
        for row in rows:
            modes[row[0]] = {
                'name': row[1],
                'team_size': row[2],
                'description': row[3]
            }
        
        conn.close()
        return modes
    
    def remove_mode(self, mode_name: str) -> tuple[bool, str]:
        """Remove a game mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if mode exists
        cursor.execute('SELECT mode_name FROM game_modes WHERE mode_name = ?', (mode_name,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Mode '{mode_name}' does not exist!"
        
        # Check if mode is 'default' (cannot remove default mode if it exists)
        if mode_name == 'default':
            conn.close()
            return False, "Cannot remove the default mode!"
        
        # Remove mode and its aliases
        try:
            cursor.execute('DELETE FROM game_modes WHERE mode_name = ?', (mode_name,))
            cursor.execute('DELETE FROM mode_aliases WHERE mode_name = ?', (mode_name,))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def add_mode_alias(self, alias: str, mode_name: str) -> tuple[bool, str]:
        """Add an alias for a game mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if mode exists
        cursor.execute('SELECT mode_name FROM game_modes WHERE mode_name = ?', (mode_name,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Mode '{mode_name}' does not exist!"
        
        # Check if alias already exists
        cursor.execute('SELECT mode_name FROM mode_aliases WHERE alias = ?', (alias,))
        if cursor.fetchone():
            conn.close()
            return False, f"Alias '{alias}' already exists!"
        
        # Check if alias conflicts with existing mode name
        cursor.execute('SELECT mode_name FROM game_modes WHERE mode_name = ?', (alias,))
        if cursor.fetchone():
            conn.close()
            return False, f"'{alias}' is already a mode name!"
        
        # Add alias
        try:
            cursor.execute('INSERT INTO mode_aliases (alias, mode_name) VALUES (?, ?)', (alias, mode_name))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def remove_mode_alias(self, alias: str) -> tuple[bool, str]:
        """Remove a mode alias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT mode_name FROM mode_aliases WHERE alias = ?', (alias,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Alias '{alias}' does not exist!"
        
        cursor.execute('DELETE FROM mode_aliases WHERE alias = ?', (alias,))
        conn.commit()
        conn.close()
        return True, None
    
    def get_mode_aliases(self, mode_name: str) -> list:
        """Get all aliases for a mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT alias FROM mode_aliases WHERE mode_name = ?', (mode_name,))
        rows = cursor.fetchall()
        
        conn.close()
        return [row[0] for row in rows]
    
    def resolve_mode_alias(self, name: str) -> str:
        """Resolve an alias to its actual mode name, or return the name if it's not an alias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if it's an alias
        cursor.execute('SELECT mode_name FROM mode_aliases WHERE alias = ?', (name,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else name
    
    # Bot Settings operations
    def get_setting(self, key: str) -> Optional[str]:
        """Get a bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM bot_settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a bot setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def is_scraping_enabled(self) -> bool:
        """Check if scraping is enabled"""
        value = self.get_setting('scraping_enabled')
        return value == 'true' if value else False
    
    def set_scraping_enabled(self, enabled: bool):
        """Enable or disable scraping"""
        self.set_setting('scraping_enabled', 'true' if enabled else 'false')
    
    # Per-Mode ELO Functions
    def is_per_mode_elo_enabled(self, mode_name: str = None) -> bool:
        """Check if per-mode ELO is enabled for a specific mode
        
        Args:
            mode_name: Mode to check. If None, checks global setting (deprecated)
            
        Returns:
            bool: True if the mode has per-mode ELO enabled
        """
        if mode_name:
            # Check mode-specific setting
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT per_mode_elo_enabled FROM game_modes WHERE mode_name = ?
            ''', (mode_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return row[0] == 1
            return False
        else:
            # Legacy: Check global setting (deprecated)
            value = self.get_setting('per_mode_elo_enabled')
            return value == 'true' if value else False
    
    def set_per_mode_elo_for_mode(self, mode_name: str, enabled: bool) -> tuple[bool, str]:
        """Enable or disable per-mode ELO for a specific mode
        
        Args:
            mode_name: The mode to configure
            enabled: True to enable, False to disable
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if mode exists
        cursor.execute('SELECT mode_name FROM game_modes WHERE mode_name = ?', (mode_name,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Mode '{mode_name}' does not exist!"
        
        # Update per_mode_elo_enabled flag
        cursor.execute('''
            UPDATE game_modes SET per_mode_elo_enabled = ? WHERE mode_name = ?
        ''', (1 if enabled else 0, mode_name))
        
        conn.commit()
        conn.close()
        return True, None
    
    def set_mode_elo_prefix(self, mode_name: str, elo_prefix: str) -> tuple[bool, str]:
        """Set the ELO prefix for a mode (for grouping modes with same prefix)
        
        Args:
            mode_name: The mode to configure
            elo_prefix: The prefix (e.g., 'ctf' for ctf2v2, ctf3v3, ctf5v5)
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if mode exists
        cursor.execute('SELECT mode_name FROM game_modes WHERE mode_name = ?', (mode_name,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Mode '{mode_name}' does not exist!"
        
        # Update elo_prefix
        cursor.execute('''
            UPDATE game_modes SET elo_prefix = ? WHERE mode_name = ?
        ''', (elo_prefix.lower() if elo_prefix else None, mode_name))
        
        conn.commit()
        conn.close()
        return True, None
    
    def get_mode_elo_prefix(self, mode_name: str) -> Optional[str]:
        """Get the ELO prefix for a mode
        
        Args:
            mode_name: The mode name
            
        Returns:
            str or None: The ELO prefix if set, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT elo_prefix FROM game_modes WHERE mode_name = ?', (mode_name,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row and row[0] else None
    
    def get_effective_mode_for_elo(self, mode_name: str) -> str:
        """Get the effective mode name for ELO purposes
        
        If the mode has an elo_prefix, returns the prefix.
        Otherwise returns the mode_name.
        
        This allows modes like ctf2v2, ctf3v3, ctf5v5 to share ELO
        if they all have elo_prefix='ctf'.
        
        Args:
            mode_name: The actual mode name
            
        Returns:
            str: The effective mode name for ELO tracking
        """
        elo_prefix = self.get_mode_elo_prefix(mode_name)
        return elo_prefix if elo_prefix else mode_name
    
    def get_modes_with_per_mode_elo(self) -> list:
        """Get list of modes that have per-mode ELO enabled"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mode_name FROM game_modes WHERE per_mode_elo_enabled = 1
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def set_per_mode_elo_enabled(self, enabled: bool):
        """Enable or disable per-mode ELO (deprecated - kept for compatibility)"""
        self.set_setting('per_mode_elo_enabled', 'true' if enabled else 'false')
    
    def get_player_mode_elo(self, discord_id: str, server_id: str, mode_name: str) -> Dict:
        """Get player's ELO for a specific mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT elo, wins, losses, peak_elo, current_streak, best_win_streak, best_loss_streak
            FROM player_mode_elos
            WHERE discord_id = ? AND server_id = ? AND mode_name = ?
        ''', (discord_id, server_id, mode_name))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'elo': row[0],
                'wins': row[1],
                'losses': row[2],
                'peak_elo': row[3],
                'current_streak': row[4],
                'best_win_streak': row[5],
                'best_loss_streak': row[6]
            }
        else:
            # Return default values if not found
            return {
                'elo': 1000,
                'wins': 0,
                'losses': 0,
                'peak_elo': 1000,
                'current_streak': 0,
                'best_win_streak': 0,
                'best_loss_streak': 0
            }
    
    def init_player_mode_elo(self, discord_id: str, server_id: str, mode_name: str, starting_elo: float = 1000):
        """Initialize a player's ELO for a specific mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO player_mode_elos 
            (discord_id, server_id, mode_name, elo, peak_elo)
            VALUES (?, ?, ?, ?, ?)
        ''', (discord_id, server_id, mode_name, starting_elo, starting_elo))
        
        conn.commit()
        conn.close()
    
    def update_player_mode_elo(self, discord_id: str, server_id: str, mode_name: str, new_elo: float):
        """Update player's ELO for a specific mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current peak ELO
        cursor.execute('''
            SELECT peak_elo FROM player_mode_elos
            WHERE discord_id = ? AND server_id = ? AND mode_name = ?
        ''', (discord_id, server_id, mode_name))
        
        row = cursor.fetchone()
        peak_elo = row[0] if row else new_elo
        
        # Update peak if new ELO is higher
        if new_elo > peak_elo:
            peak_elo = new_elo
        
        # Upsert (insert or update)
        cursor.execute('''
            INSERT OR REPLACE INTO player_mode_elos 
            (discord_id, server_id, mode_name, elo, peak_elo, wins, losses, current_streak, best_win_streak, best_loss_streak, last_updated)
            VALUES (
                ?, ?, ?, ?, ?,
                COALESCE((SELECT wins FROM player_mode_elos WHERE discord_id = ? AND server_id = ? AND mode_name = ?), 0),
                COALESCE((SELECT losses FROM player_mode_elos WHERE discord_id = ? AND server_id = ? AND mode_name = ?), 0),
                COALESCE((SELECT current_streak FROM player_mode_elos WHERE discord_id = ? AND server_id = ? AND mode_name = ?), 0),
                COALESCE((SELECT best_win_streak FROM player_mode_elos WHERE discord_id = ? AND server_id = ? AND mode_name = ?), 0),
                COALESCE((SELECT best_loss_streak FROM player_mode_elos WHERE discord_id = ? AND server_id = ? AND mode_name = ?), 0),
                CURRENT_TIMESTAMP
            )
        ''', (discord_id, server_id, mode_name, new_elo, peak_elo,
              discord_id, server_id, mode_name,
              discord_id, server_id, mode_name,
              discord_id, server_id, mode_name,
              discord_id, server_id, mode_name,
              discord_id, server_id, mode_name))
        
        conn.commit()
        conn.close()
    
    def update_player_mode_stats(self, discord_id: str, server_id: str, mode_name: str, won: bool):
        """Update player's win/loss stats for a specific mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Initialize if doesn't exist
        self.init_player_mode_elo(discord_id, server_id, mode_name)
        
        # Get current stats
        cursor.execute('''
            SELECT wins, losses, current_streak, best_win_streak, best_loss_streak
            FROM player_mode_elos
            WHERE discord_id = ? AND server_id = ? AND mode_name = ?
        ''', (discord_id, server_id, mode_name))
        
        row = cursor.fetchone()
        if not row:
            wins, losses, current_streak, best_win_streak, best_loss_streak = 0, 0, 0, 0, 0
        else:
            wins, losses, current_streak, best_win_streak, best_loss_streak = row
        
        if won:
            wins += 1
            current_streak = current_streak + 1 if current_streak >= 0 else 1
            if current_streak > best_win_streak:
                best_win_streak = current_streak
        else:
            losses += 1
            current_streak = current_streak - 1 if current_streak <= 0 else -1
            if abs(current_streak) > best_loss_streak:
                best_loss_streak = abs(current_streak)
        
        cursor.execute('''
            UPDATE player_mode_elos
            SET wins = ?, losses = ?, current_streak = ?, best_win_streak = ?, best_loss_streak = ?
            WHERE discord_id = ? AND server_id = ? AND mode_name = ?
        ''', (wins, losses, current_streak, best_win_streak, best_loss_streak, discord_id, server_id, mode_name))
        
        conn.commit()
        conn.close()
    
    def set_player_mode_elo(self, discord_id: str, server_id: str, mode_name: str, new_elo: float):
        """Admin function to set a player's ELO for a specific mode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if mode exists
        cursor.execute('SELECT mode_name FROM game_modes WHERE mode_name = ?', (mode_name,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Mode '{mode_name}' does not exist!"
        
        # Initialize or update
        self.update_player_mode_elo(discord_id, server_id, mode_name, new_elo)
        
        conn.close()
        return True, None
    
    def get_all_player_mode_elos(self, discord_id: str, server_id: str) -> Dict:
        """Get all mode-specific ELOs for a player"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mode_name, elo, wins, losses, peak_elo
            FROM player_mode_elos
            WHERE discord_id = ? AND server_id = ?
            ORDER BY elo DESC
        ''', (discord_id, server_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = {}
        for row in rows:
            result[row[0]] = {
                'elo': row[1],
                'wins': row[2],
                'losses': row[3],
                'peak_elo': row[4]
            }
        
        return result

    
    # Map management operations
    def add_map(self, server_id: str, mode_prefix: str, map_name: str) -> tuple:
        """Add a map to a mode's map pool"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO maps (server_id, mode_prefix, map_name)
                VALUES (?, ?, ?)
            ''', (server_id, mode_prefix.lower(), map_name))
            
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            if 'UNIQUE constraint' in str(e):
                return False, f"Map '{map_name}' already exists for {mode_prefix}!"
            return False, str(e)
    
    def remove_map(self, server_id: str, mode_prefix: str, map_name: str) -> tuple:
        """Remove a map from a mode's map pool"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM maps
            WHERE server_id = ? AND mode_prefix = ? AND map_name = ?
        ''', (server_id, mode_prefix.lower(), map_name))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            return True, None
        else:
            return False, f"Map '{map_name}' not found for {mode_prefix}!"
    
    def get_maps_for_mode(self, server_id: str, mode_prefix: str) -> list:
        """Get all maps for a specific mode/prefix"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT map_name FROM maps
            WHERE server_id = ? AND mode_prefix = ?
            ORDER BY map_name
        ''', (server_id, mode_prefix.lower()))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_all_maps_grouped(self, server_id: str) -> dict:
        """Get all maps grouped by mode prefix"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mode_prefix, map_name FROM maps
            WHERE server_id = ?
            ORDER BY mode_prefix, map_name
        ''', (server_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = {}
        for prefix, map_name in rows:
            if prefix not in result:
                result[prefix] = []
            result[prefix].append(map_name)
        
        return result
    
    def add_map_to_cooldown(self, server_id: str, mode_prefix: str, map_name: str):
        """Add a map to the cooldown list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO map_cooldowns (server_id, mode_prefix, map_name)
            VALUES (?, ?, ?)
        ''', (server_id, mode_prefix.lower(), map_name))
        
        conn.commit()
        conn.close()
    
    def get_maps_on_cooldown(self, server_id: str, mode_prefix: str, cooldown_count: int = 3) -> list:
        """Get the most recently used maps (on cooldown)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT map_name FROM map_cooldowns
            WHERE server_id = ? AND mode_prefix = ?
            ORDER BY used_at DESC
            LIMIT ?
        ''', (server_id, mode_prefix.lower(), cooldown_count))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def clear_old_cooldowns(self, server_id: str, mode_prefix: str, keep_count: int = 10):
        """Clear old cooldown entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM map_cooldowns
            WHERE server_id = ? AND mode_prefix = ?
            AND id NOT IN (
                SELECT id FROM map_cooldowns
                WHERE server_id = ? AND mode_prefix = ?
                ORDER BY used_at DESC
                LIMIT ?
            )
        ''', (server_id, mode_prefix.lower(), server_id, mode_prefix.lower(), keep_count))
        
        conn.commit()
        conn.close()
