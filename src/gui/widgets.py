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
                # Parse prayer time and combine with today's date to get a datetime object
                prayer_time = datetime.datetime.combine(now.date(), datetime.datetime.strptime(time_str, "%H:%M").time())
                
                # Skip if prayer time has already passed
                if prayer_time < now:
                    continue
                 # Time difference between now and prayer time
                delta = prayer_time - now
                # If this is the first future prayer found, or if it occurs sooner than the current next prayer candidate
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    next_prayer = prayer
            except ValueError:
                # Time string could not be parsed, skip this prayer
                continue
            except Exception as e:
                continue

        if next_prayer and min_delta:
            total_seconds = int(min_delta.total_seconds())
            if total_seconds < 3600:
                minutes, seconds = divmod(total_seconds, 60)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {minutes}m {seconds}s"
                )
                self.after(1000, self.update_next_prayer)  # update every second
            else:
                hours, minutes = self.format_time_delta(min_delta)
                self.next_prayer_label.config(
                    text=f"Next prayer: {next_prayer} in {hours}h {minutes}m"
                )
                self.after(60000, self.update_next_prayer)  # update every minute
            return

        # If all prayers today have passed, calculate time until tomorrow's Fajr
        try:
            # Date for tomorrow
            tomorrow = now.date() + datetime.timedelta(days=1)
            # Fetch prayer times for tomorrow at current location
            tomorrow_times = calculate_prayer_times(tomorrow, self.location)
            # Get tomorrow's Fajr time string
            fajr_time_str = tomorrow_times.get("Fajr")
            if fajr_time_str:
                # Parse Fajr time and combine with tomorrow's date
                fajr_time = datetime.datetime.combine(tomorrow, datetime.datetime.strptime(fajr_time_str, "%H:%M").time())
                # Time difference to tomorrow's Fajr
                delta = fajr_time - now
                hours, minutes = self.format_time_delta(delta)
                # Update label to show countdown to tomorrow's Fajr
                self.next_prayer_label.config(
                    text=f"Next prayer: Fajr (tomorrow) in {hours}h {minutes}m"
                )
            else:
                # No Fajr time available for tomorrow
                self.next_prayer_label.config(text="No prayer times available for tomorrow.")
        except Exception as e:
            self.next_prayer_label.config(text="Error fetching tomorrow's prayer times.")

    def check_prayer_alerts(self):
        """
        Periodically check if it's time to alert the user for any upcoming prayer.

        Alerts once when prayer time is within 60 seconds and prevents duplicate alerts.
        """
        now = datetime.datetime.now()
        future = now + datetime.timedelta(minutes=68)
        min_delta = None
        next_prayer_to_alert = None

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
        # Auto close after 2 minute (60000 milliseconds)
        alert.after(60000*2, alert.destroy)
    
        # Content
        frame = tk.Frame(alert, bg="#000000")
        frame.pack(padx=20, pady=20)

        if prayer == "Fajr":
            message = "الصلاة خير من النوم\nPrayer is better than sleep."
            dua = "اللهم اجعلنا من المستيقظين لصلاة الفجر"
        else:
            message = "May Allah accept your prayer."
            dua = "اللهم تقبل صلاتنا وصلاتكم"

        # Display prayer time alert
        tk.Label(frame, text=f"🕌 It's time for {prayer} prayer", font=("Arial", 18, "bold"), fg="#006853", bg="#000000").pack(pady=(0, 15))
        tk.Label(frame, text=message, font=("Arial", 16), fg="#006853", bg="#000000").pack(pady=(0, 10))
        tk.Label(frame, text=dua, font=("Arial", 14, "italic"), fg="#006853", bg="#000000").pack(pady=(0, 15))
        tk.Button(frame, text="OK", font=("Arial", 14, "bold"), command=alert.destroy, bg="#000000", fg="#006853").pack(pady=(10, 0))