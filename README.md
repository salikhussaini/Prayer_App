# Prayer Times

A desktop application to view daily Islamic prayer times for selected cities and countries.  
Prayer times are fetched from the Aladhan API and cached in a local SQLite database.

## Features

- Select your country and city from the menu bar (File > Set Location)
- View Fajr, Dhuhr, Asr, Maghrib, and Isha times in individual boxes
- Prayer times displayed in AM/PM format
- Current time (AM/PM) shown at the top of the window
- Manual refresh from the menu bar (File > Set Location > Refresh Prayer Times)
- About and Settings options in the menu bar
- Caches results locally for faster access
- Error handling for API and database issues

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies:
    - `requests`

## Installation

1. Clone this repository:
    ```
    git clone https://github.com/yourusername/prayer_times.git
    cd prayer_times
    ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```
python main.py
```

## Project Structure

```
Prayer_Times/
│
├── src/
│   ├── core/
│   │   ├── api.py
│   │   ├── calculations.py
│   │   ├── db.py
│   │   └── utils.py
│   ├── gui/
│   │   ├── dialogs.py
│   │   ├── main_window.py
│   │   ├── menu.py
│   │   ├── widgets.py
│   │   └── __init__.py
│   └── __init__.py
├── main.py
├── requirements.txt
└── README.md
```

## Credits

- [Aladhan API](https://aladhan.com/prayer-times-api) for prayer times data

## License

MIT License