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
        self.geometry("500x350")
        self.configure(bg="#f5f5f5")

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
        self.clock_label = tk.Label(self, text="", font=("Arial", 14), bg="#f5f5f5", fg="#34495e")
        self.clock_label.pack(pady=(0, 10))
        self.update_clock()

        self.prayer_frame = PrayerTimesFrame(
            self, date=datetime.date.today(),
            location={"city": self.city_var.get(), "country": self.country_var.get()}
        )
        self.prayer_frame.pack(pady=10)

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