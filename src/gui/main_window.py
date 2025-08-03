import tkinter as tk
import math
import datetime
from src.gui.widgets import COUNTRY_CITIES, PrayerTimesFrame
from src.gui.menu import PrayerMenu
from src.core.db import init_db

from datetime import timedelta
from src.core.db import get_prayer_times_from_db
from src.core.api import ensure_future_data

def check_and_ensure_tomorrow_data(city, country):
    tomorrow = datetime.datetime.now().date() + timedelta(days=1)
    # Check if prayer times for tomorrow exist in DB
    data = get_prayer_times_from_db(tomorrow, city)
    if data is None:
        print(f"No prayer times found for {city}, {country} on {tomorrow}. Fetching data...")
        ensure_future_data(city=city, country=country, days=30)  # Prefetch next 7 days
class MainWindow(tk.Tk):
    BG_COLOR = "#000000"
    PRIMARY_COLOR = "#006853"
    HOUR_HAND_COLOR = "#00FF99"
    SECOND_HAND_COLOR = "#FF5555"
    def __init__(self):
        super().__init__()
        init_db()  # Ensure DB and table are created before anything else
        # Set background color to black
        self.configure(bg=self.BG_COLOR) 
        self.title("Prayer Times")

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set geometry to full screen size (e.g., "1920x1080")
        self.geometry(f"{screen_width}x{screen_height}+0+0")


        self.country_var = tk.StringVar(value="USA") # Default country
        self.city_var = tk.StringVar(value="Chicago") # Default city

        check_and_ensure_tomorrow_data(self.city_var.get(), self.country_var.get())
        # Menu bar using PrayerMenu
        self.menu = PrayerMenu(
            self,
            self.country_var,
            self.city_var,
            COUNTRY_CITIES,
            self.on_country_change_menu,
            self.update_prayer_frame_location,
            self.refresh_prayer_times,
            self.quit
        )

        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)  # prayer frame expands vertically
        self.grid_columnconfigure(0, weight=1)

        # --- Create # --- Create a top frame to hold both analog and digital clocks ---
        self.top_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.top_frame.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        # --- Analog clock (top left) ---
        self.analog_canvas_size = min(screen_width // 3, screen_height // 3)
        self.analog_canvas_size = max(self.analog_canvas_size, 300)
        self.analog_clock = tk.Canvas(
            self.top_frame,
            width=self.analog_canvas_size,
            height=self.analog_canvas_size,
            bg=self.BG_COLOR,
            highlightthickness=0
        )
        self.analog_clock.grid(row=0, column=0, rowspan=3, padx=(0, 20), sticky="nw")
        self.update_analog_clock()

        # --- Clock frame to stack digital clock and both dates vertically ---
        self.clock_frame = tk.Frame(self.top_frame, bg=self.BG_COLOR)
        self.clock_frame.grid(row=0, column=1, sticky="n")

        # --- Digital clock (top right of analog) ---
        self.clock_label = tk.Label(
            self.clock_frame,
            text="",
            font=("Arial", 85, "bold"),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR
        )
        self.clock_label.grid(row=0, column=0, pady=(0, 10))
        self.update_clock()

        # --- Gregorian date (below digital clock) ---
        self.gregorian_label = tk.Label(
            self.clock_frame,
            text="",
            font=("Arial", 30),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR
        )
        self.gregorian_label.grid(row=1, column=0)

        # --- Hijri date (below Gregorian date) ---
        self.hijri_label = tk.Label(
            self.clock_frame,
            text="",
            font=("Arial", 30),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR
        )
        self.hijri_label.grid(row=2, column=0)
        # Prayer frame
        self.prayer_frame = PrayerTimesFrame(
            self,
            date=datetime.date.today(),
            location={"city": self.city_var.get(), "country": self.country_var.get()}
        )
        self.prayer_frame.grid(row=1, column=0, pady=10, sticky="nsew")
        self.schedule_midnight_update()
    def update_analog_clock(self):
        """Draw analog clock hands and update every second."""
        self.analog_clock.delete("all")
        size = self.analog_canvas_size
        center = size // 2
        radius = size // 2 - 10

        # Draw clock face
        self.analog_clock.create_oval(center - radius, center - radius, center + radius, center + radius, outline=self.PRIMARY_COLOR, width=4)

        # Hour marks
        for i in range(12):
            angle = math.radians(i * 30)
            x_start = center + radius * 0.85 * math.sin(angle)
            y_start = center - radius * 0.85 * math.cos(angle)
            x_end = center + radius * 0.95 * math.sin(angle)
            y_end = center - radius * 0.95 * math.cos(angle)
            self.analog_clock.create_line(x_start, y_start, x_end, y_end, fill=self.PRIMARY_COLOR, width=2)

        now = datetime.datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second

        # Angles
        hour_angle = math.radians((hour + minute / 60) * 30)
        minute_angle = math.radians((minute + second / 60) * 6)
        second_angle = math.radians(second * 6)

        # Draw hour hand
        hour_len = radius * 0.5
        hour_x = center + hour_len * math.sin(hour_angle)
        hour_y = center - hour_len * math.cos(hour_angle)
        self.analog_clock.create_line(center, center, hour_x, hour_y, fill=self.HOUR_HAND_COLOR, width=5)

        # Draw minute hand
        minute_len = radius * 0.7
        minute_x = center + minute_len * math.sin(minute_angle)
        minute_y = center - minute_len * math.cos(minute_angle)
        self.analog_clock.create_line(center, center, minute_x, minute_y, fill=self.HOUR_HAND_COLOR, width=3)

        # Draw second hand
        second_len = radius * 0.9
        second_x = center + second_len * math.sin(second_angle)
        second_y = center - second_len * math.cos(second_angle)
        self.analog_clock.create_line(center, center, second_x, second_y, fill=self.SECOND_HAND_COLOR, width=1)

        # Schedule next update
        self.after(1000, self.update_analog_clock)
    def update_hijri_date_from_db(self):
        hijri_months = {
            1: {"english": "Muharram", "arabic": "مُحَرَّم"},
            2: {"english": "Safar", "arabic": "صَفَر"},
            3: {"english": "Rabi' al-Awwal", "arabic": "رَبِيع ٱلْأَوَّل"},
            4: {"english": "Rabi' al-Thani", "arabic": "رَبِيع ٱلثَّانِي"},
            5: {"english": "Jumada al-Awwal", "arabic": "جُمَادَىٰ ٱلْأُولَىٰ"},
            6: {"english": "Jumada al-Thani", "arabic": "جُمَادَىٰ ٱلثَّانِيَة"},
            7: {"english": "Rajab", "arabic": "رَجَب"},
            8: {"english": "Sha'ban", "arabic": "شَعْبَان"},
            9: {"english": "Ramadan", "arabic": "رَمَضَان"},
            10: {"english": "Shawwal", "arabic": "شَوَّال"},
            11: {"english": "Dhu al-Qi'dah", "arabic": "ذُو ٱلْقِعْدَة"},
            12: {"english": "Dhu al-Hijjah", "arabic": "ذُو ٱلْحِجَّة"}
        }
        """Fetch Hijri date from DB and update label."""
        date = datetime.date.today()
        # Format date for display year-month-day
        date_str = date.strftime(r"%b-%d-%Y")
        self.gregorian_label.config(text=date_str)
        # Fetch Hijri date from DB
        times = get_prayer_times_from_db(date, self.city_var.get())
        if times:
            hijri_date = times.get("hijri_date")
            hijri_date_parts = hijri_date.split("-")
            month_number = int(hijri_date_parts[1])  # safer
            hijri_month_str = hijri_months[month_number]['english']
            hijri_date_str = f"{hijri_month_str}-{hijri_date_parts[0]}-{hijri_date_parts[-1]}"
        
        
            if hijri_date_str:
                self.hijri_label.config(text=hijri_date_str)
            else:
                self.hijri_label.config(text="Hijri date not available")
        else:
            self.hijri_label.config(text="Hijri date not found")
    def on_country_change_menu(self):
        cities = COUNTRY_CITIES[self.country_var.get()]
        self.city_var.set(cities[0])
        self.menu.update_city_menu()
        self.update_prayer_frame_location()
    def update_prayer_frame_location(self):
        self.prayer_frame.location = {
            "city": self.city_var.get(),
            "country": self.country_var.get()
        }
        self.prayer_frame.update_times()
    def refresh_prayer_times(self):
        self.prayer_frame.update_times()
    def update_clock(self):
        """Update the clock label every second with AM/PM format."""
        now = datetime.datetime.now().strftime("%I:%M %p")  # 12-hour format with AM/PM
        self.clock_label.config(text=f"{now}")
        self.after(1000, self.update_clock)
    def schedule_midnight_update(self):
        """Schedule prayer times update at midnight every day."""
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((midnight - now).total_seconds() * 1000)
        self.after(ms_until_midnight, self.midnight_update)
        self.update_hijri_date_from_db()  # Update Hijri date at startup 
    def midnight_update(self):
        """Update prayer times for the new day and reschedule for next midnight."""
        self.prayer_frame.date = datetime.date.today()
        self.prayer_frame.update_times()
        # Schedule daily prayer time update at midnight
        self.schedule_midnight_update()