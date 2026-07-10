"""
GUI Components for Prayer App.
Consolidates menu, dialogs, and prayer display widgets.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import datetime
import threading
import pygame
import os
from datetime import timedelta

from src.core.helpers import calculate_prayer_times, get_logger
from src.core.api import get_validated_location
from src.core.config import PROJECT_ROOT, API_CALCULATION_METHODS, API_SCHOOLS, FONT_SIZES, DEFAULT_FONT_SIZE


logger = get_logger(__name__)


# =====================================================================
# COUNTRY & CITY DEFINITIONS
# =====================================================================

COUNTRY_CITIES = {
    "UK": sorted(["London"]),
    "USA": sorted([
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle",
        "Denver", "Washington D.C.", "Boston", "El Paso", "Nashville", "Detroit",
        "Oklahoma City", "Portland", "Las Vegas", "Baltimore", "Milwaukee", "Albuquerque",
        "Tucson", "Fresno", "Sacramento", "Long Beach", "Kansas City", "Mesa",
        "Virginia Beach", "Atlanta", "Colorado Springs", "Omaha", "Raleigh", "Miami",
        "Cleveland", "Tulsa", "Oakland", "Minneapolis", "Wichita", "New Orleans",
        "Arlington", "Bakersfield", "Tampa", "Honolulu", "Anaheim", "Aurora",
        "Santa Ana", "St. Louis", "Riverside", "Corpus Christi", "Lexington",
        "Pittsburgh", "Anchorage", "Stockton", "Cincinnati", "Saint Paul", "Greensboro",
        "Lincoln", "Plano", "Henderson", "Buffalo", "Fort Wayne", "Jersey City",
        "Chula Vista", "Orlando", "St. Petersburg", "Norfolk", "Chandler", "Laredo",
        "Madison", "Mcallen", "Durham", "Lubbock", "Winston-Salem"
    ]),
    "Pakistan": ["Karachi"],
    "Egypt": ["Cairo"],
    "Indonesia": ["Jakarta"]
}


# =====================================================================
# DIALOGS
# =====================================================================

class LocationDialog(simpledialog.Dialog):
    """Dialog to ask the user for their location."""
    def body(self, master):
        tk.Label(master, text="Enter your city:").grid(row=0)
        self.city_entry = tk.Entry(master)
        self.city_entry.grid(row=0, column=1)
        return self.city_entry

    def apply(self):
        self.result = self.city_entry.get()


class SettingsDialog(simpledialog.Dialog):
    """Dialog to configure API calculation methods, school, and font size."""
    
    def __init__(self, parent, title, current_method, current_school, current_font_size=None):
        self.current_method = current_method
        self.current_school = current_school
        self.current_font_size = current_font_size or DEFAULT_FONT_SIZE
        self.result = None  # Initialize result to prevent AttributeError if cancelled
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Calculation Method:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Reverse mapping for display
        self.method_options = {v: k for k, v in API_CALCULATION_METHODS.items()}
        self.method_combo = ttk.Combobox(master, values=list(self.method_options.keys()), width=40, state="readonly")
        
        # Set current value
        current_method_name = API_CALCULATION_METHODS.get(self.current_method, "Islamic Society of North America (ISNA)")
        self.method_combo.set(current_method_name)
        self.method_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(master, text="Madhab (School):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.school_options = {v: k for k, v in API_SCHOOLS.items()}
        self.school_combo = ttk.Combobox(master, values=list(self.school_options.keys()), width=40, state="readonly")
        
        current_school_name = API_SCHOOLS.get(self.current_school, "Hanafi")
        self.school_combo.set(current_school_name)
        self.school_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(master, text="Font Size:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.font_size_options = list(FONT_SIZES.keys())
        self.font_size_combo = ttk.Combobox(master, values=self.font_size_options, width=40, state="readonly")
        self.font_size_combo.set(self.current_font_size)
        self.font_size_combo.grid(row=2, column=1, padx=5, pady=5)
        
        return self.method_combo
    
    def apply(self):
        method_name = self.method_combo.get()
        school_name = self.school_combo.get()
        font_size = self.font_size_combo.get()
        
        self.result = {
            "method": self.method_options[method_name],
            "school": self.school_options[school_name],
            "font_size": font_size
        }


def show_error(message):
    """Show an error message dialog."""
    messagebox.showerror("Error", message)


# =====================================================================
# MENU BAR
# =====================================================================

class PrayerMenu:
    """Menu bar for prayer app with location, refresh, and settings."""
    
    def __init__(
        self, master, country_var, city_var, country_cities,
        on_country_change, on_city_change, on_refresh, on_exit,
        on_settings=None
    ):
        self.master = master
        self.country_var = country_var
        self.city_var = city_var
        self.country_cities = country_cities
        self.on_country_change = on_country_change
        self.on_city_change = on_city_change
        self.on_refresh = on_refresh
        self.on_exit = on_exit
        self.on_settings = on_settings

        self.menubar = tk.Menu(master,bg="#000000", fg="#FFFFFF")
        master.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # Location submenu
        location_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Set Location", menu=location_menu)

        # Country dropdown
        country_menu = tk.Menu(location_menu, tearoff=0)
        for country in country_cities.keys():
            country_menu.add_radiobutton(
                label=country, variable=country_var, value=country,
                command=on_country_change
            )
        location_menu.add_cascade(label="Country", menu=country_menu)

        # City dropdown
        self.city_menu = tk.Menu(location_menu, tearoff=0)
        self.update_city_menu()
        location_menu.add_cascade(label="City", menu=self.city_menu)

        # Refresh and Exit
        location_menu.add_separator()
        location_menu.add_command(label="Refresh Prayer Times", command=on_refresh)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=on_exit)

        # Settings menu
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=on_settings if on_settings else self.show_settings)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def update_city_menu(self):
        """Update city menu based on selected country."""
        self.city_menu.delete(0, "end")
        for city in self.country_cities[self.country_var.get()]:
            self.city_menu.add_radiobutton(
                label=city, variable=self.city_var, value=city,
                command=self.on_city_change
            )

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Prayer Times",
            "Prayer Times App\nVersion 1.0\n\nCreated by Your Name\nPowered by Aladhan API"
        )

    def show_settings(self):
        """Show settings placeholder dialog."""
        messagebox.showinfo(
            "Settings",
            "Settings dialog not implemented yet."
        )


# =====================================================================
# PRAYER TIMES DISPLAY WIDGET
# =====================================================================

class PrayerTimesFrame(tk.Frame):
    """Frame displaying daily prayer times with location selection and next prayer countdown."""
    
    PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    now = datetime.datetime.now()
    
    def __init__(self, master=None, date=None, location=None):
        # Black background to allow parent's background image to show
        super().__init__(master, bg="#000000")
        self.date = date
        pygame.mixer.init()  # Initialize mixer once
        
        # Try IP geolocation if location not provided
        if location is None:
            location = get_validated_location(COUNTRY_CITIES)
        self.location = location
        self.labels = {}
        self.alerted_prayers = set()
        self.current_times = {}
        
        self.next_prayer_label = tk.Label(
            self, 
            text="", 
            font=("Segoe UI", 32, "bold"),
            bg="#000000",
            fg="#FFD700",
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        self.next_prayer_label.grid(row=0, column=0, columnspan=5, pady=(10, 20))
        
        for col in range(5):
            self.grid_columnconfigure(col, weight=1)

        self._init_labels()
        self.update_times()
        self.update_next_prayer()

        # Start prayer alert checking loop in background
        self.check_prayer_alerts()
        # Reset prayer times at midnight
        self.schedule_midnight_reset() 

        self.pack_propagate(False)
        # Remove padding and background to maximize transparency
        # self.configure(padx=10, pady=10)

        self.update_clock()

    def _init_labels(self):
        """Initialize and layout all prayer time label widgets."""
        self.prayer_frames = {}
        accent_color = "#00FF99"  # Brighter green for visibility
        text_color = "#00FF99"
        border_color = "#00FF99"  # Bright green border for visibility

        for idx, prayer in enumerate(self.PRAYERS):
            # Transparent frame with bright border - black bg to show parent image
            frame = tk.Frame(
                self,
                bg="#000000",
                highlightbackground=border_color, 
                highlightthickness=3, 
                padx=15, pady=15
            )
            frame.grid(row=2, column=idx, padx=10, pady=20, sticky="nsew")

            # Transparent labels - black background to show parent image
            lbl_prayer = tk.Label(
                frame, text=prayer, 
                font=("Segoe UI", 18, "bold"),
                bg="#000000",
                fg=text_color
            )
            lbl_prayer.pack(padx=5, pady=(5, 2))

            lbl_time = tk.Label(
                frame, text="--:--", 
                font=("Segoe UI", 40),
                bg="#000000",
                fg=accent_color
            )
            lbl_time.pack(padx=5, pady=(2, 8))

            self.labels[prayer] = lbl_time
            self.prayer_frames[prayer] = frame
        
    def update_clock(self):
        """Update the clock label every second."""
        PrayerTimesFrame.now = datetime.datetime.now()
        self.now = PrayerTimesFrame.now
        self.after(1000, self.update_clock)

    def on_location_change(self):
        """Handle location change events."""
        self.update_times()
        self.update_next_prayer()
        self.alerted_prayers.clear()

    def update_times(self, times=None):
        """Update displayed prayer times."""
        if times is None:
            try:
                times = calculate_prayer_times(self.date, self.location)
            except Exception as e:
                logger.error(f"Error calculating prayer times: {e}")
                times = {}
        
        self.current_times = times
        for prayer in self.PRAYERS:
            time_str = times.get(prayer, "--:--")
            try:
                time_obj = datetime.datetime.strptime(time_str, "%H:%M")
                formatted_time = time_obj.strftime("%I:%M %p")
            except Exception:
                formatted_time = time_str
            self.labels[prayer].config(text=formatted_time)
        self.update_next_prayer()

    def format_time_delta(self, delta):
        """Convert a timedelta object into hours and minutes."""
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return hours, minutes

    def highlight_next_prayer(self, next_prayer):
        """Highlight the card for the next prayer."""
        for prayer, frame in self.prayer_frames.items():
            if prayer == next_prayer:
                frame.config(highlightbackground="#FFD700", highlightthickness=5)  # Gold border, thicker
            else:
                frame.config(highlightbackground="#00FF99", highlightthickness=3)  # Bright green

    def update_next_prayer(self):
        """Calculate and display the time remaining until the next prayer."""
        now = datetime.datetime.now()
        next_prayer = None
        min_delta = None

        for prayer in self.PRAYERS:
            time_str = self.current_times.get(prayer, "--:--")
            try:
                prayer_time = datetime.datetime.combine(
                    now.date(),
                    datetime.datetime.strptime(time_str, "%H:%M").time()
                )
                if prayer_time < now:
                    continue
                delta = prayer_time - now
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    next_prayer = prayer
            except Exception:
                continue

        if next_prayer and min_delta:
            total_seconds = int(min_delta.total_seconds())
            if total_seconds < 60:
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {total_seconds} seconds..."
                )
                self.after(1000, self.update_next_prayer)
            elif total_seconds < 3600:
                minutes, seconds = divmod(total_seconds, 60)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {minutes}m {seconds}s"
                )
                self.after(1000, self.update_next_prayer)
            else:
                hours, minutes = self.format_time_delta(min_delta)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {hours}h {minutes}m"
                )
                self.after(60000, self.update_next_prayer)
            self.highlight_next_prayer(next_prayer)
            return        

        # All prayers today have passed, calculate time until tomorrow's Fajr
        try:
            now = datetime.datetime.now()
            tomorrow = now.date() + datetime.timedelta(days=1)
            tomorrow_times = calculate_prayer_times(tomorrow, self.location)
            fajr_time_str = tomorrow_times.get("Fajr")

            if fajr_time_str:
                fajr_time = datetime.datetime.combine(
                    tomorrow,
                    datetime.datetime.strptime(fajr_time_str, "%H:%M").time()
                )
                delta = fajr_time - now
                total_seconds = int(delta.total_seconds())

                hours, minutes = self.format_time_delta(delta)
                self.next_prayer_label.config(
                    text=f"Next prayer: Fajr (tomorrow) in {hours}h {minutes}m"
                )

                if total_seconds < 3600:
                    self.after(1000, self.update_next_prayer)
                else:
                    self.after(60000, self.update_next_prayer)
            else:
                self.next_prayer_label.config(text="No prayer times available for tomorrow.")
                self.after(60000, self.update_next_prayer)
        except Exception:
            self.next_prayer_label.config(text="Error fetching tomorrow's prayer times.")
            self.after(60000, self.update_next_prayer)

    def check_prayer_alerts(self):
        """Monitor prayer times and trigger alerts when appropriate."""
        now = datetime.datetime.now()
        next_prayer_to_alert = None
        min_delta = None 

        for prayer in self.PRAYERS:
            time_str = self.current_times.get(prayer)
            if not time_str:
                continue
                
            try:
                prayer_time = datetime.datetime.combine(now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
                
                if prayer_time < now:
                    logger.debug(f"{prayer} has already passed")
                    continue
                
                delta = prayer_time - now
                seconds_until = delta.total_seconds()
                
                if (min_delta is None or seconds_until < min_delta) and seconds_until > 0:
                    min_delta = seconds_until
                    next_prayer_to_alert = prayer
                
                if 0 <= seconds_until < 30 and prayer not in self.alerted_prayers:
                    self.alert_user(prayer)
                    self.alerted_prayers.add(prayer)
            except ValueError as e:
                logger.warning(f"Error parsing prayer time '{time_str}' for '{prayer}': {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error checking alerts for {prayer}: {e}")
                continue
        
        logger.debug(f"Next prayer to alert: {next_prayer_to_alert} in {min_delta} seconds")
        
        # Schedule next check based on how soon the next prayer is
        CHECK_INTERVALS = [
            (15, 5000),
            (60, 10000),
            (75, 20000),
            (120, 30000),
            (240, 60000),
            (600, 120000),
            (900, 300000),
            (1200, 600000),
            (1800, 900000),
            (3600, 1200000),
            (7200, 2400000)
        ]

        try:
            if min_delta is not None:
                for limit, interval in CHECK_INTERVALS:
                    if min_delta < limit:
                        self.after(interval, self.check_prayer_alerts)
                        break
                else:
                    self.after(6000000, self.check_prayer_alerts)
            else:
                self.after(6000000, self.check_prayer_alerts)
        except Exception as e:
            logger.error(f"Error scheduling prayer alert checks: {e}")
            self.after(12000000, self.check_prayer_alerts)

    def alert_user(self, prayer):
        """Play alert sounds for prayer time notification."""
        def play_with_wait(path):
            """Load and play audio file, wait for completion."""
            if not os.path.exists(path):
                logger.warning(f"Audio file not found: {path}")
                return
            
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                logger.debug(f"Successfully played: {path}")
            except pygame.error as e:
                logger.error(f"Pygame error playing {path}: {e}")
            except Exception as e:
                logger.error(f"Error playing audio {path}: {e}")

        def play_sequence(first_path, second_path):
            """Play two audio files in sequence."""
            play_with_wait(first_path)
            play_with_wait(second_path)

        if prayer in self.PRAYERS:
            dua_path = PROJECT_ROOT / "src/assets/dua.wav"
            if prayer == "Fajr":
                athan_path = PROJECT_ROOT / "src/assets/fajr_athan.wav"
            else:
                athan_path = PROJECT_ROOT / "src/assets/athan.wav"

            logger.info(f"Alert triggered for {prayer}")
            threading.Thread(
                target=play_sequence,
                args=(athan_path, dua_path),
                daemon=True
            ).start()

    def schedule_midnight_reset(self):
        """Schedule daily reset of prayer alerts at midnight."""
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)
        self.after(ms_until_midnight, self._midnight_reset_wrapper)

    def _midnight_reset_wrapper(self):
        """Wrapper function for midnight reset operations."""
        self.reset_alerts()
        self.update_times()
        self.update_next_prayer()

        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)

        self.after(ms_until_midnight, self._midnight_reset_wrapper)
        
    def reset_alerts(self):
        """Reset all prayer alert tracking at day boundary."""
        self.alerted_prayers.clear()
        self.date = datetime.date.today()
        self.update_times()
        self.update_next_prayer()
        self.check_prayer_alerts()
        logger.info(f"Prayer alerts reset for new day ({datetime.date.today()})")
