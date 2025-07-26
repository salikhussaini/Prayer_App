# Prayer Times

A desktop application to view daily Islamic prayer times for selected cities and countries.  
Prayer times are fetched from the Aladhan API and cached in a local SQLite database.

## Features

- Select your country and city from dropdown menus
- View Fajr, Dhuhr, Asr, Maghrib, and Isha times
- Refresh button to update prayer times
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
├── core/
│   ├── api.py
│   ├── db.py
│   ├── calculations.py
│   └── utils.py
│
├── gui/
│   ├── main_window.py
│   ├── widgets.py
│   ├── dialogs.py
│   └── __init__.py
│
├── main.py
├── requirements.txt
└── README.md
```

## Credits

- [Aladhan API](https://aladhan.com/prayer-times-api) for prayer times data

## License

MIT License