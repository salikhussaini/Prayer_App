import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

# Get the project root (where main.py is located)
# Navigate from src/core/db.py → src/core/ → src/ → project_root/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Create data directory relative to main.py location
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = str(DATA_DIR / "prayer_times.db")


class DatabaseManager:
    """Singleton database connection manager with connection pooling."""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor with automatic cleanup."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


_db_manager = DatabaseManager()


def init_db():
    """Initialize database and create prayer_times table if it doesn't exist."""
    with _db_manager.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prayer_times (
                date TEXT,
                hijri_date TEXT,
                city TEXT,
                fajr TEXT,
                dhuhr TEXT,
                asr TEXT,
                maghrib TEXT,
                isha TEXT,
                PRIMARY KEY (date, city)
            )
        """)


def store_prayer_times(date, hijri_date, city, times):
    """Store prayer times in database."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO prayer_times 
                (date, hijri_date, city, fajr, dhuhr, asr, maghrib, isha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date.strftime("%Y-%m-%d"),
                hijri_date,
                city,
                times["Fajr"],
                times["Dhuhr"],
                times["Asr"],
                times["Maghrib"],
                times["Isha"]
            ))
    except KeyError as e:
        raise ValueError(f"Missing prayer time key: {e}")
    except Exception as e:
        raise Exception(f"Failed to store prayer times for {city} on {date}: {e}")


def get_prayer_times_from_db(date, city):
    """Retrieve prayer times for a specific date and city."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT fajr, dhuhr, asr, maghrib, isha, hijri_date FROM prayer_times
                WHERE date=? AND city=?
            """, (date.strftime("%Y-%m-%d"), city))
            row = cursor.fetchone()
    except Exception as e:
        raise Exception(f"Failed to retrieve prayer times for {city}: {e}")
    
    if row:
        return {
            "Fajr": row[0],
            "Dhuhr": row[1],
            "Asr": row[2],
            "Maghrib": row[3],
            "Isha": row[4],
            "hijri_date": row[5]
        }
    return None


def get_prayer_times_range_from_db(start_date, end_date, city):
    """Retrieve prayer times for a date range and city."""
    try:
        with _db_manager.get_cursor() as cursor:
            cursor.execute('''
                SELECT date, fajr, dhuhr, asr, maghrib, isha
                FROM prayer_times
                WHERE city = ? AND date BETWEEN ? AND ?
                ORDER BY date ASC
            ''', (city, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            rows = cursor.fetchall()
    except Exception as e:
        raise Exception(f"Failed to retrieve prayer times range for {city}: {e}")

    return {row[0]: {
        "Fajr": row[1], "Dhuhr": row[2], "Asr": row[3],
        "Maghrib": row[4], "Isha": row[5]
    } for row in rows}

