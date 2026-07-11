"""
GUI Module for Prayer App
Combines all components, dialogs, menus, and main window.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import datetime
import threading
import pygame
import os
import sys
import math
from datetime import timedelta

from . import core


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


logger = core.get_logger(__name__)


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
        self.current_font_size = current_font_size or core.DEFAULT_FONT_SIZE
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Calculation Method:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.method_options = {v: k for k, v in core.API_CALCULATION_METHODS.items()}
        self.method_combo = ttk.Combobox(master, values=list(self.method_options.keys()), 
                                        width=40, state="readonly")
        
        current_method_name = core.API_CALCULATION_METHODS.get(
            self.current_method, "Islamic Society of North America (ISNA)")
        self.method_combo.set(current_method_name)
        self.method_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(master, text="Madhab (School):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.school_options = {v: k for k, v in core.API_SCHOOLS.items()}
        self.school_combo = ttk.Combobox(master, values=list(self.school_options.keys()), 
                                        width=40, state="readonly")
        
        current_school_name = core.API_SCHOOLS.get(self.current_school, "Hanafi")
        self.school_combo.set(current_school_name)
        self.school_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(master, text="Font Size:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.font_size_options = list(core.FONT_SIZES.keys())
        self.font_size_combo = ttk.Combobox(master, values=self.font_size_options, 
                                           width=40, state="readonly")
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
    """Menu bar for prayer app."""
    
    def __init__(self, master, country_var, city_var, country_cities,
                 on_country_change, on_city_change, on_refresh, on_exit, on_settings=None):
        self.master = master
        self.country_var = country_var
        self.city_var = city_var
        self.country_cities = country_cities
        self.on_country_change = on_country_change
        self.on_city_change = on_city_change
        self.on_refresh = on_refresh
        self.on_exit = on_exit
        self.on_settings = on_settings

        self.menubar = tk.Menu(master, bg="#000000", fg="#FFFFFF")
        master.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)

        location_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Set Location", menu=location_menu)

        country_menu = tk.Menu(location_menu, tearoff=0)
        for country in country_cities.keys():
            country_menu.add_radiobutton(
                label=country, variable=country_var, value=country,
                command=on_country_change
            )
        location_menu.add_cascade(label="Country", menu=country_menu)

        self.city_menu = tk.Menu(location_menu, tearoff=0)
        self.update_city_menu()
        location_menu.add_cascade(label="City", menu=self.city_menu)

        location_menu.add_separator()
        location_menu.add_command(label="Refresh Prayer Times", command=on_refresh)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=on_exit)

        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", 
                                 command=on_settings if on_settings else self.show_settings)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def update_city_menu(self):
        """Update city menu based on selected country."""
        self.city_menu.delete(0, "end")
        country = self.country_var.get()
        if country not in self.country_cities:
            logger.warning(f"Invalid country in menu: {country}")
            return
        for city in self.country_cities[country]:
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
        messagebox.showinfo("Settings", "Settings dialog not implemented yet.")


# =====================================================================
# PRAYER TIMES DISPLAY WIDGET
# =====================================================================

class PrayerTimesFrame(tk.Frame):
    """Frame displaying daily prayer times."""
    
    PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    now = datetime.datetime.now()
    
    def __init__(self, master=None, date=None, location=None):
        super().__init__(master, bg="#000000")
        self.date = date
        
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(1.0)
            logger.info("Pygame mixer initialized successfully")
            self._test_audio_files()
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
        
        if location is None:
            location = core.get_validated_location(COUNTRY_CITIES)
        self.location = location
        self.labels = {}
        self.alerted_prayers = set()
        self.current_times = {}
        
        self.next_prayer_label = tk.Label(
            self, text="", font=("Segoe UI", 32, "bold"),
            bg="#000000", fg="#FFD700", pady=15
        )
        self.next_prayer_label.grid(row=0, column=0, columnspan=5, pady=(10, 20))
        
        for col in range(5):
            self.grid_columnconfigure(col, weight=1)

        self._init_labels()
        self.update_times()
        self.update_next_prayer()
        self.check_prayer_alerts()
        self.schedule_midnight_reset()
        self.pack_propagate(False)
        self.update_clock()

    def _test_audio_files(self):
        """Test that all required audio files exist."""
        audio_files = [
            ("Dua", core.PROJECT_ROOT / "src/assets/dua.wav"),
            ("Fajr Athan", core.PROJECT_ROOT / "src/assets/fajr_athan.wav"),
            ("Regular Athan", core.PROJECT_ROOT / "src/assets/athan.wav")
        ]
        
        all_exist = True
        for name, path in audio_files:
            if os.path.exists(path):
                logger.info(f"✅ {name} audio file found: {path}")
            else:
                logger.error(f"❌ {name} audio file MISSING: {path}")
                all_exist = False
        
        if all_exist:
            logger.info("✅ All audio files verified")
        else:
            logger.warning("⚠️ Some audio files missing")

    def _init_labels(self):
        """Initialize prayer time label widgets."""
        self.prayer_frames = {}
        accent_color = "#00FF99"
        text_color = "#00FF99"
        border_color = "#00FF99"

        for idx, prayer in enumerate(self.PRAYERS):
            frame = tk.Frame(self, bg="#000000", highlightbackground=border_color, 
                           highlightthickness=3, padx=15, pady=15)
            frame.grid(row=2, column=idx, padx=10, pady=20, sticky="nsew")

            lbl_prayer = tk.Label(frame, text=prayer, font=("Segoe UI", 18, "bold"),
                                bg="#000000", fg=text_color)
            lbl_prayer.pack(padx=5, pady=(5, 2))

            lbl_time = tk.Label(frame, text="--:--", font=("Segoe UI", 40),
                              bg="#000000", fg=accent_color)
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
                times = core.calculate_prayer_times(self.date, self.location)
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
        """Convert timedelta to hours and minutes."""
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return hours, minutes

    def highlight_next_prayer(self, next_prayer):
        """Highlight the card for the next prayer."""
        for prayer, frame in self.prayer_frames.items():
            if prayer == next_prayer:
                frame.config(highlightbackground="#FFD700", highlightthickness=5)
            else:
                frame.config(highlightbackground="#00FF99", highlightthickness=3)

    def update_next_prayer(self):
        """Calculate and display the time remaining until next prayer."""
        now = datetime.datetime.now()
        next_prayer = None
        min_delta = None

        for prayer in self.PRAYERS:
            time_str = self.current_times.get(prayer, "--:--")
            try:
                prayer_time = datetime.datetime.combine(
                    now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
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
                    text=f"Next prayer: {next_prayer} in {total_seconds} seconds...")
                self.after(1000, self.update_next_prayer)
            elif total_seconds < 3600:
                minutes, seconds = divmod(total_seconds, 60)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {minutes}m {seconds}s")
                self.after(1000, self.update_next_prayer)
            else:
                hours, minutes = self.format_time_delta(min_delta)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {hours}h {minutes}m")
                self.after(60000, self.update_next_prayer)
            self.highlight_next_prayer(next_prayer)
            return

        try:
            now = datetime.datetime.now()
            tomorrow = now.date() + datetime.timedelta(days=1)
            tomorrow_times = core.calculate_prayer_times(tomorrow, self.location)
            fajr_time_str = tomorrow_times.get("Fajr")

            if fajr_time_str:
                fajr_time = datetime.datetime.combine(
                    tomorrow, datetime.datetime.strptime(fajr_time_str, "%H:%M").time())
                delta = fajr_time - now
                total_seconds = int(delta.total_seconds())

                hours, minutes = self.format_time_delta(delta)
                self.next_prayer_label.config(
                    text=f"Next prayer: Fajr (tomorrow) in {hours}h {minutes}m")

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
        """Monitor prayer times and trigger alerts."""
        now = datetime.datetime.now()
        next_prayer_to_alert = None
        min_delta = None

        for prayer in self.PRAYERS:
            time_str = self.current_times.get(prayer)
            if not time_str:
                continue
                
            try:
                prayer_time = datetime.datetime.combine(
                    now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
                
                if prayer_time < now:
                    continue
                
                delta = prayer_time - now
                seconds_until = delta.total_seconds()
                
                if (min_delta is None or seconds_until < min_delta) and seconds_until > 0:
                    min_delta = seconds_until
                    next_prayer_to_alert = prayer
                
                # Check if prayer is within alert threshold (30 seconds before)
                if 0 <= seconds_until <= core.ALERT_THRESHOLD_SECONDS and prayer not in self.alerted_prayers:
                    logger.info(f"🔔 Prayer alert triggered for {prayer} (in {seconds_until:.1f} seconds)")
                    self.alert_user(prayer)
                    self.alerted_prayers.add(prayer)
            except ValueError as e:
                logger.warning(f"Error parsing prayer time '{time_str}' for '{prayer}': {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error checking alerts for {prayer}: {e}")
                continue
        
        # Adaptive check interval: check more frequently when close to prayer time
        try:
            if min_delta is not None:
                if min_delta < 15:
                    # Less than 15 seconds away: check every second
                    check_interval = 1000
                elif min_delta < 60:
                    # Less than 60 seconds away: check every 2 seconds
                    check_interval = 2000
                elif min_delta < 300:
                    # Less than 5 minutes: check every 5 seconds
                    check_interval = 5000
                elif min_delta < 900:
                    # Less than 15 minutes: check every 10 seconds
                    check_interval = 10000
                elif min_delta < 3600:
                    # Less than 1 hour: check every 30 seconds
                    check_interval = 30000
                else:
                    # More than 1 hour: check every 5 minutes
                    check_interval = 300000
                
                self.after(check_interval, self.check_prayer_alerts)
            else:
                # No prayer times available, check again in 5 minutes
                logger.warning("No upcoming prayer times found, rechecking in 5 minutes")
                self.after(300000, self.check_prayer_alerts)
        except Exception as e:
            logger.error(f"Error scheduling prayer alert checks: {e}")
            self.after(60000, self.check_prayer_alerts)

    def alert_user(self, prayer):
        """Play alert sounds for prayer notification."""
        logger.info(f"🔔 Starting alert sequence for {prayer} prayer")
        
        dua_path = str(core.PROJECT_ROOT / "src/assets/dua.wav")
        if prayer == "Fajr":
            athan_path = str(core.PROJECT_ROOT / "src/assets/fajr_athan.wav")
        else:
            athan_path = str(core.PROJECT_ROOT / "src/assets/athan.wav")
        
        # Schedule audio playback in main thread using after()
        self.play_alert_audio(athan_path, dua_path)

    def play_alert_audio(self, athan_path, dua_path):
        """Play audio files sequentially in the main thread (thread-safe)."""
        if not os.path.exists(athan_path):
            logger.warning(f"❌ Athan file not found: {athan_path}")
            return
        
        try:
            logger.info(f"🔊 Playing athan: {athan_path}")
            pygame.mixer.music.load(athan_path)
            pygame.mixer.music.play()
            
            # Get duration to schedule next audio
            audio_length = pygame.mixer.Sound(athan_path).get_length()
            delay_ms = int(audio_length * 1000) + 500  # Add 500ms buffer
            
            # Schedule dua playback after athan finishes
            self.after(delay_ms, lambda: self.play_dua_audio(dua_path))
            logger.info(f"✅ Athan scheduled (duration: {audio_length:.1f}s)")
            
        except pygame.error as e:
            logger.error(f"❌ Pygame error loading athan: {e}")
        except Exception as e:
            logger.error(f"❌ Error playing athan: {e}")

    def play_dua_audio(self, dua_path):
        """Play dua audio file."""
        if not os.path.exists(dua_path):
            logger.warning(f"❌ Dua file not found: {dua_path}")
            return
        
        try:
            logger.info(f"🔊 Playing dua: {dua_path}")
            pygame.mixer.music.load(dua_path)
            pygame.mixer.music.play()
            logger.info(f"✅ Dua playing")
            
        except pygame.error as e:
            logger.error(f"❌ Pygame error loading dua: {e}")
        except Exception as e:
            logger.error(f"❌ Error playing dua: {e}")

    def schedule_midnight_reset(self):
        """Schedule daily reset of prayer alerts at midnight."""
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)
        self.after(ms_until_midnight, self._midnight_reset_wrapper)

    def _midnight_reset_wrapper(self):
        """Wrapper for midnight reset operations."""
        self.reset_alerts()
        self.update_times()
        self.update_next_prayer()

        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)
        self.after(ms_until_midnight, self._midnight_reset_wrapper)
        
    def reset_alerts(self):
        """Reset all prayer alert tracking."""
        self.alerted_prayers.clear()
        self.date = datetime.date.today()
        self.update_times()
        self.update_next_prayer()
        self.check_prayer_alerts()
        logger.info(f"Prayer alerts reset for new day ({datetime.date.today()})")


# =====================================================================
# MAIN WINDOW
# =====================================================================

class MainWindow(tk.Tk):
    BG_COLOR = "#000000"
    PRIMARY_COLOR = "#006853"
    HOUR_HAND_COLOR = "#00FF99"
    SECOND_HAND_COLOR = "#FF5555"

    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        core.init_db()
        self._validate_assets()
        
        self.configure(bg=self.BG_COLOR)
        self.title("Prayer Times")
        
        self.now = PrayerTimesFrame.now

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        self.start_time = datetime.datetime.now()
        self.last_date = datetime.datetime.now().date()
        self.country_var = tk.StringVar(value="USA")
        self.city_var = tk.StringVar(value="Chicago")

        self.api_method = core.API_METHOD
        self.api_school = core.API_SCHOOL
        self.font_size = core.DEFAULT_FONT_SIZE

        self.check_and_ensure_tomorrow_data(self.city_var.get(), self.country_var.get())
        
        self.menu = PrayerMenu(
            self, self.country_var, self.city_var, COUNTRY_CITIES,
            self.on_country_change_menu, self.update_prayer_frame_location,
            self.refresh_prayer_times, self.quit, on_settings=self.open_settings
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.top_frame.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        self.analog_canvas_size = min(screen_width // 3, screen_height // 3)
        self.analog_canvas_size = max(self.analog_canvas_size, 300)
        self.analog_clock = tk.Canvas(
            self.top_frame, width=self.analog_canvas_size,
            height=self.analog_canvas_size, bg=self.BG_COLOR, highlightthickness=0
        )
        self.analog_clock.grid(row=0, column=0, rowspan=2, padx=(0, 20), sticky="nw")

        self.clock_frame = tk.Frame(self.top_frame, bg=self.BG_COLOR)
        self.clock_frame.grid(row=0, column=1, sticky="n")

        self.configure_styles()
        
        self.clock_label = ttk.Label(self.clock_frame, text="", style="Clock.TLabel")
        self.clock_label.grid(row=0, column=0, sticky="nw", pady=(0, 0))

        self.date_frame = tk.Frame(self.top_frame, bg=self.BG_COLOR)
        self.date_frame.grid(row=1, column=1, sticky="ne")
        
        self.gregorian_label = ttk.Label(self.date_frame, text="", style="Date.TLabel")
        self.gregorian_label.pack(fill="x", anchor="e")

        self.hijri_label = ttk.Label(self.date_frame, text="", style="Date.TLabel")
        self.hijri_label.pack(fill="x", anchor="e")
        
        self.prayer_frame = PrayerTimesFrame(
            self, date=datetime.date.today(),
            location={"city": self.city_var.get(), "country": self.country_var.get()}
        )
        self.prayer_frame.grid(row=1, column=0, pady=10, sticky="nsew")
        
        # Load prayer data asynchronously to avoid UI freeze
        threading.Thread(target=self.check_and_ensure_tomorrow_data,
                        args=(self.city_var.get(), self.country_var.get()),
                        daemon=True).start()
        
        self.update_analog_clock()
        self.update_clock()
        self.schedule_midnight_update()

    def configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 20), background=self.BG_COLOR,
                       foreground=self.PRIMARY_COLOR, anchor="e", justify="right")
        style.configure("Clock.TLabel", font=("Segoe UI", 85, "bold"),
                       foreground="#00FF99", background=self.BG_COLOR, 
                       anchor="e", justify="right")
        style.configure("Date.TLabel", font=("Segoe UI", 40),
                       foreground=self.PRIMARY_COLOR, background=self.BG_COLOR,
                       anchor="e", justify="right")

    def check_and_ensure_tomorrow_data(self, city, country):
        """Ensure prayer times for tomorrow are available."""
        try:
            tomorrow = datetime.datetime.now().date() + timedelta(days=1)
            data = core.get_prayer_times_from_db(tomorrow, city)
            if data is None:
                logger.info(f"No prayer times for {city} on {tomorrow}. Fetching...")
                core.ensure_future_data(city=city, country=country, days=30)
        except core.PrayerAPIException as e:
            logger.error(f"Failed to ensure tomorrow's data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking tomorrow's data: {e}", exc_info=True)
    
    def _validate_assets(self):
        """Validate required audio assets exist."""
        required_assets = [
            core.PROJECT_ROOT / "src/assets/dua.wav",
            core.PROJECT_ROOT / "src/assets/fajr_athan.wav",
            core.PROJECT_ROOT / "src/assets/athan.wav",
        ]
        for asset in required_assets:
            if not os.path.exists(asset):
                logger.warning(f"Missing asset file: {asset}")

    def update_analog_clock(self):
        """Draw analog clock."""
        self.analog_clock.delete("all")
        size = self.analog_canvas_size
        center = size // 2
        radius = size // 2 - 10

        self.analog_clock.create_oval(center - radius, center - radius,
                                     center + radius, center + radius,
                                     outline=self.PRIMARY_COLOR, width=4)

        for i in range(12):
            angle = math.radians(i * 30)
            x_start = center + radius * 0.85 * math.sin(angle)
            y_start = center - radius * 0.85 * math.cos(angle)
            x_end = center + radius * 0.95 * math.sin(angle)
            y_end = center - radius * 0.95 * math.cos(angle)
            self.analog_clock.create_line(x_start, y_start, x_end, y_end,
                                         fill=self.PRIMARY_COLOR, width=2)

        hour = self.now.hour % 12
        minute = self.now.minute
        second = self.now.second

        hour_angle = math.radians((hour + minute / 60) * 30)
        minute_angle = math.radians((minute + second / 60) * 6)
        second_angle = math.radians(second * 6)

        hour_len = radius * 0.5
        hour_x = center + hour_len * math.sin(hour_angle)
        hour_y = center - hour_len * math.cos(hour_angle)
        self.analog_clock.create_line(center, center, hour_x, hour_y,
                                     fill=self.HOUR_HAND_COLOR, width=5)

        minute_len = radius * 0.7
        minute_x = center + minute_len * math.sin(minute_angle)
        minute_y = center - minute_len * math.cos(minute_angle)
        self.analog_clock.create_line(center, center, minute_x, minute_y,
                                     fill=self.HOUR_HAND_COLOR, width=3)

        second_len = radius * 0.9
        second_x = center + second_len * math.sin(second_angle)
        second_y = center - second_len * math.cos(second_angle)
        self.analog_clock.create_line(center, center, second_x, second_y,
                                     fill=self.SECOND_HAND_COLOR, width=1)

        now = datetime.datetime.now()
        digital_time = now.strftime("%I:%M %p")
        self.clock_label.config(text=digital_time)

        self.after(1000, self.update_analog_clock)

    def update_hijri_date_from_db(self):
        """Fetch and display Hijri date."""
        date = datetime.date.today()
        date_str = date.strftime(r"%b-%d-%Y")
        self.gregorian_label.config(text=date_str)
        
        times = core.get_prayer_times_from_db(date, self.city_var.get())
        if times and times.get("hijri_date"):
            hijri_date = times.get("hijri_date")
            hijri_date_parts = hijri_date.split("-")
            month_number = int(hijri_date_parts[1])
            hijri_month_str = core.HIJRI_MONTHS[month_number]['english']
            hijri_date_str = f"{hijri_month_str}-{hijri_date_parts[0]}-{hijri_date_parts[-1]}"
            self.hijri_label.config(text=hijri_date_str)
        else:
            self.hijri_label.config(text="Hijri date not found")

    def on_country_change_menu(self):
        """Handle country selection change."""
        country = self.country_var.get()
        if country not in COUNTRY_CITIES:
            logger.warning(f"Invalid country selected: {country}")
            return
        cities = COUNTRY_CITIES[country]
        self.city_var.set(cities[0])
        self.menu.update_city_menu()
        self.update_prayer_frame_location()

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self, "Settings", self.api_method, 
                               self.api_school, self.font_size)
        if dialog.result:
            try:
                self.api_method = dialog.result["method"]
                self.api_school = dialog.result["school"]
                self.font_size = dialog.result["font_size"]
                
                core.API_METHOD = self.api_method
                core.API_SCHOOL = self.api_school
                
                logger.info(f"Settings updated: Method={self.api_method}, "
                          f"School={self.api_school}, Font Size={self.font_size}")
                self.apply_font_sizes()
                self.refresh_prayer_times()
            except Exception as e:
                logger.error(f"Error applying settings: {e}", exc_info=True)
    
    def apply_font_sizes(self):
        """Apply selected font size."""
        try:
            if self.font_size not in core.FONT_SIZES:
                logger.error(f"Invalid font size: {self.font_size}")
                return
            
            sizes = core.FONT_SIZES[self.font_size]
            
            self.clock_label.config(font=("Segoe UI", sizes["clock"], "bold"))
            self.gregorian_label.config(font=("Segoe UI", sizes["date"]))
            self.hijri_label.config(font=("Segoe UI", sizes["date"]))
            self.prayer_frame.next_prayer_label.config(
                font=("Segoe UI", sizes["next_prayer"], "bold"))
            
            for prayer in self.prayer_frame.PRAYERS:
                # Get prayer name label from frame (first widget is name, second is time)
                frame_children = self.prayer_frame.prayer_frames[prayer].winfo_children()
                if len(frame_children) >= 2:
                    prayer_name_label = frame_children[0]
                    prayer_time_label = self.prayer_frame.labels[prayer]
                    prayer_name_label.config(font=("Segoe UI", sizes["prayer_name"], "bold"))
                    prayer_time_label.config(font=("Segoe UI", sizes["prayer_time"]))
            
            logger.info(f"Font sizes applied: {self.font_size}")
        except Exception as e:
            logger.error(f"Error applying font sizes: {e}", exc_info=True)

    def update_prayer_frame_location(self):
        """Update prayer frame with new location."""
        self.prayer_frame.location = {
            "city": self.city_var.get(),
            "country": self.country_var.get()
        }
        self.prayer_frame.update_times()

    def refresh_prayer_times(self):
        """Force refresh of prayer times."""
        self.prayer_frame.update_times()

    def update_clock(self):
        """Update clock state checks."""
        self.now = PrayerTimesFrame.now

        uptime = datetime.datetime.now() - self.start_time
        if uptime.days >= core.AUTO_RESTART_DAYS:
            logger.info(f"App running for {uptime.days} days. Restarting...")
            self.quit()
            sys.exit(0)

        if self.now.date() != self.last_date:
            self.schedule_midnight_update()
            self.last_date = self.now.date()

        self.after(1000, self.update_clock)

    def schedule_midnight_update(self):
        """Schedule midnight update."""
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((midnight - now).total_seconds() * 1000)
        self.after(ms_until_midnight, self.midnight_update)
        self.update_hijri_date_from_db()

    def midnight_update(self):
        """Update at midnight."""
        try:
            today = datetime.date.today()
            self.prayer_frame.date = today
            self.last_date = today
            
            self.check_and_ensure_tomorrow_data(self.city_var.get(), 
                                               self.country_var.get())
            self.prayer_frame.update_times()
            self.update_hijri_date_from_db()
            self.prayer_frame.reset_alerts()
            
            self.schedule_midnight_update()
        except Exception as e:
            logger.error(f"Midnight update failed: {e}", exc_info=True)
            self.after(300000, self.midnight_update)
