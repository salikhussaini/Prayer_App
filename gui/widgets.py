import tkinter as tk
from core.calculations import calculate_prayer_times  # Import calculation function

# Define valid cities for each country
COUNTRY_CITIES = {
    "UK": sorted(["London"]),
    "USA": sorted([
        "New York", "Los Angeles", "Chicago"
        , "Houston", "Phoenix", "Philadelphia"
        , "San Antonio", "San Diego", "Dallas", "San Jose"
        , "Austin", "Jacksonville", "Fort Worth", "Columbus"
        , "Charlotte", "San Francisco", "Indianapolis", "Seattle"
        , "Denver", "Washington D.C.", "Boston", "El Paso"
        , "Nashville", "Detroit", "Oklahoma City", "Portland"
        , "Las Vegas", "Baltimore", "Milwaukee", "Albuquerque"
        , "Tucson", "Fresno", "Sacramento", "Long Beach"
        , "Kansas City", "Mesa", "Virginia Beach", "Atlanta"
        , "Colorado Springs", "Omaha", "Raleigh", "Miami"
        , "Cleveland", "Tulsa", "Oakland", "Minneapolis"
        , "Wichita", "New Orleans", "Arlington", "Bakersfield"
        , "Tampa", "Honolulu", "Anaheim", "Aurora"
        , "Santa Ana", "St. Louis", "Riverside", "Corpus Christi"
        , "Lexington", "Pittsburgh", "Anchorage", "Stockton"
        , "Cincinnati", "Saint Paul", "Greensboro", "Lincoln"
        , "Plano", "Henderson", "Buffalo", "Fort Wayne"
        , "Jersey City", "Chula Vista", "Orlando", "St. Petersburg"
        , "Norfolk", "Chandler", "Laredo", "Madison"

    ]),
    "Pakistan": ["Karachi"],
    "Egypt": ["Cairo"],
    "Indonesia": ["Jakarta"]
}

class PrayerTimesFrame(tk.Frame):
    """A frame to display all daily prayer times with location selection."""
    def __init__(self, master=None, date=None, location=None):
        super().__init__(master)
        self.date = date
        self.location = location or {"city": "London", "country": "UK"}
        self.labels = {}

        # Country dropdown
        self.country_var = tk.StringVar(value=self.location["country"])
        tk.Label(self, text="Country:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.country_menu = tk.OptionMenu(self, self.country_var, *COUNTRY_CITIES.keys(), command=self.on_country_change)
        self.country_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # City dropdown (will be updated based on country)
        self.city_var = tk.StringVar(value=self.location["city"])
        tk.Label(self, text="City:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.city_menu = tk.OptionMenu(self, self.city_var, *COUNTRY_CITIES[self.country_var.get()])
        self.city_menu.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Update button
        self.update_btn = tk.Button(self, text="Update Location", command=self.on_location_change)
        self.update_btn.grid(row=0, column=4, padx=10, pady=5)

        # Prayer time labels start from row 1
        self._init_labels()

    def _init_labels(self):
        """Initialize prayer time labels with placeholders."""
        for idx, prayer in enumerate(["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]):
            lbl = tk.Label(self, text=f"{prayer}: --:--")
            lbl.grid(row=idx + 1, column=0, columnspan=5, sticky="w", padx=10, pady=2)
            self.labels[prayer] = lbl

    def on_country_change(self, selected_country):
        """Update city dropdown when country changes."""
        cities = COUNTRY_CITIES[selected_country]
        self.city_var.set(cities[0])
        menu = self.city_menu["menu"]
        menu.delete(0, "end")
        for city in cities:
            menu.add_command(label=city, command=lambda value=city: self.city_var.set(value))

    def on_location_change(self):
        """Update location and refresh prayer times."""
        self.location = {
            "city": self.city_var.get(),
            "country": self.country_var.get()
        }
        self.update_times()

    def update_times(self, times=None):
        """Update the displayed prayer times."""
        if times is None:
            times = calculate_prayer_times(self.date, self.location)
        for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            time = times.get(prayer, "--:--")
            self.labels[prayer].config(text=f"{prayer}: {time}")