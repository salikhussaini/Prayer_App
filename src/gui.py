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
    """Unified settings dialog with tabs for Location, API, Display, Audio, and Notifications."""
    
    def __init__(self, parent, title, country_cities, current_country, current_city, 
                 current_method, current_school, current_font_size=None, current_volume=1.0):
        self.country_cities = country_cities
        self.current_country = current_country
        self.current_city = current_city
        self.country_var = tk.StringVar(value=current_country or list(country_cities.keys())[0])
        
        self.current_method = current_method
        self.current_school = current_school
        self.current_font_size = current_font_size or core.DEFAULT_FONT_SIZE
        self.current_volume = current_volume
        self.athan_file = str(core.PROJECT_ROOT / "src/assets/athan.wav")
        self.fajr_athan_file = str(core.PROJECT_ROOT / "src/assets/fajr_athan.wav")
        self.dua_file = str(core.PROJECT_ROOT / "src/assets/dua.wav")
        
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        notebook = ttk.Notebook(master)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 1: Location
        self.create_location_tab(notebook)
        
        # Tab 2: API Settings
        self.create_api_settings_tab(notebook)
        
        # Tab 3: Display
        self.create_display_tab(notebook)
        
        # Tab 4: Audio Settings
        self.create_audio_tab(notebook)
        
        # Tab 5: Notifications
        self.create_notifications_tab(notebook)
        
        return self.method_combo
    
    def create_location_tab(self, notebook):
        """Create Location tab."""
        location_frame = ttk.Frame(notebook)
        notebook.add(location_frame, text="Location")
        
        tk.Label(location_frame, text="Select Country:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        country_combo = ttk.Combobox(location_frame, textvariable=self.country_var, 
                                     values=list(self.country_cities.keys()), state="readonly", width=40)
        country_combo.grid(row=0, column=1, padx=5, pady=(5, 2))
        country_combo.bind('<<ComboboxSelected>>', self.on_country_change)
        
        tk.Label(location_frame, text="Select City:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="nw", padx=5, pady=(5, 2))
        
        scrollbar = ttk.Scrollbar(location_frame)
        scrollbar.grid(row=1, column=2, rowspan=2, sticky="ns")
        
        self.city_listbox = tk.Listbox(location_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 10), height=12, width=40)
        self.city_listbox.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=5, pady=(2, 5))
        scrollbar.config(command=self.city_listbox.yview)
        
        self.populate_cities()
        self.city_listbox.bind('<Double-Button-1>', lambda e: self.ok())
        self.city_listbox.bind('<Return>', lambda e: self.ok())
        
        location_frame.grid_rowconfigure(1, weight=1)
        location_frame.grid_columnconfigure(1, weight=1)
    
    def populate_cities(self):
        """Populate city listbox based on selected country."""
        self.city_listbox.delete(0, tk.END)
        country = self.country_var.get()
        cities = self.country_cities.get(country, [])
        
        for city in cities:
            self.city_listbox.insert(tk.END, city)
        
        if self.current_city and self.current_city in cities:
            index = cities.index(self.current_city)
            self.city_listbox.selection_set(index)
            self.city_listbox.see(index)
        elif cities:
            self.city_listbox.selection_set(0)
            self.city_listbox.see(0)
    
    def on_country_change(self, event=None):
        """Handle country selection change."""
        self.populate_cities()
    
    def create_api_settings_tab(self, notebook):
        """Create API Settings tab."""
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="API Settings")
        
        tk.Label(api_frame, text="Calculation Method:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.method_options = {v: k for k, v in core.API_CALCULATION_METHODS.items()}
        self.method_combo = ttk.Combobox(api_frame, values=list(self.method_options.keys()), width=40, state="readonly")
        current_method_name = core.API_CALCULATION_METHODS.get(self.current_method, "Islamic Society of North America (ISNA)")
        self.method_combo.set(current_method_name)
        self.method_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(api_frame, text="Madhab (School):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.school_options = {v: k for k, v in core.API_SCHOOLS.items()}
        self.school_combo = ttk.Combobox(api_frame, values=list(self.school_options.keys()), width=40, state="readonly")
        current_school_name = core.API_SCHOOLS.get(self.current_school, "Hanafi")
        self.school_combo.set(current_school_name)
        self.school_combo.grid(row=1, column=1, padx=5, pady=5)
    
    def create_display_tab(self, notebook):
        """Create Display tab."""
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="Display")
        
        tk.Label(display_frame, text="Font Size:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.font_size_options = list(core.FONT_SIZES.keys())
        self.font_size_combo = ttk.Combobox(display_frame, values=self.font_size_options, width=40, state="readonly")
        self.font_size_combo.set(self.current_font_size)
        self.font_size_combo.grid(row=0, column=1, padx=5, pady=5)
    
    def create_audio_tab(self, notebook):
        """Create Audio Settings tab."""
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Audio")
        
        tk.Label(audio_frame, text="Alert Volume:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        volume_control_frame = tk.Frame(audio_frame)
        volume_control_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        self.volume_var = tk.DoubleVar(value=self.current_volume)
        self.volume_scale = ttk.Scale(volume_control_frame, from_=0, to=1, orient="horizontal", variable=self.volume_var, command=self.update_volume_label)
        self.volume_scale.pack(side="left", fill="x", expand=True)
        
        self.volume_label = tk.Label(volume_control_frame, text=f"{int(self.current_volume * 100)}%", width=5)
        self.volume_label.pack(side="left", padx=5)
        
        tk.Label(audio_frame, text="Test Audio:").grid(row=1, column=0, sticky="w", padx=5, pady=(20, 5))
        button_frame = tk.Frame(audio_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        tk.Button(button_frame, text="Test Athan", command=self.test_athan_audio, width=15).pack(side="left", padx=3)
        tk.Button(button_frame, text="Test Fajr Athan", command=self.test_fajr_audio, width=15).pack(side="left", padx=3)
        tk.Button(button_frame, text="Test Dua", command=self.test_dua_audio, width=15).pack(side="left", padx=3)
        
        tk.Label(audio_frame, text="Custom Audio Files:").grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=(20, 10))
        tk.Label(audio_frame, text="Athan File:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        tk.Button(audio_frame, text="Browse...", command=self.select_athan_file, width=15).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.athan_path_label = tk.Label(audio_frame, text=self.athan_file, font=("Segoe UI", 8), fg="#666666")
        self.athan_path_label.grid(row=4, column=1, sticky="e", padx=5, pady=5)
        
        tk.Label(audio_frame, text="Dua File:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        tk.Button(audio_frame, text="Browse...", command=self.select_dua_file, width=15).grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.dua_path_label = tk.Label(audio_frame, text=self.dua_file, font=("Segoe UI", 8), fg="#666666")
        self.dua_path_label.grid(row=5, column=1, sticky="e", padx=5, pady=5)
        
        audio_frame.grid_columnconfigure(1, weight=1)
    
    def create_notifications_tab(self, notebook):
        """Create Notifications tab."""
        notif_frame = ttk.Frame(notebook)
        notebook.add(notif_frame, text="Notifications")
        
        tk.Label(notif_frame, text="Alert Threshold (seconds before prayer):").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.alert_threshold_var = tk.IntVar(value=core.ALERT_THRESHOLD_SECONDS)
        threshold_spin = ttk.Spinbox(notif_frame, from_=5, to=300, textvariable=self.alert_threshold_var, width=10)
        threshold_spin.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        tk.Label(notif_frame, text="Prayers to Alert:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(20, 10))
        
        self.prayer_alerts = {}
        prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        for idx, prayer in enumerate(prayers):
            self.prayer_alerts[prayer] = tk.BooleanVar(value=True)
            tk.Checkbutton(notif_frame, text=prayer, variable=self.prayer_alerts[prayer]).grid(row=2+idx, column=0, sticky="w", padx=10, pady=3)
    
    def update_volume_label(self, value):
        """Update volume percentage label."""
        volume_percent = int(float(value) * 100)
        self.volume_label.config(text=f"{volume_percent}%")
    
    def test_athan_audio(self):
        """Test play athan audio."""
        self.play_test_audio(self.athan_file, "Athan")
    
    def test_fajr_audio(self):
        """Test play fajr athan audio."""
        self.play_test_audio(self.fajr_athan_file, "Fajr Athan")
    
    def test_dua_audio(self):
        """Test play dua audio."""
        self.play_test_audio(self.dua_file, "Dua")
    
    def play_test_audio(self, audio_path, audio_name):
        """Play test audio file."""
        if not os.path.exists(audio_path):
            messagebox.showerror("Error", f"{audio_name} file not found: {audio_path}")
            return
        try:
            volume = self.volume_var.get()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            logger.info(f"Testing {audio_name} at volume {int(volume * 100)}%")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play {audio_name}: {str(e)}")
            logger.error(f"Error playing test audio: {e}")
    
    def select_athan_file(self):
        """Select custom athan audio file."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(title="Select Athan Audio File", filetypes=[("Audio Files", "*.wav *.mp3 *.ogg"), ("All Files", "*.*")])
        if file_path:
            self.athan_file = file_path
            self.athan_path_label.config(text=os.path.basename(file_path))
    
    def select_dua_file(self):
        """Select custom dua audio file."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(title="Select Dua Audio File", filetypes=[("Audio Files", "*.wav *.mp3 *.ogg"), ("All Files", "*.*")])
        if file_path:
            self.dua_file = file_path
            self.dua_path_label.config(text=os.path.basename(file_path))
    
    def apply(self):
        """Apply all settings and prepare result."""
        selection = self.city_listbox.curselection()
        country = self.country_var.get()
        cities = self.country_cities.get(country, [])
        city = cities[selection[0]] if selection else cities[0]
        
        method_name = self.method_combo.get()
        school_name = self.school_combo.get()
        font_size = self.font_size_combo.get()
        
        self.result = {
            "country": country,
            "city": city,
            "method": self.method_options[method_name],
            "school": self.school_options[school_name],
            "font_size": font_size,
            "volume": self.volume_var.get(),
            "athan_file": self.athan_file,
            "dua_file": self.dua_file,
            "alert_threshold": self.alert_threshold_var.get(),
            "prayer_alerts": {prayer: var.get() for prayer, var in self.prayer_alerts.items()}
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
                 on_country_change, on_city_change, on_exit, on_settings=None):
        self.master = master
        self.country_var = country_var
        self.city_var = city_var
        self.country_cities = country_cities
        self.on_country_change = on_country_change
        self.on_city_change = on_city_change
        self.on_exit = on_exit
        self.on_settings = on_settings

        self.menubar = tk.Menu(master, bg="#000000", fg="#FFFFFF")
        master.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="About", command=self.show_about)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=on_exit)

        self.menubar.add_command(label="Settings", 
                                command=on_settings if on_settings else self.show_settings)

    def open_location_dialog(self):
        """Open unified settings dialog."""
        # Delegate to the on_settings callback which is handled by MainWindow
        if callable(self.on_settings):
            self.on_settings()

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
        
        # Load settings from cache
        saved_settings = core.load_settings()
        
        self.configure(bg=self.BG_COLOR)
        self.title("Prayer Times")
        
        self.now = PrayerTimesFrame.now

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        self.start_time = datetime.datetime.now()
        self.last_date = datetime.datetime.now().date()
        self.country_var = tk.StringVar(value=saved_settings["country"])
        self.city_var = tk.StringVar(value=saved_settings["city"])

        self.api_method = saved_settings["method"]
        self.api_school = saved_settings["school"]
        self.font_size = saved_settings["font_size"]
        self.audio_volume = saved_settings["volume"]
        self.athan_file = saved_settings["athan_file"]
        self.fajr_athan_file = str(core.PROJECT_ROOT / "src/assets/fajr_athan.wav")
        self.dua_file = saved_settings["dua_file"]
        self.alert_threshold = saved_settings["alert_threshold"]
        self.prayer_alerts = saved_settings["prayer_alerts"]

        self.check_and_ensure_tomorrow_data(self.city_var.get(), self.country_var.get())
        
        self.menu = PrayerMenu(
            self, self.country_var, self.city_var, COUNTRY_CITIES,
            self.on_country_change_menu, self.update_prayer_frame_location,
            self.quit, on_settings=self.open_settings
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
        self.update_prayer_frame_location()

    def open_settings(self):
        """Open unified settings dialog."""
        dialog = SettingsDialog(self, "Settings", COUNTRY_CITIES,
                               self.country_var.get(), self.city_var.get(),
                               self.api_method, self.api_school, 
                               self.font_size, self.audio_volume)
        if dialog.result:
            try:
                # Update location
                self.country_var.set(dialog.result["country"])
                self.city_var.set(dialog.result["city"])
                
                # Update API settings
                self.api_method = dialog.result["method"]
                self.api_school = dialog.result["school"]
                
                # Update display
                self.font_size = dialog.result["font_size"]
                
                # Update audio
                self.audio_volume = dialog.result["volume"]
                self.athan_file = dialog.result["athan_file"]
                self.dua_file = dialog.result["dua_file"]
                
                # Update notifications (currently stored but not used yet)
                self.alert_threshold = dialog.result["alert_threshold"]
                self.prayer_alerts = dialog.result["prayer_alerts"]
                
                core.API_METHOD = self.api_method
                core.API_SCHOOL = self.api_school
                core.ALERT_THRESHOLD_SECONDS = self.alert_threshold
                
                pygame.mixer.music.set_volume(self.audio_volume)
                
                logger.info(f"Settings updated: Country={dialog.result['country']}, "
                          f"City={dialog.result['city']}, Method={self.api_method}, "
                          f"School={self.api_school}, Font Size={self.font_size}, "
                          f"Volume={int(self.audio_volume * 100)}%, "
                          f"Alert Threshold={self.alert_threshold}s")
                
                # Save settings to cache
                core.save_settings({
                    "country": dialog.result["country"],
                    "city": dialog.result["city"],
                    "method": self.api_method,
                    "school": self.api_school,
                    "font_size": self.font_size,
                    "volume": self.audio_volume,
                    "athan_file": self.athan_file,
                    "dua_file": self.dua_file,
                    "alert_threshold": self.alert_threshold,
                    "prayer_alerts": self.prayer_alerts
                })
                
                self.prayer_frame.on_location_change()
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
