# Prayer Times

A desktop application to view daily Islamic prayer times for selected cities and countries.  
Prayer times are fetched from the Aladhan API and cached in a local SQLite database.

## Features

- **Location-Based Prayer Times**: Select your country and city from the menu bar (File > Set Location).
- **Core Prayers**: View Fajr, Dhuhr, Asr, Maghrib, and Isha times with an analog clock interface.
- **Audio Notifications**: Automated Athan and Dua alerts using `pygame` (unique Fajr Athan supported).
- **Data Persistence**: Caches 30 days of prayer times in a local SQLite database for offline access.
- **Robust Architecture**:
    - Centralized configuration in `src/core/config.py`.
    - Singleton Database Management with automated connection pooling.
    - Custom API Exception hierarchy for reliable network handling.
- **Daily Log Rotation**: Comprehensive debugging logs stored in `logs/` with daily rotation.
- **Consolidated Storage**: All application data (database, settings) stored in a unified `data/` directory.
- **Hiijri Date Support**: Displays the current Hijri date alongside Gregorian prayer times.

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies:
    - `requests`
    - `pygame`

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/prayer_times.git
    cd prayer_times
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
Prayer_Times/
│
├── data/               # Consolidated database and app data
├── logs/               # Daily rotating log files
├── src/
│   ├── assets/         # Audio (.wav) and image assets
│   ├── core/
│   │   ├── api.py           # API communication & error handling
│   │   ├── calculations.py  # Business logic
│   │   ├── config.py        # Centralized constants & settings
│   │   ├── db.py            # Database singleton & operations
│   │   ├── logger_config.py # Logging setup
│   │   └── utils.py         # Helper functions
│   ├── gui/
│   │   ├── dialogs.py       # Custom Tkinter dialogs
│   │   ├── main_window.py   # Main window controller
│   │   ├── menu.py          # Menu bar definition
│   │   ├── widgets.py       # Prayer display & clock widgets
│   │   └── __init__.py
│   └── __init__.py
├── main.py             # Entry point
├── requirements.txt
└── README.md
```

## Credits

- [Aladhan API](https://aladhan.com/prayer-times-api) for prayer times data

## License

MIT License