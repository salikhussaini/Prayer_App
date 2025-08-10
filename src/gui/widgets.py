import tkinter as tk
import datetime
from src.core.calculations import calculate_prayer_times
import threading
from playsound import playsound
import os

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
    """Frame displaying daily prayer times with location selection and next prayer countdown."""
    def __init__(self, master=None, date=None, location=None):
        super().__init__(master,bg="#000000")
        self.date = date
        self.location = location or {"city": "Chicago", "country": "USA"}
        self.labels = {}
        self.alerted_prayers = set()
        self.current_times = {}
        self.next_prayer_label = tk.Label(self, text="", font=("Arial", 24, "bold"), fg="#006853", bg="#000000")

        self.next_prayer_label.grid(row=1, column=0, columnspan=5)
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

    def _init_labels(self):
        """Initialize prayer time labels with individual boxes."""
        prayers = self.PRAYERS
        for idx, prayer in enumerate(prayers):
            frame = tk.Frame(self, bd=3, relief="ridge", bg="#000000", padx=5, pady=5)
            frame.grid(row=2, column=idx, padx=5, pady=20, sticky="nsew")

            lbl_prayer = tk.Label(frame, text=prayer, font=("Arial", 25, "bold"), bg="#000000", fg="#006853")
            lbl_prayer.pack(padx=5, pady=(10, 5))

            lbl_time = tk.Label(frame, text="--:--", font=("Arial", 28), bg="#000000", fg="#006853")
            lbl_time.pack(padx=5, pady=(5, 10))

            self.labels[prayer] = lbl_time
        
    def on_location_change(self):
        """Update location and refresh prayer times."""
        self.update_times()
        self.update_next_prayer()
        self.alerted_prayers.clear()  # reset alerts for new location

    def update_times(self, times=None):
        """Update the displayed prayer times in AM/PM format."""
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

    def update_next_prayer(self):
        """
        Calculate and display the time remaining until the next prayer.

        - Checks all today's prayer times and finds the soonest upcoming prayer.
        - If no more prayers remain today, fetches and displays time until tomorrow's Fajr.
        - Updates the label widget to show the next prayer and countdown.
        """
        # Current date and time
        now = datetime.datetime.now()
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
                    now.date(),
                    datetime.datetime.strptime(time_str, "%H:%M").time()
                )
                # Skip if prayer time has already passed
                if prayer_time < now:
                    continue
                # Calculate time difference to this prayer
                delta = prayer_time - now
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
                    text=f"Next prayer: {next_prayer} in a few seconds..."
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
            return

        # If all prayers today have passed, calculate time until tomorrow's Fajr
        try:
            # Date for tomorrow
            tomorrow = now.date() + datetime.timedelta(days=1)
            # Fetch tomorrow's prayer times
            tomorrow_times = calculate_prayer_times(tomorrow, self.location)
            # Get tomorrow's Fajr time string
            fajr_time_str = tomorrow_times.get("Fajr")

            if fajr_time_str:
                fajr_time = datetime.datetime.combine(
                    tomorrow,
                    datetime.datetime.strptime(fajr_time_str, "%H:%M").time()
                )
                delta = fajr_time - now
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
        """
        Periodically check if it's time to alert the user for any upcoming prayer.

        Alerts once when prayer time is within 60 seconds and prevents duplicate alerts.
        """
        #now = now + datetime.timedelta(minutes=30)
        now = datetime.datetime.now()
        seconds_until = None
        next_prayer_to_alert = None
        min_delta = None 

        for prayer, time_str in self.current_times.items():
            try:
                # Convert string to today's datetime object
                prayer_time = datetime.datetime.combine(now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
                
                # Skip if this prayer has already passed
                if prayer_time < now:
                    continue
                
                # Determine if this is the soonest upcoming prayer
                delta = prayer_time - now
                seconds_until = delta.total_seconds()
                next_prayer_to_alert = prayer
                
                # Update the minimum delta if this is the first future prayer found,
                # or if this prayer occurs sooner than the current next prayer candidate
                if (min_delta is None or delta < min_delta) and seconds_until > 0:
                    #print(f"Checking prayer: {prayer} at {time_str}, delta: {delta}")
                    # Keep track of soonest upcoming prayer
                    min_delta = delta
                    next_prayer_to_alert = prayer
                
                # Alert user if this prayer is within 1 minute
                seconds_until = delta.total_seconds()
                if 0 <= seconds_until < 60 and prayer not in self.alerted_prayers:
                    self.alert_user(prayer)
                    self.alerted_prayers.add(prayer)
            except Exception:
                continue
            except ValueError as e:
                print(f"Error parsing prayer time '{time_str}' for '{prayer}': {e}")
                continue
        # Schedule next check based on how soon the next prayer is
        if seconds_until is not None:
            if seconds_until < 60:
                self.after(10000, self.check_prayer_alerts)   # check every 10 sec
            elif seconds_until < 3600:
                self.after(60000, self.check_prayer_alerts)   # check every 1 min
            else:
                self.after(600000, self.check_prayer_alerts)  # check every 10 min
        else:
            # No prayers left today — check again in 10 minutes
            self.after(600000, self.check_prayer_alerts)
        

    def alert_user(self, prayer):
        """
        Play Athan sound when it's time for a prayer.
        Prevents GUI blocking by running audio in a separate thread.
        """
        def play_athan():
            try:
                athan_path = os.path.join("src/assets", "athan.mp3")
                playsound(athan_path)
            except Exception as e:
                print(f"Error playing Athan for {prayer}: {e}")
        def play_fajr_athan():
            try:
                athan_path = os.path.join("src/assets", "fajr_athan.mp3")
                playsound(athan_path)
            except Exception as e:
                print(f"Error playing Athan for {prayer}: {e}")

        # Only play Athan for valid prayers
        if prayer in self.PRAYERS:
            if prayer == "Fajr":
                threading.Thread(target=play_fajr_athan, daemon=True).start()
            else: 
                threading.Thread(target=play_athan, daemon=True).start()
    
    def schedule_midnight_reset(self):
        """Schedules the prayer alerts reset to run exactly at midnight every day."""
        now = datetime.datetime.now()

        # Calculate next midnight (start of the next day)
        tomorrow = now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)

        # Time until midnight in milliseconds
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)

        # Schedule first reset at midnight
        self.after(ms_until_midnight, self._midnight_reset_wrapper)

    def _midnight_reset_wrapper(self):
        """Wrapper to reset alerts and reschedule next midnight reset."""
        self.reset_alerts()
        self.update_times()        # refresh prayer times for new day
        self.update_next_prayer()  # refresh next prayer countdown

        # Always recalculate next midnight to prevent drift
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)

        self.after(ms_until_midnight, self._midnight_reset_wrapper)
        
    def reset_alerts(self):
        """Clear alerted prayers set at midnight and refresh times."""
        self.alerted_prayers.clear()
        self.date = datetime.date.today()  # update to new day
        self.update_times()                # refresh prayer times
        self.update_next_prayer()           # restart countdown
        self.check_prayer_alerts()          # restart alert checks
        print(f"[{datetime.datetime.now()}] Prayer alerts reset for new day.")