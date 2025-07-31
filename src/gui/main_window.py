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
    else:
        print(f"Prayer times for {city}, {country} on {tomorrow} are already available.")


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

        # Accept canvas size as a parameter or use screen scaling
        self.analog_canvas_size = int(screen_height * 0.25)
        self.analog_canvas_size = 250
        self.analog_clock = tk.Canvas(self, width=self.analog_canvas_size, height=self.analog_canvas_size, bg=self.BG_COLOR, highlightthickness=0)
        self.analog_clock.pack(pady=(20, 10))
        self.update_analog_clock()  # Start analog clock

        # Current clock label
        # Green text color
        self.clock_label = tk.Label(self, text="", font=("Arial", 36, "bold"), bg=self.BG_COLOR, fg=self.PRIMARY_COLOR)
        self.clock_label.pack(pady=(10, 40))


        # Start the clock update loop
        self.update_clock()

        # Prayer times frame    
        self.prayer_frame = PrayerTimesFrame(
            self, date=datetime.date.today(),
            location={"city": self.city_var.get(), "country": self.country_var.get()}
        )
        self.prayer_frame.pack(pady=10)
        # Schedule daily prayer time update at midnight
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
        self.analog_clock.create_line(center, center, hour_x, hour_y, fill="#00FF99", width=5)

        # Draw minute hand
        minute_len = radius * 0.7
        minute_x = center + minute_len * math.sin(minute_angle)
        minute_y = center - minute_len * math.cos(minute_angle)
        self.analog_clock.create_line(center, center, minute_x, minute_y, fill="#00FF99", width=3)

        # Draw second hand
        second_len = radius * 0.9
        second_x = center + second_len * math.sin(second_angle)
        second_y = center - second_len * math.cos(second_angle)
        self.analog_clock.create_line(center, center, second_x, second_y, fill="#FF5555", width=1)

        # Schedule next update
        self.after(1000, self.update_analog_clock)


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
    def midnight_update(self):
        """Update prayer times for the new day and reschedule for next midnight."""
        self.prayer_frame.date = datetime.date.today()
        self.prayer_frame.update_times()
        # Schedule daily prayer time update at midnight
        self.schedule_midnight_update()