import tkinter as tk
import datetime
from src.gui.widgets import COUNTRY_CITIES, PrayerTimesFrame
from src.gui.menu import PrayerMenu
from src.core.db import init_db

class MainWindow(tk.Tk):
    def __init__(self):
        init_db()  # Ensure DB and table are created before anything else
        super().__init__()
        self.title("Prayer Times")

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set geometry to full screen size (e.g., "1920x1080")
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        # Set background color to black
        self.configure(bg="#000000") 

        self.country_var = tk.StringVar(value="USA") # Default country
        self.city_var = tk.StringVar(value="Chicago") # Default city

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

        # Current clock label
        # Green text color
        self.clock_label = tk.Label(self, text="", font=("Arial", 14), bg="#000000", fg="#006853") 
        self.clock_label.pack(pady=(0, 10))

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
        now = datetime.datetime.now().strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
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
        self.schedule_midnight_update()
