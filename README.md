# Prayer Times

A desktop application to view daily Islamic prayer times for selected cities and countries.  
Prayer times are fetched from the Aladhan API and cached in a local SQLite database.

## Features

- **Location-Based Prayer Times**: Select your country and city from File > Set Location menu.
- **Core Prayers**: Display Fajr, Dhuhr, Asr, Maghrib, and Isha times with countdown timer and next prayer highlighting.
- **Analog & Digital Clocks**: Analog clock with hour/minute/second hands and digital time display.
- **Audio Notifications**: Automated Athan and Dua alerts (with unique Fajr Athan) using pygame.
- **Hijri Calendar**: Display current Hijri date alongside Gregorian calendar.
- **Data Caching**: 30-day prayer time cache in local SQLite database for offline access.
- **Configurable**: API calculation method, Madhab school, and font size settings.
- **Logging**: Comprehensive daily rotating logs for debugging.
- **Lightweight**: Condensed into 2 main modules (core.py, gui.py) for maintainability.
- **Cross-Platform**: Works on Windows, Linux, and Raspberry Pi.

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
3. Run the application:
    ```bash
    python main.py
    ```

## Usage

Run the application:
```bash
python main.py
```

### Menu Navigation
- **File > Set Location**: Change country and city
- **File > Refresh Prayer Times**: Force reload prayer times
- **Settings > Preferences**: Adjust calculation method, school (Madhab), and font size
- **Help > About**: View app information

## Project Structure

```
Prayer_App/
│
├── main.py             # Entry point - initializes app
├── src/
│   ├── core.py         # Backend: config, DB, API, logging (750 lines)
│   ├── gui.py          # Frontend: dialogs, menus, widgets, main window (750 lines)
│   ├── assets/         # Audio (.wav) and image assets
│   ├── scripts/        # Update scripts
│   ├── data/           # SQLite database & app data (created at runtime)
│   └── logs/           # Daily rotating log files (created at runtime)
├── requirements.txt
└── README.md
```

## Core Modules

**src/core.py** - Unified Backend (Configuration, Database, API, Logging)
- Configuration constants (API URLs, prayer names, UI settings, colors, Hijri months)
- Logging setup with daily rotating file handler
- Database singleton manager with connection pooling
- Prayer times API functions (fetch, cache, validate)
- Geolocation from IP address
- Update checking for Linux/Raspberry Pi

**src/gui.py** - Unified Frontend (GUI Components, Dialogs, Main Window)
- Country/city definitions and location dialogs
- Settings dialog for API method, Madhab school, font size
- Menu bar with location, settings, and help menus
- Prayer times display frame with audio alerts
- Main window with analog clock, digital clock, Gregorian/Hijri dates
- Event handlers and UI logic


## Credits

- [Aladhan API](https://aladhan.com/prayer-times-api) for prayer times data

## License

MIT License