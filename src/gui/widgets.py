import tkinter as tk
import datetime
from src.core.calculations import calculate_prayer_times

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
    """A frame to display all daily prayer times with location selection and next prayer countdown."""
    def __init__(self, master=None, date=None, location=None):
        super().__init__(master,bg="#000000")
        self.date = date
        self.location = location or {"city": "Chicago", "country": "USA"}
        self.labels = {}
        self.alerted_prayers = set()
        
        self.next_prayer_label = tk.Label(self, text="", font=("Arial", 12, "bold"), fg="#006853", bg="#000000")
        self.next_prayer_label.grid(row=1, column=0, columnspan=5, pady=(0, 10))
        
        self._init_labels()
        self.update_times()
        self.update_next_prayer()

        # 🔁 Start prayer time alert checking loop
        self.check_prayer_alerts()

    def _init_labels(self):
        """Initialize prayer time labels with individual boxes."""
        prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        for idx, prayer in enumerate(prayers):
            frame = tk.Frame(self, bd=2, relief="groove", bg="#000000")
            frame.grid(row=2, column=idx, padx=8, pady=10, sticky="nsew")
            lbl_prayer = tk.Label(frame, text=prayer, font=("Arial", 12, "bold"), bg="#000000", fg="#FFFFFF")
            lbl_prayer.pack(padx=8, pady=(8, 2))
            lbl_time = tk.Label(frame, text="--:--", font=("Arial", 14), bg="#000000", fg="#006853")
            lbl_time.pack(padx=8, pady=(2, 8))
            self.labels[prayer] = lbl_time

    def on_location_change(self):
        """Update location and refresh prayer times."""
        self.update_times()
        self.update_next_prayer()

    def update_times(self, times=None):
        """Update the displayed prayer times in AM/PM format."""
        if times is None:
            times = calculate_prayer_times(self.date, self.location)
        self.current_times = times
        for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            time_str = times.get(prayer, "--:--")
            try:
                time_obj = datetime.datetime.strptime(time_str, "%H:%M")
                formatted_time = time_obj.strftime("%I:%M %p")
            except Exception:
                formatted_time = time_str
            self.labels[prayer].config(text=f"{formatted_time}")
        self.update_next_prayer()

    def update_next_prayer(self):
        """Calculate and display time until next prayer."""
        now = datetime.datetime.now()
        next_prayer = None
        min_delta = None
        for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            time_str = self.current_times.get(prayer, "--:--")
            try:
                prayer_time = datetime.datetime.combine(now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
                if prayer_time < now:
                    continue
                delta = prayer_time - now
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    next_prayer = prayer
            except Exception:
                continue
        if next_prayer and min_delta:
            hours, remainder = divmod(min_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.next_prayer_label.config(
                text=f"Next prayer: {next_prayer} in {hours}h {minutes}m"
            )
        else:
            self.next_prayer_label.config(text="No more prayers today.")
    def check_prayer_alerts(self):
        """
        Check if it's time to alert the user for any upcoming prayer.

        This method compares current time against today's prayer times.
        If a prayer is within 60 seconds and hasn't been alerted, an alert is triggered.
        """
        now = datetime.datetime.now()
        future = now + datetime.timedelta(minutes=68)
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
                
                # Update the minimum delta if this is the first future prayer found,
                # or if this prayer occurs sooner than the current next prayer candidate
                if min_delta is None or delta < min_delta:
                    #print(f"Checking prayer: {prayer} at {time_str}, delta: {delta}")
                    # Keep track of soonest upcoming prayer
                    min_delta = delta
                
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

        # Re-check after 1 minute
        self.after(60000, self.check_prayer_alerts)
    def alert_user(self, prayer):
        # Create popup
        alert = tk.Toplevel(self)
        alert.title("Prayer Time")
        alert.configure(bg="#000000")
        alert.geometry("350x150+500+300")
        alert.resizable(False, False)
        # Make it modal
        alert.grab_set()
        alert.focus_force()
    
        # Content
        frame = tk.Frame(alert, bg="#000000")
        frame.pack(padx=20, pady=20)

        # Special text for Fajr
        if prayer == "Fajr":
            message = "الصلاة خير من النوم\nPrayer is better than sleep."
        else:
            message = "May Allah accept your prayer."

        tk.Label(frame, text=f"🕌 It's time for {prayer} prayer", font=("Arial", 14, "bold"), fg="#00FF00", bg="#000000").pack(pady=(0, 10))
        tk.Label(frame, text=message, font=("Arial", 12), fg="#CCCCCC", bg="#000000").pack(pady=(0, 10))
        tk.Button(frame, text="OK", command=alert.destroy).pack()