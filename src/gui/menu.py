import tkinter as tk
from tkinter import messagebox

class PrayerMenu:
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
        self.city_menu.delete(0, "end")
        for city in self.country_cities[self.country_var.get()]:
            self.city_menu.add_radiobutton(
                label=city, variable=self.city_var, value=city,
                command=self.on_city_change
            )

    def show_about(self):
        messagebox.showinfo(
            "About Prayer Times",
            "Prayer Times App\nVersion 1.0\n\nCreated by Your Name\nPowered by Aladhan API"
        )

    def show_settings(self):
        messagebox.showinfo(
            "Settings",
            "Settings dialog not implemented yet."
        )
