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
        self.geometry("500x350")
        self.configure(bg="#f5f5f5")
        # Title label
        title_label = tk.Label(self, text="Prayer Times", font=("Arial", 22, "bold"), bg="#f5f5f5", fg="#2c3e50")
        title_label.pack(pady=(20, 10))
        # Frame for prayer times and controls
        content_frame = tk.Frame(self, bg="#f5f5f5")
        content_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Prayer times frame
        self.prayer_frame = PrayerTimesFrame(self, date=datetime.date.today())
        self.prayer_frame.pack(pady=10)

        # Button frame for better layout
        button_frame = tk.Frame(self, bg="#f5f5f5")
        button_frame.pack(pady=10)

        # Refresh button calls update_times on prayer_frame
        self.refresh_button = tk.Button(
            button_frame, text="Refresh", font=("Arial", 12),
            bg="#2980b9", fg="white", relief="raised", bd=2,
            command=self.prayer_frame.update_times
        )
        self.refresh_button.pack(ipadx=10, ipady=3)

    def refresh_times(self):
        # No longer needed, logic moved to button command
        pass

# To run the window (for testing)
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()