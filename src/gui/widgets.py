import tkinter as tk
import time
import datetime
from src.core.calculations import calculate_prayer_times
import threading
import pygame
import os
from datetime import timedelta

# Define valid cities for each country
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

class PrayerTimesFrame(tk.Frame):
    PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    # For testing future time
    # now = datetime.datetime.now() + datetime.timedelta(minutes=1)
    now = datetime.datetime.now() 
    
    """Frame displaying daily prayer times with location selection and next prayer countdown."""
    def __init__(self, master=None, date=None, location=None):
        super().__init__(master,bg="#000000")
        self.date = date
        pygame.mixer.init()  # Initialize mixer once on class instantiation
        self.now = PrayerTimesFrame.now
        self.location = location or {"city": "Chicago", "country": "USA"}
        self.labels = {}
        self.alerted_prayers = set()
        self.current_times = {}
        self.next_prayer_label = tk.Label(
            self, 
            text="", 
            font=("Segoe UI", 32, "bold"), 
            fg="#540000", bg="#000000", 
            pady=15
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
        self.configure(padx=10, pady=10)

        self.update_clock()

    def _init_labels(self):
        """Initialize and layout all prayer time label widgets.

        Creates:
        - A frame for each prayer (Fajr, Dhuhr, Asr, Maghrib, Isha)
        - Prayer name label
        - Time display label
        - Stores references in self.labels dictionary
        """
        self.prayer_frames = {}
        accent_color = "#006853" 
        text_color = "#006853"
        card_bg = "#000000"

        for idx, prayer in enumerate(self.PRAYERS):
            frame = tk.Frame(
                self, 
                bg=card_bg, 
                highlightbackground=accent_color, 
                highlightthickness=2, 
                padx=10, pady=10
            )
            frame.grid(row=2, column=idx, padx=10, pady=20, sticky="nsew")

            lbl_prayer = tk.Label(
                frame, text=prayer, 
                font=("Segoe UI", 18, "bold"), 
                bg=card_bg, fg=text_color
            )
            lbl_prayer.pack(padx=5, pady=(5, 2))

            lbl_time = tk.Label(
                frame, text="--:--", 
                font=("Segoe UI", 33), 
                bg=card_bg, fg=accent_color
            )
            lbl_time.pack(padx=5, pady=(2, 5))

            self.labels[prayer] = lbl_time
            self.prayer_frames[prayer] = frame
        
    def update_clock(self):
        """Update the clock label every second with AM/PM format."""
        # For testing future time
        # PrayerTimesFrame.now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        PrayerTimesFrame.now = datetime.datetime.now()
        self.now = PrayerTimesFrame.now
        self.after(1000, self.update_clock)

    def on_location_change(self):
        """Handle location change events.
        
        Performs:
        1. Clears any existing prayer alerts
        2. Updates displayed prayer times
        3. Resets next prayer countdown
        """
        self.update_times()
        self.update_next_prayer()
        self.alerted_prayers.clear()  # reset alerts for new location

    def update_times(self, times=None):
        """Update displayed prayer times with optional override values.
        
        Args:
            times (dict, optional): Pre-calculated prayer times in {'Prayer': 'HH:MM'} format.
                                    If None, times will be calculated automatically.
                                    
        Behavior:
        - Converts 24-hour times to 12-hour AM/PM format
        - Handles calculation errors gracefully
        - Updates all prayer time labels
        - Triggers next prayer countdown update
        
        Note: Passing times parameter bypasses calculation - use for testing or
            when you have pre-computed times.
        """
        if times is None:
            try:
                times = calculate_prayer_times(self.date, self.location)
            except Exception as e:
                print(f"Error calculating prayer times: {e}")
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
        """
        Convert a timedelta object into hours and minutes.

        Args:
            delta (datetime.timedelta): The time difference to format.

        Returns:
            tuple: (hours, minutes) representing the delta.
        """
        # Get total seconds from timedelta
        total_seconds = int(delta.total_seconds())
        # Calculate full hours and leftover seconds
        hours, remainder = divmod(total_seconds, 3600)
        # Calculate full minutes from remainder seconds
        minutes, _ = divmod(remainder, 60)
        return hours, minutes

    def highlight_next_prayer(self, next_prayer):
        """Highlight the card for the next prayer."""
        for prayer, frame in self.prayer_frames.items():
            if prayer == next_prayer:
                frame.config(highlightbackground="#FFD700", highlightthickness=4)  # gold border
            else:
                frame.config(highlightbackground="#00FF99", highlightthickness=2)


    def update_next_prayer(self):
        """
        Calculate and display the time remaining until the next prayer.

        - Checks all today's prayer times and finds the soonest upcoming prayer.
        - If no more prayers remain today, fetches and displays time until tomorrow's Fajr.
        - Updates the label widget to show the next prayer and countdown.
        """
        # Current date and time
        #now = datetime.datetime.now()
        # Will hold the name of the next prayer
        next_prayer = None
        # Smallest time difference to next prayer
        min_delta = None

        # Loop through today's prayers to find the next upcoming one
        for prayer in self.PRAYERS:
            # Get prayer time string and convert to datetime object
            time_str = self.current_times.get(prayer, "--:--")
            try:
                prayer_time = datetime.datetime.combine(
                    PrayerTimesFrame.now.date(),
                    datetime.datetime.strptime(time_str, "%H:%M").time()
                )
                # Skip if prayer time has already passed
                if prayer_time < PrayerTimesFrame.now:
                    continue
                # Calculate time difference to this prayer
                delta = prayer_time - PrayerTimesFrame.now
                # If this is the first future prayer found, or if it occurs sooner than the current next prayer candidate
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    next_prayer = prayer
            except Exception:
                continue  # Skip invalid times silently

        if next_prayer and min_delta:
            # If next prayer is today, display its countdown
            total_seconds = int(min_delta.total_seconds())
            if total_seconds < 60:
                # Just 1 second left, refresh quickly
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {total_seconds} seconds..."
                )
                self.after(1000, self.update_next_prayer)
            elif total_seconds < 3600:
                # Less than an hour: show minutes and seconds
                minutes, seconds = divmod(total_seconds, 60)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {minutes}m {seconds}s"
                )
                self.after(1000, self.update_next_prayer)
            else:
                # More than an hour: show hours and minutes
                hours, minutes = self.format_time_delta(min_delta)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {hours}h {minutes}m"
                )
                self.after(60000, self.update_next_prayer)
            self.highlight_next_prayer(next_prayer)
            return        

        # If all prayers today have passed, calculate time until tomorrow's Fajr
        try:
            # Date for tomorrow
            tomorrow = PrayerTimesFrame.now.date() + datetime.timedelta(days=1)
            # Fetch tomorrow's prayer times
            tomorrow_times = calculate_prayer_times(tomorrow, self.location)
            # Get tomorrow's Fajr time string
            fajr_time_str = tomorrow_times.get("Fajr")

            if fajr_time_str:
                fajr_time = datetime.datetime.combine(
                    tomorrow,
                    datetime.datetime.strptime(fajr_time_str, "%H:%M").time()
                )
                delta = fajr_time - PrayerTimesFrame.now
                total_seconds = int(delta.total_seconds())

                # Show hours and minutes for Fajr countdown
                hours, minutes = self.format_time_delta(delta)
                # Update label to show countdown to tomorrow's Fajr
                self.next_prayer_label.config(
                    text=f"Next prayer: Fajr (tomorrow) in {hours}h {minutes}m"
                )

                # Use 1-minute refresh until under 1 hour, then every second
                if total_seconds < 3600:
                    self.after(1000, self.update_next_prayer)
                else:
                    self.after(60000, self.update_next_prayer)
            else:
                # No Fajr time available for tomorrow
                self.next_prayer_label.config(text="No prayer times available for tomorrow.")
                self.after(60000, self.update_next_prayer)
        except Exception:
            self.next_prayer_label.config(text="Error fetching tomorrow's prayer times.")
            self.after(60000, self.update_next_prayer)

    def check_prayer_alerts(self):
        """Monitor prayer times and trigger alerts when appropriate.
        
        Operation:
        1. Checks all upcoming prayer times
        2. Finds the next occurring prayer
        3. Triggers audio alert when prayer time is within 60 seconds
        4. Prevents duplicate alerts using alerted_prayers set
        
        Scheduling:
        - Checks more frequently as prayer time approaches:
        - Every 10 seconds when <60 seconds away
        - Every minute when <1 hour away
        - Every 10 minutes otherwise
        
        Note: Runs continuously via tkinter's after() scheduler.
        """
        #now = now + datetime.timedelta(minutes=30)
        #now = datetime.datetime.now()
        seconds_until = None
        next_prayer_to_alert = None
        min_delta = None 

        for prayer, time_str in self.current_times.items():
            try:
                # Convert string to today's datetime object
                prayer_time = datetime.datetime.combine(PrayerTimesFrame.now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
                
                # Skip if this prayer has already passed
                if prayer_time < PrayerTimesFrame.now:
                    print(prayer, "has already passed.", prayer_time, "<", PrayerTimesFrame.now)
                    continue
                

                # Determine if this is the soonest upcoming prayer
                delta = prayer_time - PrayerTimesFrame.now
                seconds_until = delta.total_seconds()
                
                # Update the minimum delta if this is the first future prayer found,
                # or if this prayer occurs sooner than the current next prayer candidate
                if (min_delta is None or delta < min_delta) and seconds_until > 0:
                    #print(f"Checking prayer: {prayer} at {time_str}, delta: {delta}")
                    # Keep track of soonest upcoming prayer
                    min_delta = delta.total_seconds()
                    next_prayer_to_alert = prayer
                
                # Alert user if this prayer is within 1 minute
                seconds_until = delta.total_seconds()
                if 0 <= seconds_until < 30 and prayer not in self.alerted_prayers:
                    self.alert_user(prayer)
                    self.alerted_prayers.add(prayer)
            except Exception:
                continue
            except ValueError as e:
                print(f"Error parsing prayer time '{time_str}' for '{prayer}': {e}")
                continue
        print(f"Next prayer to alert: {next_prayer_to_alert} in {min_delta} seconds.")
        # Schedule next check based on how soon the next prayer is
        CHECK_INTERVALS = [
            (15, 5000),
            (60, 10000), # Check every 10 seconds if within 1 minute
            (75, 20000), # Check every 20 seconds if within 1.25 minutes
            (120, 30000), # Check every 30 seconds if within 2 minutes
            (240, 60000), # Check every 1 minute if within 4 minutes
            (600, 120000), # Check every 2 minutes if within 10 minutes
            (900, 300000), # Check every 5 minutes if within 15 minutes
            (1200, 600000), # Check every 10 minutes if within 20 minutes
            (1800, 900000), # Check every 15 minutes if within 30 minutes
            (3600, 1200000), # Check every 20 minutes if within 1 hour
            (7200, 2400000) # Check every 40 minutes if within 2 hours

        ]

        try:
            for limit, interval in CHECK_INTERVALS:
                if min_delta < limit:
                    self.after(interval, self.check_prayer_alerts)
                    break
            else:
                self.after(6000000, self.check_prayer_alerts) # Default to 1 hour checks if no prayer is imminent
        except Exception as e:
            print(f"Error scheduling prayer alert checks: {e}")
            self.after(12000000, self.check_prayer_alerts) # Fallback to 2 hour checks on error
    def alert_user(self, prayer):
        def play_with_wait(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():  # Wait until finished
                    pygame.time.Clock().tick(10)
            except Exception as e:
                print(f"Error playing {path} for {prayer}: {e}")

        def play_sequence(first_path, second_path):
            play_with_wait(first_path)
            play_with_wait(second_path)

        if prayer in self.PRAYERS:
            dua_path = os.path.join("src", "assets", "dua.wav")
            if prayer == "Fajr":
                athan_path = os.path.join("src", "assets", "fajr_athan.wav")
            else:
                athan_path = os.path.join("src", "assets", "athan.wav")

            threading.Thread(
                target=play_sequence,
                args=(athan_path, dua_path),
                daemon=True
            ).start()
            
    def schedule_midnight_reset(self):
        """Schedule daily reset of prayer alerts at midnight.
    
        Calculates exact milliseconds until next midnight and schedules
        _midnight_reset_wrapper to execute at that time.
        """
        #now = datetime.datetime.now()

        # Calculate next midnight (start of the next day)
        tomorrow = PrayerTimesFrame.now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)

        # Time until midnight in milliseconds
        ms_until_midnight = int((next_midnight - PrayerTimesFrame.now).total_seconds() * 1000)

        # Schedule first reset at midnight
        self.after(ms_until_midnight, self._midnight_reset_wrapper)

    def _midnight_reset_wrapper(self):
        """Wrapper function for midnight reset operations.
        
        Handles:
        1. Executing reset_alerts()
        2. Recalculating next midnight
        3. Rescheduling itself for following day
        
        Ensures daily prayer alert resets remain precisely timed.
        """
        self.reset_alerts()
        self.update_times()        # refresh prayer times for new day
        self.update_next_prayer()  # refresh next prayer countdown

        # Always recalculate next midnight to prevent drift
        #now = datetime.datetime.now()
        tomorrow = PrayerTimesFrame.now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((next_midnight - PrayerTimesFrame.now).total_seconds() * 1000)

        self.after(ms_until_midnight, self._midnight_reset_wrapper)
        
    def reset_alerts(self):
        """Reset all prayer alert tracking at day boundary.
        
        Performs:
        1. Clears alerted_prayers set
        2. Updates to current date
        3. Refreshes prayer times display
        4. Restarts countdown and alert checks
        """
        self.alerted_prayers.clear()
        self.date = datetime.date.today()  # update to new day
        self.update_times()                # refresh prayer times
        self.update_next_prayer()           # restart countdown
        self.check_prayer_alerts()          # restart alert checks
        print(f"[{datetime.datetime.now()}] Prayer alerts reset for new day.")