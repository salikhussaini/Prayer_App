import tkinter as tk
import datetime
from src.gui.widgets import COUNTRY_CITIES, PrayerTimesFrame  
from src.gui.dialogs import LocationDialog, show_error

class MainWindow(tk.Tk):
    """Main application window for displaying prayer times."""
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.geometry("500x350")
        self.configure(bg="#f5f5f5")

        # Menu bar
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # Location submenu
        location_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Location", menu=location_menu)

        # Country dropdown in menu
        self.country_var = tk.StringVar(value="UK")
        country_menu = tk.Menu(location_menu, tearoff=0)
        for country in COUNTRY_CITIES.keys():
            country_menu.add_radiobutton(
                label=country, variable=self.country_var, value=country,
                command=self.on_country_change_menu
            )
        location_menu.add_cascade(label="Country", menu=country_menu)

        # City dropdown in menu
        self.city_var = tk.StringVar(value=COUNTRY_CITIES[self.country_var.get()][0])
        self.city_menu = tk.Menu(location_menu, tearoff=0)
        self.update_city_menu()
        location_menu.add_cascade(label="City", menu=self.city_menu)
        
        # Add Exit to File menu
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=self.quit
        )
        
        # Title label
        title_label = tk.Label(self, text="Prayer Times", font=("Arial", 22, "bold"), bg="#f5f5f5", fg="#2c3e50")
        title_label.pack(pady=(20, 10))

        # Current clock label
        self.clock_label = tk.Label(self, text="", font=("Arial", 14), bg="#f5f5f5", fg="#34495e")
        self.clock_label.pack(pady=(0, 10))
        self.update_clock()

        # Frame for prayer times and controls
        content_frame = tk.Frame(self, bg="#f5f5f5")
        content_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Prayer times frame
        self.prayer_frame = PrayerTimesFrame(
            self, date=datetime.date.today(),
            location={"city": self.city_var.get(), "country": self.country_var.get()}
        )
        self.prayer_frame.pack(pady=10)

        # Add Refresh to Location menu update_times on prayer_frame
        location_menu.add_separator()
        location_menu.add_command(
            label="Refresh Prayer Times",
            command=self.prayer_frame.update_times
        )
    def update_clock(self):
        """Update the clock label every second."""
        now = datetime.datetime.now().strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def on_country_change_menu(self):
        """Update city menu when country changes from menu bar."""
        cities = COUNTRY_CITIES[self.country_var.get()]
        self.city_var.set(cities[0])
        self.update_city_menu()
        self.update_prayer_frame_location()

    def update_city_menu(self):
        """Refresh city menu items in the menu bar."""
        self.city_menu.delete(0, "end")
        for city in COUNTRY_CITIES[self.country_var.get()]:
            self.city_menu.add_radiobutton(
                label=city, variable=self.city_var, value=city,
                command=self.update_prayer_frame_location
            )

    def update_prayer_frame_location(self):
        """Update location in prayer frame and refresh times."""
        self.prayer_frame.location = {
            "city": self.city_var.get(),
            "country": self.country_var.get()
        }
        self.prayer_frame.update_times()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()