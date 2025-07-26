import tkinter as tk
import datetime
# In main_window.py
from gui.widgets import PrayerTimesFrame  
from gui.dialogs import LocationDialog, show_error

class MainWindow(tk.Tk):
    """Main application window for displaying prayer times."""
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.title("Prayer Times")
        self.geometry("400x300")

        self.prayer_frame = PrayerTimesFrame(self, date=datetime.date.today())
        self.prayer_frame.pack()

        # Refresh button calls update_times on prayer_frame
        self.refresh_button = tk.Button(self, text="Refresh", command=self.prayer_frame.update_times)
        self.refresh_button.pack(pady=20)

    def refresh_times(self):
        
        # No longer needed, logic moved to button command
        pass

# To run the window (for testing)
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()