import sqlite3

DB_PATH = "prayer_times.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prayer_times (
            date TEXT,
            city TEXT,
            fajr TEXT,
            dhuhr TEXT,
            asr TEXT,
            maghrib TEXT,
            isha TEXT,
            PRIMARY KEY (date, city)
        )
    """)
    conn.commit()
    conn.close()

def store_prayer_times(date, city, times):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO prayer_times (date, city, fajr, dhuhr, asr, maghrib, isha)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date.strftime("%Y-%m-%d"),
        city,
        times["Fajr"],
        times["Dhuhr"],
        times["Asr"],
        times["Maghrib"],
        times["Isha"]
    ))
    conn.commit()
    conn.close()

def get_prayer_times_from_db(date, city):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fajr, dhuhr, asr, maghrib, isha FROM prayer_times
        WHERE date=? AND city=?
    """, (date.strftime("%Y-%m-%d"), city))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "Fajr": row[0],
            "Dhuhr": row[1],
            "Asr": row[2],
            "Maghrib": row[3],
            "Isha": row[4]
        }
    return None