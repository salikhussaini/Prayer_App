import tkinter as tk
from tkinter import simpledialog, messagebox

class LocationDialog(simpledialog.Dialog):
    """Dialog to ask the user for their location."""
    def body(self, master):
        tk.Label(master, text="Enter your city:").grid(row=0)
        self.city_entry = tk.Entry(master)
        self.city_entry.grid(row=0, column=1)
        return self.city_entry

    def apply(self):
        self.result = self.city_entry.get()

def show_error(message):
    """Show an error message dialog."""
    messagebox.showerror("Error", message)